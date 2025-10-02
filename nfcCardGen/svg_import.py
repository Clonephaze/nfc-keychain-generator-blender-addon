"""
SVG import and processing utilities for the NFC Card & Keychain Generator add-on.

This module provides functions and operators for importing SVG files,
converting them to clean manifold meshes, and connecting them to the
geometry node setup.
"""

import time

import bpy
from bpy.types import Operator


def _process_mesh_geometry(design_obj):
    """
    Process mesh geometry in edit mode with all operations batched together.
    
    Args:
        design_obj: The mesh object to process
    """
    with bpy.context.temp_override():
        bpy.ops.object.mode_set(mode="EDIT")
        
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.dissolve_limited()

        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.6)})

        bpy.ops.mesh.select_all(action="DESELECT")
        
        try:
            bpy.ops.mesh.select_interior_faces()
            bpy.ops.mesh.delete(type="FACE")
        except Exception:
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.delete(type="FACE")

        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)

        bpy.ops.mesh.remove_doubles()

        bpy.ops.object.mode_set(mode="OBJECT")


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
        bpy.ops.object.select_all(action="DESELECT")
        objects_before = set(bpy.context.scene.objects)

        if not hasattr(bpy.ops.import_curve, "svg"):
            return False

        bpy.ops.import_curve.svg(filepath=filepath)

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

        bpy.ops.object.select_all(action="DESELECT")
        
        curve_objects = []
        mesh_objects = []
        
        for obj in imported_curves:
            if obj.type == "CURVE":
                obj.select_set(True)
                curve_objects.append(obj)
            elif obj.type == "MESH":
                mesh_objects.append(obj)
        
        # WHY: Batch convert all curves at once for better performance
        if curve_objects:
            bpy.context.view_layer.objects.active = curve_objects[0]
            bpy.ops.object.convert(target="MESH")
            mesh_objects.extend(curve_objects)

        if not mesh_objects:
            return False

        if len(mesh_objects) > 1:
            bpy.ops.object.select_all(action="DESELECT")
            for obj in mesh_objects:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_objects[0]
            bpy.ops.object.join()
        elif len(mesh_objects) == 1:
            bpy.context.view_layer.objects.active = mesh_objects[0]

        design_obj = bpy.context.active_object
        design_obj.name = f"Design_{design_num}_SVG"

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        dimensions = design_obj.dimensions
        max_dim = max(dimensions.x, dimensions.y)
        if max_dim > 0:
            scale_factor = 40.0 / max_dim
            design_obj.scale = (scale_factor, scale_factor, scale_factor)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # WHY: Batch all mesh operations to minimize expensive viewport updates
        _process_mesh_geometry(design_obj)

        bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="MEDIAN")

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
        bpy.ops.object.select_all(action="DESELECT")
        for obj in orig_selected:
            if obj.name in bpy.context.view_layer.objects:
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
