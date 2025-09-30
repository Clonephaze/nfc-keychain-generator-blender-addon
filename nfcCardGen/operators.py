"""
Operator definitions for the NFC Card & Keychain Generator add-on.

This module contains all the operators (buttons and actions) that users can trigger
from the UI panel. These operators will append the pre-built geometry node setup
and provide automation for SVG processing.
"""

import os
from typing import Set

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

# Import shared utilities and constants
from .utils import (
    DRIVER_MAPPINGS,
    MOD_OPT_MAPPING,
    OBJECT_NAME,
    ensure_scene_mode,
    force_update_ui_and_geometry,
    get_modifier_value,
    setup_driver_connection,
    update_modifier_option,
)


class OBJECT_OT_scene_setup(Operator):
    """Setup scene by clearing all objects and appending the pre-built NFC card setup"""

    bl_idname = "object.scene_setup"
    bl_label = "Setup Scene"
    bl_description = "Append the NFC card geometry node setup to the current scene"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene hasn't been set up yet."""
        return not context.scene.nfc_card_props.scene_setup

    def execute(self, context) -> Set[str]:
        """
        This will:
        1. Clear all objects from the current scene
        2. Set scene units to mm and set scale to 0.001
        3. Append the object with its modifiers.
        4. Fetch current modifier values and update scene properties accordingly
        5. Add drivers between modifiers based on DRIVER_MAPPINGS
        """

        addon_dir = os.path.dirname(__file__)
        blend_file = os.path.join(addon_dir, "appendInfo.blend")

        if not os.path.exists(blend_file):
            self.report(
                {"ERROR"},
                "Template .blend file not found. Please ensure appendInfo.blend is in the add-on directory.",
            )
            return {"CANCELLED"}

        try:
            # Setup basic scene properties
            if not self._setup_scene_basics(context):
                return {"CANCELLED"}

            # Append the card object from the blend file
            if not self._append_card_object(context, blend_file):
                return {"CANCELLED"}

            context.scene.nfc_card_props.scene_setup = True

            # Get the card object reference
            card_obj = bpy.data.objects.get(OBJECT_NAME)
            if not card_obj:
                self.report(
                    {"ERROR"}, f"{OBJECT_NAME} object not found after appending"
                )
                return {"CANCELLED"}

            # Sync modifier values to UI properties
            self._sync_modifier_values_to_props(context, card_obj)

            # Setup drivers between modifiers
            self._setup_modifier_drivers(card_obj)

            return {"FINISHED"}

        except Exception as e:
            self.report({"ERROR"}, f"Failed to append {OBJECT_NAME} object: {str(e)}")
            return {"CANCELLED"}

    def _setup_scene_basics(self, context) -> bool:
        """Set up basic scene properties like units and delete existing objects"""
        try:
            ensure_scene_mode("OBJECT", report=self.report)

            # Delete all existing objects
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False, confirm=False)

            # Set scene units
            context.scene.unit_settings.system = "METRIC"
            context.scene.unit_settings.length_unit = "MILLIMETERS"
            context.scene.unit_settings.scale_length = (
                0.001  # Makes units match real-world mm
            )

            # Set clip start to avoid clipping issues
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == "VIEW_3D":
                        for space in area.spaces:
                            if space.type == "VIEW_3D":
                                space.clip_start = 2.0

            return True
        except Exception as e:
            self.report({"ERROR"}, f"Failed to set up scene basics: {str(e)}")
            return False

    def _append_card_object(self, context, blend_file_path) -> bool:
        """Append the card object from the blend file"""
        try:
            with bpy.data.libraries.load(blend_file_path, link=False) as (
                data_from,
                data_to,
            ):
                data_to.objects = [
                    name for name in data_from.objects if name == OBJECT_NAME
                ]
                data_to.node_groups = data_from.node_groups

                if not data_to.objects:
                    self.report(
                        {"ERROR"},
                        f'The "{OBJECT_NAME}" object was not found in appendInfo.blend.',
                    )
                    return False

            for obj in data_to.objects:
                if obj and obj.name == OBJECT_NAME:
                    context.collection.objects.link(obj)

                    bpy.ops.object.select_all(action="DESELECT")
                    obj.select_set(True)

                    context.view_layer.objects.active = obj
                    return True

            return False
        except Exception as e:
            self.report({"ERROR"}, f"Failed to append object: {str(e)}")
            return False

    def _sync_modifier_values_to_props(self, context, card_obj) -> None:
        """Fetch modifier values and update scene properties"""
        for logical_name, (modifier_name, socket_name) in MOD_OPT_MAPPING.items():
            try:
                value = get_modifier_value(card_obj, modifier_name, socket_name)
                if value is not None:
                    # Special handling for enum properties that are stored as integers in geometry nodes
                    if logical_name == "MAG_SHAPE":
                        # Convert integer value to string enum value
                        # 0 = "CIRCLE", 1 = "HEXAGON"
                        value = "CIRCLE" if value == 0 else "HEXAGON"

                    setattr(context.scene.nfc_card_props, logical_name.lower(), value)
            except Exception as e:
                print(
                    f"Warning: Could not fetch initial value for {logical_name}: {str(e)}"
                )

    def _setup_modifier_drivers(self, card_obj) -> None:
        """Set up drivers between modifiers based on DRIVER_MAPPINGS"""
        for (source_mod, source_socket), (
            target_mod,
            target_prop,
        ) in DRIVER_MAPPINGS.items():
            setup_driver_connection(
                card_obj, source_mod, source_socket, target_mod, target_prop
            )


class OBJECT_OT_nfc_toggle_boolean_option(Operator):
    """Toggle boolean options for NFC card features"""

    bl_idname = "object.nfc_toggle_boolean_option"
    bl_label = "Toggle Boolean Option"
    bl_description = "Toggle boolean options for NFC card features"
    bl_options = {"REGISTER", "UNDO"}

    # Property to determine which option to toggle
    option_type: bpy.props.EnumProperty(
        name="Option Type",
        description="Which boolean option to toggle",
        items=[
            ("MAGNET_CHOICE", "Magnet Holes", "Toggle magnet holes"),
            ("INSET_CHOICE", "Inset Design", "Toggle inset design"),
            ("KEYCHAIN_CHOICE", "Keychain Hole", "Toggle keychain hole"),
        ],
        default="MAGNET_CHOICE",
    )

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene is set up and Card object exists."""
        if not context.scene.nfc_card_props.scene_setup:
            return False
        return OBJECT_NAME in bpy.data.objects

    def execute(self, context) -> Set[str]:
        """Toggle the boolean option via the modifier socket."""
        ensure_scene_mode("OBJECT", report=self.report)

        props = context.scene.nfc_card_props

        # Get current value and toggle it
        if self.option_type == "MAGNET_CHOICE":
            current_value = props.magnet_choice
            props.magnet_choice = not current_value
            new_value = props.magnet_choice
        elif self.option_type == "INSET_CHOICE":
            current_value = props.inset_choice
            props.inset_choice = not current_value
            new_value = props.inset_choice
        elif self.option_type == "KEYCHAIN_CHOICE":
            current_value = props.keychain_choice
            props.keychain_choice = not current_value
            new_value = props.keychain_choice

        print(f"Toggling {self.option_type}: {current_value} -> {new_value}")

        if update_modifier_option(self.option_type, new_value, self.report):
            force_update_ui_and_geometry(context, self.option_type.lower())

            return {"FINISHED"}
        else:
            return {"CANCELLED"}


class OBJECT_OT_nfc_set_shape_preset(Operator):
    """Set shape preset (rectangle or circle)"""

    bl_idname = "object.nfc_set_shape_preset"
    bl_label = "Set Shape Preset"
    bl_description = "Set the shape preset for the NFC card/tag"
    bl_options = {"REGISTER", "UNDO"}

    # Property to determine which shape to set
    shape_type: bpy.props.EnumProperty(
        name="Shape Type",
        description="Which shape to set",
        items=[
            ("RECTANGLE", "Rectangle", "Rectangular card shape"),
            ("CIRCLE", "Circle", "Circular card shape w/ optional keychain loop"),
        ],
        default="RECTANGLE",
    )

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene is set up and Card object exists."""
        if not context.scene.nfc_card_props.scene_setup:
            return False
        return OBJECT_NAME in bpy.data.objects

    def execute(self, context) -> Set[str]:
        """Set the shape preset via the modifier socket."""
        ensure_scene_mode("OBJECT", report=self.report)

        print(f"Setting shape to: {self.shape_type}")

        # Update the property
        context.scene.nfc_card_props.shape_preset = self.shape_type

        # Determine the value to set (0 = Rectangle, 1 = Circle)
        choice = 0 if self.shape_type == "RECTANGLE" else 1
        print(f"Choice value: {choice}")

        if update_modifier_option("SHAPE_CHOICE", choice, self.report):
            force_update_ui_and_geometry(context, "shape_preset")

            return {"FINISHED"}
        else:
            return {"CANCELLED"}


# HELPER FUNCTIONS
# All utility functions moved to utils.py


class OBJECT_OT_nfc_toggle_magnet_shape(Operator):
    """Set magnet shape (circle or hexagon)"""

    bl_idname = "object.nfc_toggle_magnet_shape"
    bl_label = "Set Magnet Shape"
    bl_description = "Set the shape of the magnet holes"
    bl_options = {"REGISTER", "UNDO"}

    # Property to determine which shape to set
    shape_type: bpy.props.EnumProperty(
        name="Shape Type",
        description="Which magnet shape to set",
        items=[
            ("CIRCLE", "Circle", "Circular magnet holes (harder tolerance)"),
            ("HEXAGON", "Hexagon", "Hexagonal magnet holes (better tolerance)"),
        ],
        default="HEXAGON",
    )

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene is set up, Card object exists, and magnets are enabled."""
        if not context.scene.nfc_card_props.scene_setup:
            return False
        if not context.scene.nfc_card_props.magnet_choice:
            return False
        return OBJECT_NAME in bpy.data.objects

    def execute(self, context) -> Set[str]:
        """Set the magnet shape via the modifier socket."""
        ensure_scene_mode("OBJECT", report=self.report)

        print(f"Setting magnet shape to: {self.shape_type}")

        # Update the property
        context.scene.nfc_card_props.mag_shape = self.shape_type
        
        # The conversion between string enum and integer is handled in update_modifier_option
        if update_modifier_option("MAG_SHAPE", self.shape_type, self.report):
            force_update_ui_and_geometry(context, "mag_shape")
            
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


class OBJECT_OT_nfc_export_stl(Operator, ExportHelper):
    """Export the NFC card to STL format for 3D printing"""
    
    bl_idname = "object.nfc_export_stl"
    bl_label = "Export STL"
    bl_description = "Export the NFC card as an STL file for 3D printing"
    bl_options = {'REGISTER', 'UNDO'}
    
    # ExportHelper mixin class uses this
    filename_ext = ".stl"
    filter_glob: StringProperty(
        default="*.stl",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    def execute(self, context):
        """Execute the STL export operation."""
        try:
            # Get the final card object
            card_obj = None
            for obj in bpy.context.scene.objects:
                if obj.name.lower() == "card" or obj.name.startswith("FinalCardTag") or obj.name == "CardTag":
                    card_obj = obj
                    break
            
            if not card_obj:
                self.report({'ERROR'}, "No card object found to export. Generate a card first.")
                return {'CANCELLED'}
            
            # Clear selection and select only the card object
            bpy.ops.object.select_all(action='DESELECT')
            card_obj.select_set(True)
            bpy.context.view_layer.objects.active = card_obj
            
            # Export to STL using the native Blender STL exporter
            bpy.ops.wm.stl_export(
                filepath=self.filepath,
                export_selected_objects=True,
                global_scale=1.0,
                apply_modifiers=True
            )
            
            self.report({'INFO'}, f"STL exported successfully to: {os.path.basename(self.filepath)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"STL export failed: {str(e)}")
            return {'CANCELLED'}


CLASSES = (
    OBJECT_OT_scene_setup,
    OBJECT_OT_nfc_toggle_boolean_option,
    OBJECT_OT_nfc_set_shape_preset,
    OBJECT_OT_nfc_toggle_magnet_shape,
    OBJECT_OT_nfc_export_stl,
)


def register() -> None:
    """Register all operator classes with Blender."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister all operator classes from Blender."""
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
