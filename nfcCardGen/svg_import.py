"""
SVG import and processing utilities for the NFC Card & Keychain Generator add-on.

This module provides functions and operators for importing SVG files,
converting them to clean manifold meshes, and connecting them to the
geometry node setup.
"""

import time

import bmesh
import bpy
from bpy.types import Operator
from mathutils import Matrix


def _process_mesh_geometry(design_obj):
    """
    Processes a flat plane mesh to make it a 0.6mm thick manifold mesh.
        - In edit mode, select all and extrude by 0.6mm
        - Select all, dissolve limited, and merge by distance
        - Select all interior faces and delete them
        - Second dissolve limited and recalculate normals outside

    Args:
        design_obj: The mesh object to process
    """

    mesh = design_obj.data
    mesh.calc_loop_triangles()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    faces = bm.faces[:]
    ANGLE = 0.084726646  # ~5 degrees in radians

    # Extrude faces upwards by 0.6mm
    extruded_faces = bmesh.ops.extrude_face_region(bm, geom=faces)
    bmesh.ops.transform(
        bm,
        matrix=Matrix.Translation((0, 0, 0.6)),
        verts=[v for v in extruded_faces["geom"] if isinstance(v, bmesh.types.BMVert)],
    )

    # Limited dissolve and merge by distance
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=ANGLE,
        verts=bm.verts,
        edges=bm.edges,
        delimit={"NORMAL"},
    )
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    # Select and delete interior faces
    interior_faces = _select_interior_faces(bm)
    if interior_faces:
        bmesh.ops.delete(bm, geom=interior_faces, context="FACES")

    # Second dissolve limited and recalculate normals
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=ANGLE,
        use_dissolve_boundaries=False,
        verts=bm.verts,
        edges=bm.edges,
        delimit={"NORMAL"},
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()


def _apply_scale_to_mesh(obj):
    """
    Apply scale to mesh data

    Args:
        obj: The mesh object to apply scale to
    """
    mesh = obj.data

    # Create a scale matrix from the object's current scale
    scale_matrix = (
        Matrix.Scale(obj.scale.x, 4, (1, 0, 0))
        @ Matrix.Scale(obj.scale.y, 4, (0, 1, 0))
        @ Matrix.Scale(obj.scale.z, 4, (0, 0, 1))
    )

    # Apply scale to mesh vertices
    mesh.transform(scale_matrix)

    # Reset object scale to 1
    obj.scale = (1.0, 1.0, 1.0)


def _set_origin_to_center_of_mass(obj):
    """
    Set object origin to the center of mass (median center)

    This calculates the geometric center of all vertices and moves the mesh
    so that center becomes the object's origin point.

    Args:
        obj: The mesh object to center
    """
    from mathutils import Vector

    mesh = obj.data

    # Calculate the center of all vertices (median center)
    if len(mesh.vertices) == 0:
        return

    center = sum((v.co for v in mesh.vertices), Vector((0, 0, 0))) / len(mesh.vertices)

    # Move all vertices by the negative of the center to place center at origin
    for v in mesh.vertices:
        v.co -= center

    # Move the object location by the center offset (in world space)
    # This keeps the mesh in the same world position but moves the origin
    obj.location += center


def _join_mesh_objects_bmesh(mesh_objects: list):
    """
    Join multiple mesh objects into one using BMesh.

    Args:
        mesh_objects: List of mesh objects to join

    Returns:
        The base mesh object with all others merged into it, or None if empty list
    """
    if not mesh_objects:
        return None
    if len(mesh_objects) == 1:
        return mesh_objects[0]

    base_obj = mesh_objects[0]
    base_mesh = base_obj.data

    # Create BMesh and load base mesh
    bm = bmesh.new()
    bm.from_mesh(base_mesh)

    # Merge each additional object into the base
    for obj in mesh_objects[1:]:
        # Create temporary BMesh for this object
        bm_temp = bmesh.new()
        bm_temp.from_mesh(obj.data)

        # Transform vertices to match base object's world space
        transform_matrix = obj.matrix_world @ base_obj.matrix_world.inverted()
        bm_temp.transform(transform_matrix)

        # Merge the temporary BMesh into the base BMesh
        # We need to manually copy geometry
        vert_map = {}

        for v in bm_temp.verts:
            new_vert = bm.verts.new(v.co)
            vert_map[v.index] = new_vert

        for f in bm_temp.faces:
            try:
                new_verts = [vert_map[v.index] for v in f.verts]
                bm.faces.new(new_verts)
            except ValueError:
                # Face already exists, skip
                pass

        bm_temp.free()

        # Remove the merged object
        bpy.data.objects.remove(obj, do_unlink=True)

    # Update base mesh with merged geometry
    bm.to_mesh(base_mesh)
    base_mesh.update()
    bm.free()

    return base_obj


def _batch_convert_curves_to_meshes(curve_objects: list) -> list:
    """
    Convert curve objects to mesh objects using low-level API (depsgraph evaluation).
    Args:
        curve_objects: List of curve objects to convert

    Returns:
        List of newly created mesh objects
    """
    context = bpy.context
    depsgraph = context.evaluated_depsgraph_get()
    new_mesh_objects = []
    objects_to_remove = []

    for obj in curve_objects:
        if obj.type not in {"CURVE", "SURFACE", "FONT"}:
            continue

        # Get evaluated version with modifiers applied
        obj_eval = obj.evaluated_get(depsgraph)

        # Create mesh from evaluated object
        mesh = bpy.data.meshes.new_from_object(obj_eval)

        # Create new mesh object with same transform
        new_obj = bpy.data.objects.new(obj.name + "_mesh", mesh)
        new_obj.matrix_world = obj.matrix_world.copy()

        # Link to scene collection
        context.scene.collection.objects.link(new_obj)
        new_mesh_objects.append(new_obj)

        # Mark original for removal
        objects_to_remove.append(obj)

    # Remove original curve objects after creating all meshes
    for obj in objects_to_remove:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    return new_mesh_objects


def _select_interior_faces(bm) -> dict:
    """
    Select interior faces in a BMesh using a two-pass method:
        1. Identify candidate faces where all edges have more than 2 face users.
        2. Verify candidates with raycasts to ensure they're truly interior, if the ray
        hits another face along the normal direction whose normal is roughly opposite.
    Args:
        bm: The BMesh to operate on
    Returns:
        A dictionary with selected interior faces
    """
    candidate_faces = [
        f for f in bm.faces if f.edges and all(len(e.link_faces) > 2 for e in f.edges)
    ]

    interior_faces = []
    bm.faces.ensure_lookup_table()

    for face in candidate_faces:
        ray_origin = face.calc_center_median()
        ray_direction = face.normal

        # Check if ray hits another face
        hit = False
        for other_face in bm.faces:
            if other_face == face:
                continue
            # If we can reach the back of another face along the normal, this face is interior
            result = other_face.calc_center_median() - ray_origin
            if result.dot(ray_direction) > 0.001:  # Small epsilon for floating point
                # Check if the other face's normal is roughly opposite
                if other_face.normal.dot(ray_direction) < -0.5:
                    hit = True
                    break

        if hit:
            interior_faces.append(face)

    return interior_faces


def _check_mesh_manifold(design_obj) -> tuple[bool, int]:
    """
    Check if a mesh is manifold (has no non-manifold geometry) using pure BMesh.

    Non-manifold conditions:
    - Vertices with no faces
    - Edges with no faces or more than 2 faces
    - Edges with duplicate faces
    - Vertices not belonging to any edges

    Args:
        design_obj: The mesh object to check

    Returns:
        Tuple of (is_manifold: bool, non_manifold_count: int)
    """
    mesh = design_obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    non_manifold_verts = set()

    # Check for edges with non-manifold conditions
    for edge in bm.edges:
        if len(edge.link_faces) == 0 or len(edge.link_faces) > 2:
            non_manifold_verts.update(edge.verts)
        # Check for duplicate faces on edge
        elif len(edge.link_faces) == 2:
            if edge.link_faces[0] == edge.link_faces[1]:
                non_manifold_verts.update(edge.verts)

    # Check for vertices with no edges
    for vert in bm.verts:
        if len(vert.link_edges) == 0:
            non_manifold_verts.add(vert)
        # Check for vertices with no faces (wire edges)
        elif len(vert.link_faces) == 0:
            non_manifold_verts.add(vert)

    non_manifold_count = len(non_manifold_verts)
    is_manifold = non_manifold_count == 0

    bm.free()

    return is_manifold, non_manifold_count


def _find_logo_placer_node_group():
    """
    Find the Logo Placer node group with flexible name matching.

    Returns:
        The Logo Placer node group, or None if not found
    """
    for ng_name in bpy.data.node_groups.keys():
        if "logo" in ng_name.lower() and "placer" in ng_name.lower():
            return bpy.data.node_groups[ng_name]

    return bpy.data.node_groups.get("Logo Placer")


def _find_design_input_node(node_group, design_num: int):
    """
    Find the design input node within a node group with flexible name matching.

    Args:
        node_group: The node group to search in
        design_num: Which design slot (1 or 2) to find

    Returns:
        The design input node, or None if not found
    """
    design_key = f"design_{design_num}"
    input_key = "input"

    for node in node_group.nodes:
        node_name_lower = node.name.lower()
        if design_key in node_name_lower and input_key in node_name_lower:
            return node

    if design_num == 1:
        return node_group.nodes.get("Design 1 Input")
    else:
        return node_group.nodes.get("Design 2 Input")


def process_svg_to_mesh(filepath: str, design_num: int, report_func=None) -> bool:
    """
    Import an SVG file and process it into a clean manifold mesh.

    Args:
        filepath: Path to the SVG file to import
        design_num: Which design slot (1 or 2) this is for
        report_func: Optional Blender operator report function for user messages

    Returns:
        True if successful, False otherwise
    """
    orig_selected = [obj for obj in bpy.context.selected_objects]
    orig_active = bpy.context.active_object

    start_time = time.time()

    try:
        objects_before = set(bpy.context.scene.objects)

        bpy.ops.import_curve.svg(
            filepath=filepath
        )  # Direct operator use required to import SVG, no direct API

        objects_after = set(bpy.context.scene.objects)
        new_objects = objects_after - objects_before
        imported_objects = list(new_objects)

        if not imported_objects:
            return False

        imported_curves = [obj for obj in imported_objects if obj.type == "CURVE"]

        if not imported_curves:
            if imported_objects:
                imported_curves = imported_objects
            else:
                return False

        curve_objects = []
        mesh_objects = []

        for obj in imported_curves:
            if obj.type == "CURVE":
                curve_objects.append(obj)
            elif obj.type == "MESH":
                mesh_objects.append(obj)

        # Convert curves to meshes using low-level API
        if curve_objects:
            converted_meshes = _batch_convert_curves_to_meshes(curve_objects)
            mesh_objects.extend(converted_meshes)

        if not mesh_objects:
            return False

        # Join all mesh objects into one using BMesh
        design_obj = _join_mesh_objects_bmesh(mesh_objects)
        if not design_obj:
            return False

        design_obj.name = f"Design_{design_num}_SVG"

        # Calculate scale to fit within 40mm
        dimensions = design_obj.dimensions
        max_dim = max(dimensions.x, dimensions.y)
        if max_dim > 0:
            scale_factor = 40.0 / max_dim
            design_obj.scale = (scale_factor, scale_factor, scale_factor)

        _apply_scale_to_mesh(design_obj)

        _process_mesh_geometry(design_obj)

        _set_origin_to_center_of_mass(design_obj)

        # Check if the mesh is manifold after processing
        is_manifold, non_manifold_count = _check_mesh_manifold(design_obj)
        if not is_manifold:
            if report_func:
                report_func(
                    {"ERROR"},
                    f"SVG processing resulted in non-manifold geometry ({non_manifold_count} problematic vertices). "
                    "Try fixing the SVG to use real paths, or use a different design.",
                )
            # Clean up the failed object
            bpy.data.objects.remove(design_obj, do_unlink=True)
            return False

        logo_placer_node_group = _find_logo_placer_node_group()
        if not logo_placer_node_group:
            return False

        design_input_node = _find_design_input_node(logo_placer_node_group, design_num)
        if not design_input_node:
            return False

        try:
            design_input_node.inputs[0].default_value = design_obj
        except Exception:
            return False

        design_obj.hide_viewport = True

        props = bpy.context.scene.nfc_card_props
        if design_num == 1:
            props.has_design_1 = True
        else:
            props.has_design_2 = True

        total_time = time.time() - start_time
        if report_func:
            report_func({"INFO"}, f"Processed design in {total_time:.2f}s")

        return True

    except Exception as e:
        print(f"Error processing SVG: {str(e)}")
        return False
    finally:
        # Restore original selection state
        for obj in bpy.context.view_layer.objects:
            if obj is not None:
                obj.select_set(False)

        for obj in orig_selected:
            if obj and obj.name in bpy.context.view_layer.objects:
                obj.select_set(True)

        if orig_active and orig_active.name in bpy.context.view_layer.objects:
            bpy.context.view_layer.objects.active = orig_active


class OBJECT_OT_nfc_import_svg(Operator):
    """Import an SVG file and process it for use with the NFC card generator"""

    bl_idname = "object.nfc_import_svg"
    bl_label = "Import SVG"
    bl_description = "Import and process an SVG file for the design"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(
        name="SVG File Path",
        description="Path to the SVG file",
        default="",
        subtype="FILE_PATH",
    )

    design_num: bpy.props.IntProperty(
        name="Design Number",
        description="Which design slot to use (1 or 2)",
        default=1,
        min=1,
        max=2,
    )

    filter_glob: bpy.props.StringProperty(
        default="*.svg",
        options={"HIDDEN"},
    )

    def invoke(self, context, event):
        """Open a file browser"""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        """Process the selected SVG file"""
        if not self.filepath:
            self.report({"ERROR"}, "No file selected")
            return {"CANCELLED"}

        if not _find_logo_placer_node_group():
            self.report(
                {"ERROR"},
                "Logo Placer node group not found. Please ensure scene is set up properly.",
            )
            return {"CANCELLED"}

        success = process_svg_to_mesh(self.filepath, self.design_num, self.report)

        if success:
            return {"FINISHED"}
        else:
            self.report(
                {"ERROR"}, "Failed to process SVG file. Check console for details."
            )
            return {"CANCELLED"}


def register():
    bpy.utils.register_class(OBJECT_OT_nfc_import_svg)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_nfc_import_svg)
