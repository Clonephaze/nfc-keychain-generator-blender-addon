"""
Utility functions and constants for the NFC Card & Keychain Generator add-on.

This module contains shared functions and constants used across the add-on.
"""

import bpy

# CONSTANTS
OBJECT_NAME = "Card"

# Mappings for modifiers and their inputs
MOD_OPT_MAPPING = {
    "SHAPE_CHOICE": ("Outer Shape", "Card Choice"),
    "CORNER_RADII": ("Outer Shape", "Corner Rounding"),
    "KEYCHAIN_CHOICE": ("Outer Shape", "Keychain Hole"),
    "INITIAL_HEIGHT": ("Outer Shape", "Initial Height"),
    "MAGNET_CHOICE": ("Outer Shape", "Add Magnet Holes"),
    "MAGNET_DEPTH": ("Outer Shape", "Magnet Depth"),
    "NFC_CHOICE": ("Outer Shape", "NFC Cutout"),
    "BEVEL_AMOUNT": ("Outer Shape", "Bevel"),
    "BEVEL_SEGMENTS": ("Outer Shape", "Bevel Segments"),
    "REAL_BEVEL_AMOUNT": ("Bevel", "Amount"),
    "REAL_BEVEL_SEGMENTS": ("Bevel", "Segments"),
    "MAG_SHAPE": ("Inner Hole and Magnets", "Hole Shape"),
    "MAG_WIDTH": ("Inner Hole and Magnets", "Hole Width"),
    "MAG_TAPER": ("Inner Hole and Magnets", "Hole Taper"),
    "MAG_EDGE_PAD": ("Inner Hole and Magnets", "Edge Padding"),
    "INSET_CHOICE": ("Logo Placer", "Inset Design"),
    "OFFSET_X_1": ("Logo Placer", "Design 1 X Offset"),
    "OFFSET_Y_1": ("Logo Placer", "Design 1 Y Offset"),
    "SCALE_1": ("Logo Placer", "Design 1 Scale"),
    "OFFSET_X_2": ("Logo Placer", "Design 2 X Offset"),
    "OFFSET_Y_2": ("Logo Placer", "Design 2 Y Offset"),
    "SCALE_2": ("Logo Placer", "Design 2 Scale"),
}

# Additional mapping for driver connections
DRIVER_MAPPINGS = {
    # Source: (Modifier, Socket) -> Target: (Modifier, Property)
    ("Outer Shape", "Bevel"): ("Bevel", "width"),
    ("Outer Shape", "Bevel Segments"): ("Bevel", "segments"),
}


# SHARED FUNCTIONS
def force_update_ui_and_geometry(context, property_name=None):
    """Force UI and geometry updates after a property change.

    Args:
        context: The current Blender context
        property_name: Optional name of the property for logging
    """
    # Force dependency graph updates
    bpy.context.evaluated_depsgraph_get().update()
    context.view_layer.update()

    # Force all UI panels to redraw
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

    # Force the object to update its geometry
    card_obj = bpy.data.objects.get(OBJECT_NAME)
    if card_obj:
        card_obj.update_tag()
        # if property_name:
        #     print(f"Tagged Card object for update after {property_name} change")


def update_modifier_option(logical_name, value, report_func=None):
    """Update a modifier option using the logical name from MOD_OPT_MAPPING.

    Args:
        logical_name (str): The logical name key from MOD_OPT_MAPPING (e.g., "SHAPE_CHOICE")
        value: Value to set (can be int, float, bool, etc.)
        report_func (callable, optional): Blender operator report function for error messages

    Returns:
        bool: True if update succeeded, False if it failed
    """
    if logical_name not in MOD_OPT_MAPPING:
        if report_func:
            report_func({"ERROR"}, f"Unknown logical name: {logical_name}")
        return False

    # Special handling for enum properties that need to be stored as integers in geometry nodes
    if logical_name == "MAG_SHAPE":
        # Convert string enum value to integer value
        # "CIRCLE" = 0, "HEXAGON" = 1
        value = 0 if value == "CIRCLE" else 1

    modifier_name, socket_name = MOD_OPT_MAPPING[logical_name]
    return update_modifier_input(modifier_name, socket_name, value, report_func)


def find_socket_identifier(modifier, socket_name):
    """Find the identifier for a socket in a geometry node modifier.

    Args:
        modifier: The Blender modifier object
        socket_name (str): The name of the socket to find

    Returns:
        str: Socket identifier if found, None otherwise
    """
    if not (hasattr(modifier, "node_group") and modifier.node_group):
        return None

    node_group = modifier.node_group

    # Try to find the input by name in the interface
    for input_item in node_group.interface.items_tree:
        if (
            input_item.item_type == "SOCKET"
            and input_item.in_out == "INPUT"
            and input_item.name == socket_name
        ):
            return input_item.identifier

    return None


def get_modifier_value(obj, modifier_name, socket_name):
    """Get the value of a modifier input socket.

    Args:
        obj: The Blender object with the modifier
        modifier_name (str): Name of the modifier
        socket_name (str): Name of the socket

    Returns:
        The value of the socket, or None if not found
    """
    modifier = obj.modifiers.get(modifier_name)
    if not modifier:
        return None

    socket_id = find_socket_identifier(modifier, socket_name)
    if socket_id:
        return modifier[socket_id]

    # Fallback: try direct access
    try:
        return modifier[socket_name]
    except Exception:
        return None


def setup_driver_connection(
    obj, source_mod_name, source_socket_name, target_mod_name, target_property
):
    """Set up a driver connection between a geometry node input and a modifier property.

    Args:
        obj: The Blender object with the modifiers
        source_mod_name (str): Name of the source modifier
        source_socket_name (str): Name of the source socket
        target_mod_name (str): Name of the target modifier
        target_property (str): Property name on the target modifier

    Returns:
        bool: True if driver setup succeeded, False if it failed
    """
    source_modifier = obj.modifiers.get(source_mod_name)
    target_modifier = obj.modifiers.get(target_mod_name)

    if not (source_modifier and target_modifier):
        return False

    # Find the identifier for the source socket
    socket_id = find_socket_identifier(source_modifier, source_socket_name)
    if not socket_id:
        print(
            f"Warning: '{source_socket_name}' socket not found in '{source_mod_name}' modifier node group."
        )
        return False

    try:
        # Add driver to the target property
        driver = target_modifier.driver_add(target_property)

        # Set up the driver to read from the source socket
        var = driver.driver.variables.new()
        var.name = "source_val"
        var.type = "SINGLE_PROP"
        target = var.targets[0]
        target.id = obj

        # The property path for geometry nodes modifier input
        target.data_path = f'modifiers["{source_mod_name}"]["{socket_id}"]'
        driver.driver.expression = "source_val"

        return True
    except Exception as e:
        print(f"Warning: Could not add driver: {str(e)}")
        return False


def update_modifier_input(modifier_name, socket_name, value, report_func=None):
    """Update a specific input on a geometry nodes modifier.

    Args:
        modifier_name (str): Name of the modifier
        socket_name (str): Name of the input socket (display name)
        value: Value to set
        report_func (callable, optional): Blender operator report function for error messages

    Returns:
        bool: True if update succeeded, False if it failed
    """
    if not ensure_scene_mode("OBJECT"):
        if report_func:
            report_func({"ERROR"}, "Must be in Object mode to update modifiers")
        return False

    # Get the Card object
    card_obj = bpy.data.objects.get(OBJECT_NAME)
    if not card_obj:
        if report_func:
            report_func({"ERROR"}, f"Card object '{OBJECT_NAME}' not found")
        return False

    # Get the modifier
    modifier = card_obj.modifiers.get(modifier_name)
    if not modifier:
        if report_func:
            report_func(
                {"ERROR"}, f"Modifier '{modifier_name}' not found on {OBJECT_NAME}"
            )
        return False

    try:
        # Try to access through the node group interface
        if hasattr(modifier, "node_group") and modifier.node_group:
            # Try to find the input by name in the interface
            socket_id = find_socket_identifier(modifier, socket_name)
            if socket_id:
                # Use the identifier to set the value
                modifier[socket_id] = value
                # print(
                #     f"Successfully updated {socket_name} (ID: {socket_id}) to {value}"
                # )
                return True

        # Fallback: try direct access
        modifier[socket_name] = value
        print(f"Updated {modifier_name} - {socket_name} to {value}")
        return True

    except Exception as e:
        error_msg = f"Failed to update {socket_name}: {str(e)}"
        print(error_msg)
        if report_func:
            report_func({"ERROR"}, error_msg)
        return False


def ensure_scene_mode(mode, report=None):
    """Ensure the scene is in the specified mode.
    Args:
        mode (str): The desired mode, e.g. 'OBJECT', 'EDIT', 'SCULPT', etc.
        report (callable, optional): A Blender operator report function to surface warnings, e.g. self.report
    Returns:
        bool: True if we are in the desired mode (either already or after switching), False if switching failed.
    Notes:
        - Keeps side effects minimal; only attempts a mode switch.
        - Tries to ensure an active object exists when switching to non-OBJECT modes.
    """
    try:
        if bpy.context.mode == mode:
            return True

        # When switching to a non-OBJECT mode, Blender requires an active object.
        if mode != "OBJECT" and bpy.context.active_object is None:
            # Try to activate a visible object in the current view layer
            for obj in bpy.context.view_layer.objects:
                try:
                    if obj.visible_get():
                        bpy.context.view_layer.objects.active = obj
                        break
                except Exception:
                    # visible_get can fail for some data-block states; ignore and continue
                    continue

        bpy.ops.object.mode_set(mode=mode)
        return bpy.context.mode == mode
    except Exception as e:
        if report:
            try:
                report({"WARNING"}, f"Unable to switch to {mode} mode: {e}")
            except Exception:
                pass
        return False
