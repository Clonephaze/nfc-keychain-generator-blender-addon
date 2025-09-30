"""
SVG import and processing utilities for the NFC Card & Keychain Generator add-on.

This module provides functions and operators for importing SVG files,
converting them to clean manifold meshes, and connecting them to the
geometry node setup.
"""

import bmesh
import bpy
from bpy.types import Operator


def process_svg_to_mesh(filepath: str, design_num: int) -> bool:
    """
    Import an SVG file and process it into a clean manifold mesh.

    Args:
        filepath: Path to the SVG file to import
        design_num: Which design slot (1 or 2) this is for

    Returns:
        True if successful, False otherwise
    """
    # Store the current selection and active object to restore later
    orig_selected = [obj for obj in bpy.context.selected_objects]
    orig_active = bpy.context.active_object

    try:
        # Clear any existing selection first
        bpy.ops.object.select_all(action="DESELECT")

        # Count objects before import
        objects_before = set(bpy.context.scene.objects)

        # 1. Import the SVG file
        if not hasattr(bpy.ops.import_curve, "svg"):
            return False

        bpy.ops.import_curve.svg(filepath=filepath)

        # Check what objects were added
        objects_after = set(bpy.context.scene.objects)
        new_objects = objects_after - objects_before

        # Get all newly imported objects (not just curves)
        imported_objects = list(new_objects)

        if not imported_objects:
            return False

        # Find curve objects specifically
        imported_curves = [obj for obj in imported_objects if obj.type == "CURVE"]

        # If no curves, try to work with whatever was imported
        if not imported_curves:
            if imported_objects:
                imported_curves = imported_objects
            else:
                return False

        # 2. Convert curves to meshes (or handle already mesh objects)
        mesh_objects = []
        for obj in imported_curves:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            if obj.type == "CURVE":
                bpy.ops.object.convert(target="MESH")
                mesh_objects.append(obj)
            elif obj.type == "MESH":
                mesh_objects.append(obj)

        if not mesh_objects:
            return False

        # 3. Join the meshes if there are multiple
        if len(mesh_objects) > 1:
            # Select all mesh objects
            bpy.ops.object.select_all(action="DESELECT")
            for obj in mesh_objects:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_objects[0]
            bpy.ops.object.join()
        elif len(mesh_objects) == 1:
            bpy.context.view_layer.objects.active = mesh_objects[0]

        # Get the resulting mesh object
        design_obj = bpy.context.active_object
        design_obj.name = f"Design_{design_num}_SVG"

        # 4. Scale to 40mm
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        # Get dimensions and calculate scale factor
        dimensions = design_obj.dimensions
        max_dim = max(dimensions.x, dimensions.y)
        if max_dim > 0:
            scale_factor = 40.0 / max_dim
            design_obj.scale = (scale_factor, scale_factor, scale_factor)

        # Apply scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # 5. Clean up mesh
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.dissolve_limited()

        # 6. Extrude 0.6mm
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 0.6)})

        # 7. Clear selection
        bpy.ops.mesh.select_all(action="DESELECT")

        # 8. Delete interior faces (if any)
        # This is a bit tricky as we need to identify interior faces
        # Using BMesh for more advanced selection
        bm = bmesh.from_edit_mesh(design_obj.data)

        # Find and select non-manifold elements
        non_manifold_verts = [v for v in bm.verts if not v.is_manifold]
        non_manifold_edges = [e for e in bm.edges if not e.is_manifold]

        # Select non-manifold elements
        for v in non_manifold_verts:
            v.select = True
        for e in non_manifold_edges:
            e.select = True

        # Select interior faces (faces with all vertices selected)
        for f in bm.faces:
            if all(v.select for v in f.verts):
                f.select = True

        bmesh.update_edit_mesh(design_obj.data)

        # Delete selected elements (interior faces)
        if non_manifold_verts or non_manifold_edges:
            bpy.ops.mesh.delete(type="FACE")

        # 9. Recalculate normals
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)

        # Return to object mode
        bpy.ops.object.mode_set(mode="OBJECT")

        # 10. Set origin to center of mass (volume)
        bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_MASS", center="MEDIAN")

        # 11. Connect to the node group
        # Try to find the Logo Placer node group with flexibility
        logo_placer_node_group = None
        for ng_name in bpy.data.node_groups.keys():
            if "logo" in ng_name.lower() and "placer" in ng_name.lower():
                logo_placer_node_group = bpy.data.node_groups[ng_name]
                break

        # If not found with flexible search, try exact name
        if not logo_placer_node_group:
            logo_placer_node_group = bpy.data.node_groups.get("Logo Placer")

        if not logo_placer_node_group:
            return False

        # Find the design input node with flexibility
        design_input_node = None
        design_key = f"design_{design_num}"
        input_key = "input"

        for node in logo_placer_node_group.nodes:
            node_name_lower = node.name.lower()
            if design_key in node_name_lower and input_key in node_name_lower:
                design_input_node = node
                break

        # If not found with flexible search, try exact name
        if not design_input_node:
            if design_num == 1:
                design_input_node = logo_placer_node_group.nodes.get("Design 1 Input")
            else:
                design_input_node = logo_placer_node_group.nodes.get("Design 2 Input")

        if not design_input_node:
            return False

        # Connect the object to the node
        try:
            design_input_node.inputs[0].default_value = design_obj
        except Exception as e:
            return False

        # 12. Hide the design object from viewport
        design_obj.hide_viewport = True

        # Set properties to indicate we have a design
        props = bpy.context.scene.nfc_card_props
        if design_num == 1:
            props.has_design_1 = True
        else:
            props.has_design_2 = True

        return True

    except Exception as e:
        print(f"Error processing SVG: {str(e)}")
        return False
    finally:
        # Restore original selection
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

    # File path for the SVG file
    filepath: bpy.props.StringProperty(
        name="SVG File Path",
        description="Path to the SVG file",
        default="",
        subtype="FILE_PATH",
    )

    # Design number (1 or 2)
    design_num: bpy.props.IntProperty(
        name="Design Number",
        description="Which design slot to use (1 or 2)",
        default=1,
        min=1,
        max=2,
    )

    # Filter for file browser
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

        # Verify the Logo Placer node group exists before processing
        if "Logo Placer" not in bpy.data.node_groups:
            # Try flexible search for node group
            found_logo_placer = False
            for ng_name in bpy.data.node_groups.keys():
                if "logo" in ng_name.lower() and "placer" in ng_name.lower():
                    found_logo_placer = True
                    break

            if not found_logo_placer:
                self.report(
                    {"ERROR"},
                    "Logo Placer node group not found. Please ensure scene is set up properly.",
                )
                return {"CANCELLED"}

        # Process the SVG
        success = process_svg_to_mesh(self.filepath, self.design_num)

        if success:
            self.report(
                {"INFO"}, f"SVG imported and processed for Design {self.design_num}"
            )
            return {"FINISHED"}
        else:
            self.report(
                {"ERROR"}, "Failed to process SVG file. Check console for details."
            )
            return {"CANCELLED"}


# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_nfc_import_svg)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_nfc_import_svg)
