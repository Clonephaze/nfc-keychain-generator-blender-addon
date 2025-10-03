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
def update_corner_radii(self, context):
    """Update callback for corner_radius property."""
    update_property(self, context, "corner_radius", "CORNER_RADII", self.corner_radius)


def update_keychain_choice(self, context):
    """Update callback for keychain_choice property."""
    update_property(
        self, context, "keychain_choice", "KEYCHAIN_CHOICE", self.keychain_choice
    )


def update_initial_height(self, context):
    """Update callback for initial_height property."""
    update_property(
        self, context, "initial_height", "INITIAL_HEIGHT", self.initial_height
    )


def update_magnet_choice(self, context):
    """Update callback for magnet_choice property."""
    update_property(self, context, "magnet_choice", "MAGNET_CHOICE", self.magnet_choice)


def update_magnet_depth(self, context):
    """Update callback for magnet_depth property."""
    update_property(self, context, "magnet_depth", "MAGNET_DEPTH", self.magnet_depth)


def update_nfc_cutout(self, context):
    """Update callback for nfc_choice property."""
    update_property(self, context, "nfc_choice", "NFC_CHOICE", self.nfc_choice)


def update_bevel_amount(self, context):
    """Update callback for bevel_amount property."""
    update_property(self, context, "bevel_amount", "BEVEL_AMOUNT", self.bevel_amount)


def update_bevel_segment_count(self, context):
    """Update callback for bevel_segments property."""
    update_property(
        self, context, "bevel_segments", "BEVEL_SEGMENTS", self.bevel_segments
    )


def update_mag_shape(self, context):
    """Update callback for mag_shape property."""
    update_property(self, context, "mag_shape", "MAG_SHAPE", self.mag_shape)


def update_mag_width(self, context):
    """Update callback for mag_width property."""
    update_property(self, context, "mag_width", "MAG_WIDTH", self.mag_width)


def update_mag_taper(self, context):
    """Update callback for mag_taper property."""
    update_property(self, context, "mag_taper", "MAG_TAPER", self.mag_taper)


def update_mag_padding(self, context):
    """Update callback for MAG_EDGE_PAD property."""
    update_property(self, context, "mag_padding", "MAG_EDGE_PAD", self.mag_padding)


def update_inset_choice(self, context):
    """Update callback for inset_choice property."""
    update_property(self, context, "inset_choice", "INSET_CHOICE", self.inset_choice)


def update_offset_x_1(self, context):
    """Update callback for offset_x_1 property."""
    update_property(self, context, "offset_x_1", "OFFSET_X_1", self.offset_x_1)


def update_offset_y_1(self, context):
    """Update callback for offset_y_1 property."""
    update_property(self, context, "offset_y_1", "OFFSET_Y_1", self.offset_y_1)


def update_scale_1(self, context):
    """Update callback for scale_1 property."""
    update_property(self, context, "scale_1", "SCALE_1", self.scale_1)


def update_offset_x_2(self, context):
    """Update callback for offset_x_2 property."""
    update_property(self, context, "offset_x_2", "OFFSET_X_2", self.offset_x_2)


def update_offset_y_2(self, context):
    """Update callback for offset_y_2 property."""
    update_property(self, context, "offset_y_2", "OFFSET_Y_2", self.offset_y_2)


def update_scale_2(self, context):
    """Update callback for scale_2 property."""
    update_property(self, context, "scale_2", "SCALE_2", self.scale_2)


def update_nfc_cavity_height(self, context):
    """Update callback for nfc_cavity_height property."""
    update_property(
        self, context, "nfc_cavity_height", "NFC_CAVITY_HEIGHT", self.nfc_cavity_height
    )


class NFCCardProperties(PropertyGroup):
    """
    Property group for NFC card/keychain generation parameters.

    These properties will be exposed in the UI panel and passed to
    geometry node groups for card generation.
    """

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
        default=12,
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
