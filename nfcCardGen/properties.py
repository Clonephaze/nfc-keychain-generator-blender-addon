"""
Property definitions for the NFC Card & Keychain Generator add-on.

This module defines all the custom properties that will be exposed in the UI
and used to control the geometry node groups and modifiers.
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup

# Import shared utilities and constants
from .utils import OBJECT_NAME, force_update_ui_and_geometry, update_modifier_option


def update_property(self, context, prop_name, logical_name, value):
    """Generic update callback for properties that map to modifiers.

    Args:
        self: The property group instance
        context: The current Blender context
        prop_name: Name of the property being updated (for logging)
        logical_name: The logical name in MOD_OPT_MAPPING (e.g., "MAGNET_CHOICE")
        value: The new value to set
    """
    # print(f"UPDATE CALLBACK: {prop_name} changed to {value}")

    if self.scene_setup and OBJECT_NAME in context.blend_data.objects:
        # print(f"Scene is set up and Card object exists, updating {logical_name}...")
        update_modifier_option(logical_name, value)
        # print(f"Modifier update success: {success}")

        # Force UI and geometry updates
        force_update_ui_and_geometry(context, prop_name)
    else:
        print("Scene not set up or Card object not found")


# Property-specific update callbacks that delegate to the generic function
def _make_updater(prop_attr: str, logical_name: str):
    """Factory that creates an update callback for a Blender property.

    Args:
        prop_attr: The attribute name on the PropertyGroup (e.g. "corner_radius")
        logical_name: The key in MOD_OPT_MAPPING (e.g. "CORNER_RADII")
    """
    def _update(self, context):
        update_property(self, context, prop_attr, logical_name, getattr(self, prop_attr))
    return _update


# Shape & dimension callbacks
update_corner_radii = _make_updater("corner_radius", "CORNER_RADII")
update_keychain_choice = _make_updater("keychain_choice", "KEYCHAIN_CHOICE")
update_initial_height = _make_updater("initial_height", "INITIAL_HEIGHT")
update_magnet_choice = _make_updater("magnet_choice", "MAGNET_CHOICE")
update_magnet_depth = _make_updater("magnet_depth", "MAGNET_DEPTH")
update_nfc_cutout = _make_updater("nfc_choice", "NFC_CHOICE")
update_bevel_amount = _make_updater("bevel_amount", "BEVEL_AMOUNT")
update_bevel_segment_count = _make_updater("bevel_segments", "BEVEL_SEGMENTS")

# Magnet callbacks
update_mag_shape = _make_updater("mag_shape", "MAG_SHAPE")
update_mag_width = _make_updater("mag_width", "MAG_WIDTH")
update_mag_taper = _make_updater("mag_taper", "MAG_TAPER")
update_mag_padding = _make_updater("mag_padding", "MAG_EDGE_PAD")

# Design layout callbacks
update_inset_choice = _make_updater("inset_choice", "INSET_CHOICE")

def update_design_boolean_solver(self, context):
    """Update the boolean solver on Logo Placer Mesh Boolean nodes."""
    from .utils import update_design_boolean_solver as _apply_solver
    _apply_solver(self.design_boolean_solver)
update_offset_x_1 = _make_updater("offset_x_1", "OFFSET_X_1")
update_offset_y_1 = _make_updater("offset_y_1", "OFFSET_Y_1")
update_scale_1 = _make_updater("scale_1", "SCALE_1")
update_offset_x_2 = _make_updater("offset_x_2", "OFFSET_X_2")
update_offset_y_2 = _make_updater("offset_y_2", "OFFSET_Y_2")
update_scale_2 = _make_updater("scale_2", "SCALE_2")
update_nfc_cavity_height = _make_updater("nfc_cavity_height", "NFC_CAVITY_HEIGHT")

# Text callbacks – Design 1
update_design_1_text = _make_updater("design_1_text", "DESIGN_1_TEXT")
update_text_1 = _make_updater("text_1", "TEXT_1")
update_text_size_1 = _make_updater("text_size_1", "TEXT_SIZE_1")
update_character_spacing_1 = _make_updater("character_spacing_1", "CHARACTER_SPACING_1")
update_word_spacing_1 = _make_updater("word_spacing_1", "WORD_SPACING_1")
update_line_spacing_1 = _make_updater("line_spacing_1", "LINE_SPACING_1")
update_text_box_width_1 = _make_updater("text_box_width_1", "TEXT_BOX_WIDTH_1")
update_text_box_height_1 = _make_updater("text_box_height_1", "TEXT_BOX_HEIGHT_1")
update_text_x_offset_1 = _make_updater("text_x_offset_1", "TEXT_X_OFFSET_1")
update_text_y_offset_1 = _make_updater("text_y_offset_1", "TEXT_Y_OFFSET_1")

# Text callbacks – Design 2
update_design_2_text = _make_updater("design_2_text", "DESIGN_2_TEXT")
update_text_2 = _make_updater("text_2", "TEXT_2")
update_text_size_2 = _make_updater("text_size_2", "TEXT_SIZE_2")
update_character_spacing_2 = _make_updater("character_spacing_2", "CHARACTER_SPACING_2")
update_word_spacing_2 = _make_updater("word_spacing_2", "WORD_SPACING_2")
update_line_spacing_2 = _make_updater("line_spacing_2", "LINE_SPACING_2")
update_text_box_width_2 = _make_updater("text_box_width_2", "TEXT_BOX_WIDTH_2")
update_text_box_height_2 = _make_updater("text_box_height_2", "TEXT_BOX_HEIGHT_2")
update_text_x_offset_2 = _make_updater("text_x_offset_2", "TEXT_X_OFFSET_2")
update_text_y_offset_2 = _make_updater("text_y_offset_2", "TEXT_Y_OFFSET_2")


class NFCCardProperties(PropertyGroup):
    """
    Property group for NFC card/keychain generation parameters.

    These properties will be exposed in the UI panel and passed to
    geometry node groups for card generation.
    """

    # ---- Computed height helpers ----
    def get_card_height(self) -> float:
        """Card body height before design layer is added."""
        return (
            self.initial_height
            + (self.magnet_depth if self.magnet_choice else 0)
            + (0.8 if self.nfc_choice else 0)
        )

    def get_final_height(self) -> float:
        """Total height including the design layer (0.6 mm unless inset)."""
        return self.get_card_height() + (0.6 if not self.inset_choice else 0)

    # Scene setup tracking
    scene_setup: BoolProperty(
        name="Scene Setup",
        description="Whether the NFC card scene has been set up",
        default=False,
        options={"HIDDEN"},  # Don't show in UI
    )

    # Shape preset for UI selection
    shape_preset: EnumProperty(
        name="Shape Preset",
        description="Select the shape preset for the final object",
        items=[
            (
                "RECTANGLE",
                "Rectangle",
                "Standard rectangular card shape, supports an NFC card of size '85.5mm x 54mm'",
            ),
            (
                "CIRCLE",
                "Circle",
                "Circular shape w/ optional keychain loop, supports an NFC chip up to 25.4 mm in diameter",
            ),
        ],
        default="RECTANGLE",
    )

    # Corner radius property
    corner_radius: bpy.props.FloatProperty(
        name="Corner Rounding",
        description="Radius for rounding the corners of the card",
        default=3,
        min=0.0,
        max=11.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_corner_radii,
    )

    # Keychain loop choice property
    keychain_choice: BoolProperty(
        name="Keychain Loop",
        description="Enable or disable the keychain loop on the card",
        default=True,
        update=update_keychain_choice,
    )

    # Initial height property
    initial_height: bpy.props.FloatProperty(
        name="Initial Height",
        description="Set the initial height of the card before magnet height and nfc cutout adjustments",
        default=2.4,
        min=0.8,
        max=10.0,
        precision=3,
        step=1,
        unit="LENGTH",
        update=update_initial_height,
    )

    # Magnet hole properties
    magnet_choice: BoolProperty(
        name="Add Magnet Holes",
        description="Add holes for magnets",
        default=True,
        update=update_magnet_choice,
    )

    # Magnet depth property
    magnet_depth: bpy.props.FloatProperty(
        name="Magnet Depth",
        description="Depth of the magnet holes",
        default=2.0,
        min=1.0,
        max=3.0,
        precision=3,
        step=1,
        unit="LENGTH",
        update=update_magnet_depth,
    )

    # NFC cutout properties
    nfc_choice: BoolProperty(
        name="Add NFC Cutout",
        description="Add a cutout for NFC chip placement",
        default=True,
        update=update_nfc_cutout,
    )

    # Bevel amount property
    bevel_amount: bpy.props.FloatProperty(
        name="Bevel Amount",
        description="Control the bevel size on edges",
        default=0.75,
        min=0.0,
        max=3.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_bevel_amount,
    )

    # Bevel segment count property
    bevel_segments: bpy.props.IntProperty(
        name="Bevel Segments",
        description="Number of segments for bevel",
        default=1,
        min=1,
        max=40,
        update=update_bevel_segment_count,
    )

    # NFC Cavity type choice property
    nfc_cavity_choice: EnumProperty(
        name="NFC Cavity Shape",
        description="Select the shape of the NFC cavity(s)",
        items=[
            ("RECTANGLE", "Rectangle", "Rectangular NFC cavity"),
            ("CIRCLE", "Circle", "Circular NFC cavity"),
            (
                "DOUBLE_CIRCLE",
                "Double Circle",
                "Two circular NFC cavities (Rectangular Shape Only)",
            ),
        ],
        default="RECTANGLE",
        # No update callback - use operator buttons instead
    )

    # NFC Cavity height property
    nfc_cavity_height: bpy.props.FloatProperty(
        name="NFC Cavity Height",
        description="Height of the NFC cavity - changing this can cause clipping with design layers, though it may be necessary for certain NFC tags",
        default=0.8,
        min=0.6,
        max=1,
        precision=2,
        step=1,
        # unit="LENGTH",
        subtype="FACTOR",
        update=update_nfc_cavity_height,
    )

    # Magnet shape property
    mag_shape: EnumProperty(
        name="Magnet Shape",
        description="Select the shape of the magnet holes",
        items=[
            ("CIRCLE", "Circle", "Circular magnet holes (harder tolerance)"),
            ("HEXAGON", "Hexagon", "Hexagonal magnet holes (better tolerance)"),
        ],
        default="HEXAGON",
        update=update_mag_shape,
    )

    # Magnet width property
    mag_width: bpy.props.FloatProperty(
        name="Magnet Width",
        description="Width of the magnet holes",
        default=10.0,
        min=1.0,
        max=15.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_mag_width,
    )

    # Magnet taper property
    mag_taper: bpy.props.FloatProperty(
        name="Magnet Taper",
        description="Taper angle of the magnet holes",
        default=0.087,  # ~5 degrees in radians
        min=0.0,
        max=0.697434,  # ~40 degrees in radians
        precision=2,
        step=1,
        unit="ROTATION",
        update=update_mag_taper,
    )

    # Magnet edge padding property
    mag_padding: bpy.props.FloatProperty(
        name="Magnet Edge Padding",
        description="Padding around the edges of the magnet holes",
        default=22,
        min=0.0,
        max=50.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_mag_padding,
    )

    # Inset design properties
    inset_choice: BoolProperty(
        name="Add Inset Design",
        description="Add an inset design to the card",
        default=False,
        update=update_inset_choice,
    )

    design_boolean_solver: EnumProperty(
        name="Boolean Solver",
        description=(
            "Boolean solver for design placement. "
            "Manifold is faster but Exact handles problematic geometry better"
        ),
        items=[
            ("MANIFOLD", "Manifold", "Fast solver, works well with clean geometry"),
            ("EXACT", "Exact", "Slower but more robust for complex or self-intersecting shapes"),
        ],
        default="MANIFOLD",
        update=update_design_boolean_solver,
    )

    # Export settings
    export_format: EnumProperty(
        name="Export Format",
        description="File format for card export",
        items=[
            ("3MF", "3MF", "Export with material data for multi-color slicers (requires 3MF IO addon)"),
            ("STL", "STL", "Standard mesh export for single-color printing"),
        ],
        default="3MF",
    )

    # Design 1 properties
    offset_x_1: bpy.props.FloatProperty(
        name="Design 1 X Offset",
        description="X-axis offset for design 1",
        default=0.0,
        min=-8.0,
        max=8.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_offset_x_1,
    )

    offset_y_1: bpy.props.FloatProperty(
        name="Design 1 Y Offset",
        description="Y-axis offset for design 1",
        default=0.0,
        min=-8.0,
        max=8.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_offset_y_1,
    )

    scale_1: bpy.props.FloatProperty(
        name="Design 1 Scale",
        description="Scale for design 1",
        default=1.0,
        min=0.0,
        max=5.0,
        precision=2,
        step=1,
        update=update_scale_1,
    )

    # Design status properties
    has_design_1: bpy.props.BoolProperty(
        name="Has Design 1",
        description="Whether Design 1 has been imported",
        default=False,
    )

    has_design_2: bpy.props.BoolProperty(
        name="Has Design 2",
        description="Whether Design 2 has been imported",
        default=False,
    )

    # QR Code generation properties for Design 1
    qr_mode_1: bpy.props.BoolProperty(
        name="QR Mode 1",
        description="Whether Design 1 is in QR code generation mode",
        default=False,
    )

    qr_type_1: bpy.props.EnumProperty(
        name="QR Type 1",
        description="Type of QR code to generate for Design 1",
        items=[
            ("TEXT", "Text/URL", "Text or URL QR code"),
            ("WIFI", "WiFi", "WiFi network QR code"),
            ("CONTACT", "vCard", "Contact information QR code"),
            ("EMAIL", "Email", "Email message QR code"),
        ],
        default="TEXT",
    )

    qr_error_correction_1: bpy.props.EnumProperty(
        name="Error Correction 1",
        description="Error correction level for Design 1 QR code",
        items=[
            ("L", "Low", "Low error correction (~7%)"),
            ("M", "Medium", "Medium error correction (~15%)"),
            ("Q", "Quartile", "Quartile error correction (~25%)"),
            ("H", "High", "High error correction (~30%)"),
        ],
        default="M",
    )

    # Text/URL QR properties for Design 1
    qr_text_content_1: bpy.props.StringProperty(
        name="Text/URL Content 1",
        description="Text or URL content for Design 1 QR code",
        default="",
    )

    # WiFi QR properties for Design 1
    qr_wifi_ssid_1: bpy.props.StringProperty(
        name="WiFi SSID 1",
        description="WiFi network name for Design 1 QR code",
        default="",
    )

    qr_wifi_password_1: bpy.props.StringProperty(
        name="WiFi Password 1",
        description="WiFi password for Design 1 QR code",
        default="",
        subtype="PASSWORD",
    )

    qr_wifi_security_1: bpy.props.EnumProperty(
        name="WiFi Security 1",
        description="WiFi security type for Design 1 QR code",
        items=[
            ("WPA", "WPA/WPA2", "WPA or WPA2 security"),
            ("WEP", "WEP", "WEP security (legacy)"),
            ("nopass", "Open", "No password/open network"),
        ],
        default="WPA",
    )

    qr_wifi_hidden_1: bpy.props.BoolProperty(
        name="Hidden Network 1",
        description="Whether the WiFi network is hidden for Design 1 QR code",
        default=False,
    )

    # Contact QR properties for Design 1
    qr_contact_name_1: bpy.props.StringProperty(
        name="Contact Name 1",
        description="Contact name for Design 1 vCard QR code",
        default="",
    )

    qr_contact_phone_1: bpy.props.StringProperty(
        name="Contact Phone 1",
        description="Contact phone number for Design 1 vCard QR code",
        default="",
    )

    qr_contact_email_1: bpy.props.StringProperty(
        name="Contact Email 1",
        description="Contact email for Design 1 vCard QR code",
        default="",
    )

    qr_contact_url_1: bpy.props.StringProperty(
        name="Contact URL 1",
        description="Contact website URL for Design 1 vCard QR code",
        default="",
    )

    qr_contact_org_1: bpy.props.StringProperty(
        name="Contact Organization 1",
        description="Contact organization for Design 1 vCard QR code",
        default="",
    )

    # Email QR properties for Design 1
    qr_email_to_1: bpy.props.StringProperty(
        name="Email To 1",
        description="Recipient email address for Design 1 email QR code",
        default="",
    )

    qr_email_cc_1: bpy.props.StringProperty(
        name="Email CC 1",
        description="Carbon copy recipient(s) for Design 1 email QR code (comma-separated)",
        default="",
    )

    qr_email_bcc_1: bpy.props.StringProperty(
        name="Email BCC 1",
        description="Blind carbon copy recipient(s) for Design 1 email QR code (comma-separated)",
        default="",
    )

    qr_email_subject_1: bpy.props.StringProperty(
        name="Email Subject 1",
        description="Subject line for Design 1 email QR code",
        default="",
    )

    qr_email_body_1: bpy.props.StringProperty(
        name="Email Body 1",
        description="Message body for Design 1 email QR code",
        default="",
    )

    # QR Code generation properties for Design 2
    qr_mode_2: bpy.props.BoolProperty(
        name="QR Mode 2",
        description="Whether Design 2 is in QR code generation mode",
        default=False,
    )

    qr_type_2: bpy.props.EnumProperty(
        name="QR Type 2",
        description="Type of QR code to generate for Design 2",
        items=[
            ("TEXT", "Text/URL", "Text or URL QR code"),
            ("WIFI", "WiFi", "WiFi network QR code"),
            ("CONTACT", "vCard", "Contact information QR code"),
            ("EMAIL", "Email", "Email message QR code"),
        ],
        default="TEXT",
    )

    qr_error_correction_2: bpy.props.EnumProperty(
        name="Error Correction 2",
        description="Error correction level for Design 2 QR code",
        items=[
            ("L", "Low", "Low error correction (~7%)"),
            ("M", "Medium", "Medium error correction (~15%)"),
            ("Q", "Quartile", "Quartile error correction (~25%)"),
            ("H", "High", "High error correction (~30%)"),
        ],
        default="M",
    )

    # Text/URL QR properties for Design 2
    qr_text_content_2: bpy.props.StringProperty(
        name="Text/URL Content 2",
        description="Text or URL content for Design 2 QR code",
        default="",
    )

    # WiFi QR properties for Design 2
    qr_wifi_ssid_2: bpy.props.StringProperty(
        name="WiFi SSID 2",
        description="WiFi network name for Design 2 QR code",
        default="",
    )

    qr_wifi_password_2: bpy.props.StringProperty(
        name="WiFi Password 2",
        description="WiFi password for Design 2 QR code",
        default="",
        subtype="PASSWORD",
    )

    qr_wifi_security_2: bpy.props.EnumProperty(
        name="WiFi Security 2",
        description="WiFi security type for Design 2 QR code",
        items=[
            ("WPA", "WPA/WPA2", "WPA or WPA2 security"),
            ("WEP", "WEP", "WEP security (legacy)"),
            ("nopass", "Open", "No password/open network"),
        ],
        default="WPA",
    )

    qr_wifi_hidden_2: bpy.props.BoolProperty(
        name="Hidden Network 2",
        description="Whether the WiFi network is hidden for Design 2 QR code",
        default=False,
    )

    # Contact QR properties for Design 2
    qr_contact_name_2: bpy.props.StringProperty(
        name="Contact Name 2",
        description="Contact name for Design 2 vCard QR code",
        default="",
    )

    qr_contact_phone_2: bpy.props.StringProperty(
        name="Contact Phone 2",
        description="Contact phone number for Design 2 vCard QR code",
        default="",
    )

    qr_contact_email_2: bpy.props.StringProperty(
        name="Contact Email 2",
        description="Contact email for Design 2 vCard QR code",
        default="",
    )

    qr_contact_url_2: bpy.props.StringProperty(
        name="Contact URL 2",
        description="Contact website URL for Design 2 vCard QR code",
        default="",
    )

    qr_contact_org_2: bpy.props.StringProperty(
        name="Contact Organization 2",
        description="Contact organization for Design 2 vCard QR code",
        default="",
    )

    # Email QR properties for Design 2
    qr_email_to_2: bpy.props.StringProperty(
        name="Email To 2",
        description="Recipient email address for Design 2 email QR code",
        default="",
    )

    qr_email_cc_2: bpy.props.StringProperty(
        name="Email CC 2",
        description="Carbon copy recipient(s) for Design 2 email QR code (comma-separated)",
        default="",
    )

    qr_email_bcc_2: bpy.props.StringProperty(
        name="Email BCC 2",
        description="Blind carbon copy recipient(s) for Design 2 email QR code (comma-separated)",
        default="",
    )

    qr_email_subject_2: bpy.props.StringProperty(
        name="Email Subject 2",
        description="Subject line for Design 2 email QR code",
        default="",
    )

    qr_email_body_2: bpy.props.StringProperty(
        name="Email Body 2",
        description="Message body for Design 2 email QR code",
        default="",
    )

    # Design 2 properties
    offset_x_2: bpy.props.FloatProperty(
        name="Design 2 X Offset",
        description="X-axis offset for design 2",
        default=0.0,
        min=-8.0,
        max=8.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_offset_x_2,
    )

    offset_y_2: bpy.props.FloatProperty(
        name="Design 2 Y Offset",
        description="Y-axis offset for design 2",
        default=0.0,
        min=-8.0,
        max=8.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_offset_y_2,
    )

    scale_2: bpy.props.FloatProperty(
        name="Design 2 Scale",
        description="Scale for design 2",
        default=1.0,
        min=0.0,
        max=5.0,
        precision=2,
        step=1,
        update=update_scale_2,
    )

    # Text properties - Design 1
    design_1_text: BoolProperty(
        name="Add Text to Design 1",
        description="Enable text overlay on Design 1",
        default=False,
        update=update_design_1_text,
    )

    text_1: bpy.props.StringProperty(
        name="Text",
        description="Text content for Design 1",
        default="Clone Core",
        update=update_text_1,
    )

    text_size_1: bpy.props.FloatProperty(
        name="Text Size",
        description="Font size for Design 1 text",
        default=16.22,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_size_1,
    )

    character_spacing_1: bpy.props.FloatProperty(
        name="Character Spacing",
        description="Spacing between characters for Design 1 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_character_spacing_1,
    )

    word_spacing_1: bpy.props.FloatProperty(
        name="Word Spacing",
        description="Spacing between words for Design 1 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_word_spacing_1,
    )

    line_spacing_1: bpy.props.FloatProperty(
        name="Line Spacing",
        description="Spacing between lines for Design 1 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_line_spacing_1,
    )

    text_box_width_1: bpy.props.FloatProperty(
        name="Text Box Width",
        description="Width of the text box for Design 1",
        default=66.0,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_box_width_1,
    )

    text_box_height_1: bpy.props.FloatProperty(
        name="Text Box Height",
        description="Height of the text box for Design 1",
        default=0.0,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_box_height_1,
    )

    text_x_offset_1: bpy.props.FloatProperty(
        name="Text X Offset",
        description="X-axis offset for Design 1 text",
        default=-20.28,
        min=-10000.0,
        max=10000.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_x_offset_1,
    )

    text_y_offset_1: bpy.props.FloatProperty(
        name="Text Y Offset",
        description="Y-axis offset for Design 1 text",
        default=-27.40,
        min=-10000.0,
        max=10000.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_y_offset_1,
    )

    font_path_1: bpy.props.StringProperty(
        name="Custom Font",
        description="Path to custom font file for Design 1 text",
        default="",
        subtype='FILE_PATH',
    )

    # Text properties - Design 2
    design_2_text: BoolProperty(
        name="Add Text to Design 2",
        description="Enable text overlay on Design 2",
        default=False,
        update=update_design_2_text,
    )

    text_2: bpy.props.StringProperty(
        name="Text",
        description="Text content for Design 2",
        default="",
        update=update_text_2,
    )

    text_size_2: bpy.props.FloatProperty(
        name="Text Size",
        description="Font size for Design 2 text",
        default=16.22,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_size_2,
    )

    character_spacing_2: bpy.props.FloatProperty(
        name="Character Spacing",
        description="Spacing between characters for Design 2 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_character_spacing_2,
    )

    word_spacing_2: bpy.props.FloatProperty(
        name="Word Spacing",
        description="Spacing between words for Design 2 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_word_spacing_2,
    )

    line_spacing_2: bpy.props.FloatProperty(
        name="Line Spacing",
        description="Spacing between lines for Design 2 text",
        default=1.0,
        min=0.0,
        precision=3,
        step=0.1,
        update=update_line_spacing_2,
    )

    text_box_width_2: bpy.props.FloatProperty(
        name="Text Box Width",
        description="Width of the text box for Design 2",
        default=40.0,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_box_width_2,
    )

    text_box_height_2: bpy.props.FloatProperty(
        name="Text Box Height",
        description="Height of the text box for Design 2",
        default=15.3,
        min=0.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_box_height_2,
    )

    text_x_offset_2: bpy.props.FloatProperty(
        name="Text X Offset",
        description="X-axis offset for Design 2 text",
        default=0.0,
        min=-10000.0,
        max=10000.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_x_offset_2,
    )

    text_y_offset_2: bpy.props.FloatProperty(
        name="Text Y Offset",
        description="Y-axis offset for Design 2 text",
        default=0.0,
        min=-10000.0,
        max=10000.0,
        precision=2,
        step=1,
        unit="LENGTH",
        update=update_text_y_offset_2,
    )

    font_path_2: bpy.props.StringProperty(
        name="Custom Font",
        description="Path to custom font file for Design 2 text",
        default="",
        subtype='FILE_PATH',
    )

    # QR Code Advanced Styling Options - Design 1
    qr_module_style_1: bpy.props.EnumProperty(
        name="QR Module Style 1",
        description="Shape style for QR code data modules",
        items=[
            ("SQUARE", "Square", "Standard square modules"),
            ("ROUNDED", "Rounded", "Adaptive rounded corners for organic flow"),
            ("CIRCLE", "Circle", "Circular modules"),
            ("SQUIRCLE", "Squircle", "Super-ellipse modules"),
        ],
        default="ROUNDED",
    )

    qr_finder_style_1: bpy.props.EnumProperty(
        name="QR Finder Style 1",
        description="Shape style for QR code finder pattern centers",
        items=[
            ("SQUIRCLE", "Squircle", "Super-ellipse finder centers"),
            ("SQUARE", "Square", "Standard square finder centers"),
            ("CIRCLE", "Circle", "Circular finder centers"),
        ],
        default="SQUIRCLE",  # Changed from SQUARE - better default while keeping option available
    )

    qr_finder_border_style_1: bpy.props.EnumProperty(
        name="QR Finder Border Style 1",
        description="Shape style for QR code finder pattern borders (auto-determined)",
        items=[
            ("SQUIRCLE", "Squircle", "Super-ellipse finder borders"),
            ("SQUARE", "Square", "Square finder borders"),
            ("CIRCLE", "Circle", "Circular finder borders"),
        ],
        default="SQUIRCLE",  # Changed from SQUARE - better default while keeping option available
    )

    # QR Code Advanced Styling Options - Design 2
    qr_module_style_2: bpy.props.EnumProperty(
        name="QR Module Style 2",
        description="Shape style for QR code data modules",
        items=[
            ("SQUARE", "Square", "Standard square modules"),
            ("ROUNDED", "Rounded", "Adaptive rounded corners for organic flow"),
            ("CIRCLE", "Circle", "Circular modules"),
            ("SQUIRCLE", "Squircle", "Super-ellipse modules"),
        ],
        default="ROUNDED",
    )

    qr_finder_style_2: bpy.props.EnumProperty(
        name="QR Finder Style 2",
        description="Shape style for QR code finder pattern centers",
        items=[
            ("SQUIRCLE", "Squircle", "Super-ellipse finder centers"),
            ("SQUARE", "Square", "Standard square finder centers"),
            ("CIRCLE", "Circle", "Circular finder centers"),
        ],
        default="SQUIRCLE",  # Changed from SQUARE - better default while keeping option available
    )

    qr_finder_border_style_2: bpy.props.EnumProperty(
        name="QR Finder Border Style 2",
        description="Shape style for QR code finder pattern borders (auto-determined)",
        items=[
            ("SQUIRCLE", "Squircle", "Super-ellipse finder borders"),
            ("SQUARE", "Square", "Square finder borders"),
            ("CIRCLE", "Circle", "Circular finder borders"),
        ],
        default="SQUIRCLE",  # Changed from SQUARE - better default while keeping option available
    )


def register() -> None:
    """Register property classes with Blender."""
    bpy.utils.register_class(NFCCardProperties)

    # Add properties to Scene for global access
    bpy.types.Scene.nfc_card_props = bpy.props.PointerProperty(type=NFCCardProperties)


def unregister() -> None:
    """Unregister property classes from Blender."""
    # Remove properties from Scene
    if hasattr(bpy.types.Scene, "nfc_card_props"):
        del bpy.types.Scene.nfc_card_props

    bpy.utils.unregister_class(NFCCardProperties)
