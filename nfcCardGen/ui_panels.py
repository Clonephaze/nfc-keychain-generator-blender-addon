"""
UI Panel definitions for the NFC Card & Keychain Generator add-on.

This module contains all the UI panels that will appear in the 3D Viewport sidebar,
allowing users to configure card generation settings and trigger operations.
"""

import bpy
from bpy.types import Panel


class VIEW3D_PT_tag_card_main(Panel):
    """Main panel for NFC Card & Keychain Generator"""

    bl_label = "NFC Card Generator"
    bl_idname = "VIEW3D_PT_tag_card_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NFC Cards"

    def draw(self, context) -> None:
        """Draw the main panel UI."""
        layout = self.layout
        props = context.scene.nfc_card_props

        if not props.scene_setup:
            layout.operator("object.scene_setup", text="Prep Scene", icon="IMPORT")

        else:
            layout.label(text="NFC Card Generator", icon="MESH_CUBE")

        layout.separator()


class VIEW3D_PT_tag_card_shape(Panel):
    """Controls: shape preset, height parameters, bevel settings"""

    bl_label = "Shape Settings & Bevel"
    bl_idname = "VIEW3D_PT_tag_card_shape"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NFC Cards"
    bl_parent_id = "VIEW3D_PT_tag_card_main"

    def draw(self, context) -> None:
        """Draw the shape settings panel."""
        layout = self.layout
        props = context.scene.nfc_card_props

        if not props.scene_setup:
            return

        # View control button
        view_box = layout.box()
        view_box.label(text="View:", icon='VIEW3D')
        view_op = view_box.operator("object.nfc_set_view", text="Top/Side View", icon='AXIS_TOP')
        view_op.view_type = 'TOP_ANGLE'

        layout.separator()

        self._shape_choice_section(layout, props)

        layout.separator()

        self._height_settings_section(layout, props)

        layout.separator()

        self._bevel_settings_section(layout, props)

    def _shape_choice_section(self, layout, props) -> None:
        """Draw the shape choice section with buttons and parameters unique to their shape."""
        layout.label(text="Shape Preset:")

        row = layout.row(align=True)

        # Rectangle button
        rect_op = row.operator(
            "object.nfc_set_shape_preset",
            text="Rectangle",
            depress=(props.shape_preset == "RECTANGLE"),
        )
        rect_op.shape_type = "RECTANGLE"

        # Circle button
        circle_op = row.operator(
            "object.nfc_set_shape_preset",
            text="Circle",
            depress=(props.shape_preset == "CIRCLE"),
        )
        circle_op.shape_type = "CIRCLE"

        if props.shape_preset == "RECTANGLE":
            # Corner Radius Parameter
            corner_row = layout.row(align=True)
            corner_row.prop(props, "corner_radius", text="Corner Rounding")

        if props.shape_preset == "CIRCLE":
            # Keychain Hole Parameter
            keychain_row = layout.row(align=True)
            keychain_row.prop(props, "keychain_choice", text="Keychain Hole")

    def _height_settings_section(self, layout, props) -> None:
        """Draw the height settings section with parameters and calculated heights."""

        layout.label(text="Height Parameters:")
        layout.prop(props, "initial_height", text="Initial Height")
        layout.prop(props, "magnet_choice", text="Add Magnet Holes")

        if props.magnet_choice:
            layout.prop(props, "magnet_depth", text="Magnet Hole Depth")
        layout.prop(props, "nfc_choice", text="Add NFC Slot")

        card_height = (
            props.initial_height
            + (props.magnet_depth if props.magnet_choice else 0)
            + (0.8 if props.nfc_choice else 0)
        )
        final_height = (
            props.initial_height
            + (props.magnet_depth if props.magnet_choice else 0)
            + (0.8 if props.nfc_choice else 0)
            + (0.6 if not props.inset_choice else 0)
        )

        row = layout.row()
        col_labels = row.column()
        col_values = row.column()

        col_labels.label(text="Card Height:")
        col_labels.label(text="Design Height:")
        col_labels.label(text="Final Height:")

        col_values.label(text=f"{card_height:.2f} mm")
        col_values.label(text="0.6 mm" if not props.inset_choice else "Inset")
        col_values.label(text=f"{final_height:.2f} mm")

    def _bevel_settings_section(self, layout, props) -> None:
        """Draw the bevel settings section."""

        col = layout.column(align=True)
        col.label(text="Bevel Settings:")
        col.prop(props, "bevel_amount")
        col.prop(props, "bevel_segments")


class VIEW3D_PT_tag_card_magnet_and_cavity(Panel):
    """Panel for magnet hole and NFC cavity settings"""

    bl_label = "Magnet Settings"
    bl_idname = "VIEW3D_PT_tag_card_magnet"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NFC Cards"
    bl_parent_id = "VIEW3D_PT_tag_card_main"

    def draw(self, context) -> None:
        layout = self.layout
        props = context.scene.nfc_card_props

        if not props.scene_setup:
            return

        # View control buttons
        view_box = layout.box()
        view_box.label(text="View:", icon='VIEW3D')
        row = view_box.row(align=True)
        
        # Side X-Ray view for cutout
        side_op = row.operator("object.nfc_set_view", text="Side (X-Ray)", icon='XRAY')
        side_op.view_type = 'SIDE_XRAY'
        
        # Bottom view for magnets
        if props.magnet_choice:
            bottom_op = row.operator("object.nfc_set_view", text="Bottom", icon='AXIS_TOP')
            bottom_op.view_type = 'BOTTOM'

        layout.separator()

        _draw_nfc_cavity_section = self._draw_nfc_cavity_section(layout, props)
        _draw_magnet_section = self._draw_magnet_section(layout, props)

    def _draw_magnet_section(self, layout, props) -> None:
        layout.label(
            text="Magnet Shape:"
            if props.magnet_choice
            else "Not Generating Magnet Holes"
        )

        if not props.magnet_choice:
            return

        row = layout.row(align=True)

        layout.label(text="Magnet Hole Settings:")

        # Circle button
        circle_op = row.operator(
            "object.nfc_toggle_magnet_shape",
            text="Circle",
            depress=(props.mag_shape == "CIRCLE"),
        )
        circle_op.shape_type = "CIRCLE"

        # Hexagon button
        hex_op = row.operator(
            "object.nfc_toggle_magnet_shape",
            text="Hexagon",
            depress=(props.mag_shape == "HEXAGON"),
        )
        hex_op.shape_type = "HEXAGON"

        # Other magnet settings
        layout.prop(props, "mag_width", text="Magnet Width")
        layout.prop(props, "mag_taper", text="Magnet Taper")
        layout.prop(props, "mag_padding", text="Edge Padding")

    def _draw_nfc_cavity_section(self, layout, props) -> None:
        """Draw the NFC cavity settings section."""
        layout.label(text="NFC Cavity Settings:")
        
        # Cavity shape buttons
        layout.label(text="Cavity Shape:")
        row = layout.row(align=True)
        
        # Rectangle button
        rect_op = row.operator(
            "object.nfc_set_cavity_shape",
            text="Rectangle",
            depress=(props.nfc_cavity_choice == "RECTANGLE"),
        )
        rect_op.shape_type = "RECTANGLE"
        
        # Circle button
        circle_op = row.operator(
            "object.nfc_set_cavity_shape",
            text="Circle",
            depress=(props.nfc_cavity_choice == "CIRCLE"),
        )
        circle_op.shape_type = "CIRCLE"
        
        # Double Circle button (only for rectangle shapes)
        if props.shape_preset == "RECTANGLE":
            double_op = row.operator(
                "object.nfc_set_cavity_shape",
                text="Double Circle",
                depress=(props.nfc_cavity_choice == "DOUBLE_CIRCLE"),
            )
            double_op.shape_type = "DOUBLE_CIRCLE"
        
        layout.prop(props, "nfc_cavity_height", text="Cavity Height")


class VIEW3D_PT_tag_svg_to_mesh_design(Panel):
    """
    Blender UI Panel for importing SVG or generating QR code designs.
    This panel allows users to:
    - Choose whether to inset designs for multi-material printing.
    - Configure two design slots (Design 1 and Design 2, the latter only for rectangle shapes).
    - For each design slot, select between generating a QR code or importing a custom SVG.
    - If QR mode is selected, choose the QR type (Text, WiFi, Contact) and provide relevant input fields.
    - Set the QR error correction level and generate or regenerate the QR code.
    - If SVG mode is selected, import or replace the SVG design.
    - Adjust design settings such as scale and X/Y offset for imported designs.
    The panel is only displayed if the scene setup is complete, as indicated by the 'scene_setup' property.
    """

    bl_label = "Design Import & Settings"
    bl_idname = "VIEW3D_PT_tag_svg_to_mesh_design"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NFC Cards"
    bl_parent_id = "VIEW3D_PT_tag_card_main"

    def draw(self, context) -> None:
        """Draw the design settings panel."""
        layout = self.layout
        props = context.scene.nfc_card_props

        if not props.scene_setup:
            return

        # View control buttons
        view_box = layout.box()
        view_box.label(text="View:", icon='VIEW3D')
        row = view_box.row(align=True)
        
        # Top view to see design
        top_op = row.operator("object.nfc_set_view", text="Top", icon='AXIS_TOP')
        top_op.view_type = 'TOP'
        
        # Side view to see inset/outset
        side_op = row.operator("object.nfc_set_view", text="Side", icon='AXIS_SIDE')
        side_op.view_type = 'SIDE'

        layout.separator()

        self._draw_inset_choice(layout, props)
        self._draw_design_section(layout, props, design_num=1)
        if props.shape_preset == "RECTANGLE":
            self._draw_design_section(layout, props, design_num=2)

    def _draw_inset_choice(self, layout, props) -> None:
        layout.prop(
            props,
            "inset_choice",
            text="Inset Designs"
            if props.shape_preset == "RECTANGLE"
            else "Inset Design",
        )

    def _draw_design_section(self, layout, props, design_num: int) -> None:
        box = layout.box()
        box.label(text=f"Design {design_num}")
        self._draw_mode_buttons(box, props, design_num)
        if self._is_qr_mode(props, design_num):
            self._draw_qr_settings(box, props, design_num)
            self._draw_qr_generate_button(box, props, design_num)
        else:
            self._draw_svg_import_button(box, props, design_num)
        if self._has_design(props, design_num):
            self._draw_design_settings(box, props, design_num)

    def _draw_mode_buttons(self, box, props, design_num: int) -> None:
        row = box.row(align=True)
        qr_op = row.operator(
            "object.nfc_toggle_qr_mode",
            text="Generate QR",
            depress=self._is_qr_mode(props, design_num),
        )
        qr_op.design_num = design_num
        qr_op.enable_qr = True
        svg_op = row.operator(
            "object.nfc_toggle_qr_mode",
            text="Custom SVG",
            depress=not self._is_qr_mode(props, design_num),
        )
        svg_op.design_num = design_num
        svg_op.enable_qr = False

    def _is_qr_mode(self, props, design_num: int) -> bool:
        return props.qr_mode_1 if design_num == 1 else props.qr_mode_2

    def _has_design(self, props, design_num: int) -> bool:
        return props.has_design_1 if design_num == 1 else props.has_design_2

    def _draw_qr_settings(self, box, props, design_num: int) -> None:
        qr_type = props.qr_type_1 if design_num == 1 else props.qr_type_2
        box.prop(props, f"qr_type_{design_num}", text="QR Type")
        if qr_type == "TEXT":
            box.prop(props, f"qr_text_content_{design_num}", text="Content")
        elif qr_type == "WIFI":
            box.prop(props, f"qr_wifi_ssid_{design_num}", text="SSID")
            box.prop(props, f"qr_wifi_password_{design_num}", text="Password")
            box.prop(props, f"qr_wifi_security_{design_num}", text="Encryption")
            box.prop(props, f"qr_wifi_hidden_{design_num}", text="Hidden Network")
        elif qr_type == "CONTACT":
            box.prop(props, f"qr_contact_name_{design_num}", text="Name")
            box.prop(props, f"qr_contact_phone_{design_num}", text="Phone")
            box.prop(props, f"qr_contact_email_{design_num}", text="Email")
            box.prop(props, f"qr_contact_url_{design_num}", text="URL")
            box.prop(props, f"qr_contact_org_{design_num}", text="Organization")
        box.prop(props, f"qr_error_correction_{design_num}", text="Error Correction")

    def _draw_qr_generate_button(self, box, props, design_num: int) -> None:
        if self._has_design(props, design_num):
            box.operator(
                "object.nfc_generate_qr", text="Regenerate QR"
            ).design_num = design_num
        else:
            box.operator(
                "object.nfc_generate_qr", text="Generate QR"
            ).design_num = design_num

    def _draw_svg_import_button(self, box, props, design_num: int) -> None:
        if self._has_design(props, design_num):
            box.operator(
                "object.nfc_import_svg", text="Replace SVG"
            ).design_num = design_num
        else:
            box.operator(
                "object.nfc_import_svg", text="Import SVG"
            ).design_num = design_num

    def _draw_design_settings(self, box, props, design_num: int) -> None:
        col = box.column(align=True)
        col.prop(props, f"scale_{design_num}", text="Scale")
        col.prop(props, f"offset_x_{design_num}", text="X Offset")
        col.prop(props, f"offset_y_{design_num}", text="Y Offset")


class VIEW3D_PT_tag_card_export(Panel):
    """Panel for STL export and final card information"""

    bl_label = "Export & Info"
    bl_idname = "VIEW3D_PT_tag_card_export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "NFC Cards"
    bl_parent_id = "VIEW3D_PT_tag_card_main"

    def draw(self, context) -> None:
        """Draw the export panel."""
        layout = self.layout
        props = context.scene.nfc_card_props

        if not props.scene_setup:
            return

        self._draw_card_info(layout, props)
        layout.separator()
        self._draw_export_section(layout, props)

    def _draw_card_info(self, layout, props) -> None:
        """Draw the card information box."""
        box = layout.box()
        box.label(text="Card Information", icon="INFO")

        info_lines = self._get_card_info_lines(props)
        col = box.column(align=True)
        for info in info_lines:
            col.label(text=info)

    def _get_card_info_lines(self, props) -> list:
        """Return a list of card info lines to display."""
        final_height = (
            props.initial_height
            + (props.magnet_depth if props.magnet_choice else 0)
            + (0.8 if props.nfc_choice else 0)
            + (0 if props.inset_choice else 0.6)
        )
        info_lines = [f"Final Height: {final_height:.2f} mm"]
        if props.magnet_choice:
            info_lines.append(f"Magnet Depth: {props.magnet_depth:.2f} mm")
        if props.nfc_choice:
            info_lines.append("NFC Cutout: Enabled")
        if props.bevel_amount > 0:
            info_lines.append(f"Bevel: {props.bevel_amount:.2f} mm")
        return info_lines

    def _draw_export_section(self, layout, props) -> None:
        """Draw the export box and printing tips."""
        export_box = layout.box()
        export_box.label(text="Export for 3D Printing", icon="EXPORT")
        export_box.operator(
            "object.nfc_export_stl", text="Export STL", icon="MESH_DATA"
        )
        self._draw_printing_tips(export_box)

    def _draw_printing_tips(self, export_box) -> None:
        """Draw helpful 3D printing tips."""
        col = export_box.column(align=True)
        col.scale_y = 0.8
        col.label(text="Tips for 3D Printing:", icon="INFO")
        col.label(
            text="• Remember to add a pause right before the cavity layer fills in"
        )
        col.label(text="• 0.2mm layer height recommended")
        col.label(text="• PLA/PETG materials work well")


def register() -> None:
    """Register all panel classes with Blender."""
    bpy.utils.register_class(VIEW3D_PT_tag_card_main)
    bpy.utils.register_class(VIEW3D_PT_tag_card_shape)
    bpy.utils.register_class(VIEW3D_PT_tag_card_magnet_and_cavity)
    bpy.utils.register_class(VIEW3D_PT_tag_svg_to_mesh_design)
    bpy.utils.register_class(VIEW3D_PT_tag_card_export)


def unregister() -> None:
    """Unregister all panel classes from Blender."""
    bpy.utils.unregister_class(VIEW3D_PT_tag_card_export)
    bpy.utils.unregister_class(VIEW3D_PT_tag_svg_to_mesh_design)
    bpy.utils.unregister_class(VIEW3D_PT_tag_card_magnet_and_cavity)
    bpy.utils.unregister_class(VIEW3D_PT_tag_card_shape)
    bpy.utils.unregister_class(VIEW3D_PT_tag_card_main)
