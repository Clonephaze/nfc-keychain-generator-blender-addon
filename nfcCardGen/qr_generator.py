"""
QR Code generation functionality for the NFC Card & Keychain Generator.

This module handles generating different types of QR codes using the segno library:
- Text/URL QR codes for general content
- WiFi QR codes for network sharing
- Contact (vCard) QR codes for contact information
"""

import os
import tempfile

# Import segno for QR code generation
# Why segno? Segno is a pure Python QR code library that's smaller, more reliable
# than other options and produces better quality codes with more format options
import traceback
from typing import Optional

import bmesh
import bpy
from bpy.types import Material, Object, Operator

try:
    import segno
    from segno import helpers

    print(f"[NFC Addon] Segno loaded: {segno.__version__}")
except Exception as e:
    print(
        "[NFC Addon] ERROR: segno library not found. QR code generation will not work."
    )
    print(f"[NFC Addon] Exception: {e}")
    traceback.print_exc()
    segno = None
    helpers = None


class QRCodeGenerator:
    """
    Handler for generating different types of QR codes and converting them to 3D geometry.

    Supports:
    - Text/URL QR codes for general content
    - WiFi QR codes for network credentials
    - Contact (vCard) QR codes for contact information
    """

    # QR code type constants
    QR_TYPE_TEXT = "TEXT"
    QR_TYPE_WIFI = "WIFI"
    QR_TYPE_CONTACT = "CONTACT"

    @staticmethod
    def is_segno_available() -> bool:
        """
        Check if the segno library is available for QR code generation.

        Returns:
            True if segno is available, False otherwise.
        """
        return segno is not None and helpers is not None

    @classmethod
    def generate_text_qr(
        cls, content: str, error_correction: str = "M"
    ) -> Optional[segno.QRCode]:
        """
        Generate a standard text/URL QR code.

        Args:
            content: Text or URL to encode in the QR code.
            error_correction: Error correction level ('L', 'M', 'Q', 'H').

        Returns:
            QR code object, or None if generation failed.
        """
        if not cls.is_segno_available():
            return None

        try:
            # Create standard QR code - segno automatically optimizes encoding
            qr = segno.make_qr(content, error=error_correction)
            return qr
        except Exception as e:
            print(f"Text QR code generation failed: {e}")
            return None

    @classmethod
    def generate_wifi_qr(
        cls,
        ssid: str,
        password: str = "",
        security: str = "WPA",
        hidden: bool = False,
        error_correction: str = "M",
    ) -> Optional[segno.QRCode]:
        """
        Generate a WiFi QR code using segno's WiFi helper.

        Args:
            ssid: WiFi network name.
            password: WiFi password (empty for open networks).
            security: Security type ('WPA', 'WEP', 'nopass' for open).
            hidden: Whether the network is hidden.
            error_correction: Error correction level ('L', 'M', 'Q', 'H').

        Returns:
            WiFi QR code object, or None if generation failed.
        """
        if not cls.is_segno_available():
            return None

        try:
            # Determine security type
            if not password:
                security = "nopass"

            # Create WiFi QR code using segno's helpers
            qr = helpers.make_wifi(
                ssid=ssid, password=password, security=security, hidden=hidden
            )
            return qr
        except Exception as e:
            print(f"WiFi QR code generation failed: {e}")
            return None

    @classmethod
    def generate_contact_qr(
        cls,
        name: str,
        phone: str = "",
        email: str = "",
        url: str = "",
        org: str = "",
        error_correction: str = "M",
    ) -> Optional[segno.QRCode]:
        """
        Generate a contact (vCard) QR code using segno's vCard helper.

        Args:
            name: Contact's full name.
            phone: Phone number.
            email: Email address.
            url: Website URL.
            org: Organization/company.
            error_correction: Error correction level ('L', 'M', 'Q', 'H').

        Returns:
            Contact QR code object, or None if generation failed.
        """
        if not cls.is_segno_available():
            return None

        try:
            # Create vCard QR code using segno's helpers
            # segno's make_vcard requires 'name' and 'displayname' as first two positional arguments
            qr = helpers.make_vcard(
                name=name,  # Required: structured name (first parameter)
                displayname=name,  # Required: display name (second parameter)
                phone=phone or None,
                email=email or None,
                url=url or None,
                org=org or None,
            )
            return qr
        except Exception as e:
            print(f"Contact QR code generation failed: {e}")
            return None

    @classmethod
    def generate_qr_by_type(cls, qr_type: str, **kwargs) -> Optional[segno.QRCode]:
        """
        Generate QR code based on type with appropriate parameters.

        Args:
            qr_type: Type of QR code ('TEXT', 'WIFI', 'CONTACT').
            **kwargs: Type-specific parameters.

        Returns:
            QR code object, or None if generation failed.
        """
        if qr_type == cls.QR_TYPE_TEXT:
            return cls.generate_text_qr(
                content=kwargs.get("content", ""),
                error_correction=kwargs.get("error_correction", "M"),
            )
        elif qr_type == cls.QR_TYPE_WIFI:
            return cls.generate_wifi_qr(
                ssid=kwargs.get("ssid", ""),
                password=kwargs.get("password", ""),
                security=kwargs.get("security", "WPA"),
                hidden=kwargs.get("hidden", False),
                error_correction=kwargs.get("error_correction", "M"),
            )
        elif qr_type == cls.QR_TYPE_CONTACT:
            return cls.generate_contact_qr(
                name=kwargs.get("name", ""),
                phone=kwargs.get("phone", ""),
                email=kwargs.get("email", ""),
                url=kwargs.get("url", ""),
                org=kwargs.get("org", ""),
                error_correction=kwargs.get("error_correction", "M"),
            )
        else:
            print(f"Unknown QR code type: {qr_type}")
            return None

    @classmethod
    def create_qr_mesh_from_data(
        cls, qr_data: segno.QRCode, size: float = 0.02
    ) -> Optional[Object]:
        """
        Convert QR code data into a 3D mesh object.

        This creates a mesh where each QR code module (pixel) becomes a small cube.

        Args:
            qr_data: QR code data from segno.
            size: Size of the QR code in Blender units.

        Returns:
            Created mesh object, or None if conversion failed.
        """
        if not qr_data:
            return None

        # Get QR code matrix
        # WHY: We need the raw module data to create individual cubes for each pixel
        matrix = []
        for row in qr_data.matrix:
            matrix.append(list(row))

        qr_size = len(matrix)  # QR codes are always square
        module_size = size / qr_size  # Size of each individual module

        # Create new mesh
        mesh = bpy.data.meshes.new("QR_Code")
        qr_object = bpy.data.objects.new("QR_Code", mesh)

        # Add to scene
        bpy.context.collection.objects.link(qr_object)

        # Create mesh data using bmesh for easier manipulation
        bm = bmesh.new()

        try:
            # Create cubes for each dark module (True values in matrix)
            for row_idx, row in enumerate(matrix):
                for col_idx, is_dark in enumerate(row):
                    if is_dark:  # Only create geometry for dark modules
                        # Calculate position for this module
                        x = (col_idx - qr_size / 2) * module_size
                        y = (row_idx - qr_size / 2) * module_size
                        z = 0

                        # Create cube for this module
                        bmesh.ops.create_cube(
                            bm,
                            size=module_size * 0.9,  # Slightly smaller to create gaps
                            matrix=bpy.utils.Matrix.Translation((x, y, z)),
                        )

            # Update mesh
            bm.to_mesh(mesh)
            mesh.update()

            return qr_object

        except Exception as e:
            print(f"QR mesh creation failed: {e}")
            return None

        finally:
            bm.free()

    @staticmethod
    def create_qr_material(name: str = "QR_Code_Material") -> Material:
        """
        Create a material suitable for QR codes.

        Args:
            name: Name for the created material.

        Returns:
            The created material.
        """
        # Create new material
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True

        # Clear default nodes
        nodes = material.node_tree.nodes
        nodes.clear()

        # Add principled BSDF and output nodes
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        output = nodes.new(type="ShaderNodeOutputMaterial")

        # Set up QR code material properties
        # WHY: Dark, matte material ensures good contrast and scannability
        bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)  # Very dark
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.9  # Matte finish

        # Link nodes
        material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        # Position nodes
        bsdf.location = (0, 0)
        output.location = (200, 0)

        return material

    @classmethod
    def prepare_qr_for_card(cls, qr_object: Object, target_size: float = 0.025) -> None:
        """
        Prepare QR code object for card placement by scaling it appropriately.

        Positioning is handled by the geometry node system.

        Args:
            qr_object: The QR code mesh object.
            target_size: Target size for the QR code in meters (default 25mm).
        """
        if not qr_object:
            return

        # Get current QR code bounds
        bbox_corners = [
            qr_object.matrix_world @ vertex.co for vertex in qr_object.bound_box
        ]
        current_size = max(
            max(corner.x for corner in bbox_corners)
            - min(corner.x for corner in bbox_corners),
            max(corner.y for corner in bbox_corners)
            - min(corner.y for corner in bbox_corners),
        )

        # Scale to target size
        if current_size > 0:
            scale_factor = target_size / current_size
            qr_object.scale = (scale_factor, scale_factor, scale_factor)

        # Position at origin - your geometry nodes will handle final placement
        qr_object.location = (0, 0, 0)

        # Name for identification
        qr_object.name = "QR_Code"


def generate_qr_for_card(qr_type: str, **qr_params) -> Optional[Object]:
    """
    Convenience function to generate any type of QR code for card placement.

    Args:
        qr_type: Type of QR code ('TEXT', 'WIFI', 'CONTACT').
        **qr_params: Type-specific parameters for QR generation.

    Returns:
        Created QR code object, or None if generation failed.
    """
    if not QRCodeGenerator.is_segno_available():
        print("Segno library not available for QR code generation")
        return None

    # Generate QR code data based on type
    qr_data = QRCodeGenerator.generate_qr_by_type(qr_type, **qr_params)
    if not qr_data:
        print(f"Failed to generate {qr_type} QR code")
        return None

    # Create mesh from QR data
    qr_object = QRCodeGenerator.create_qr_mesh_from_data(
        qr_data, size=0.02
    )  # 20mm default
    if not qr_object:
        print("Failed to create QR code mesh")
        return None

    # Prepare QR code for card placement (scales to 25mm by default)
    QRCodeGenerator.prepare_qr_for_card(qr_object)

    # Apply QR code material
    # Note: Material application is handled by geometry nodes pipeline
    # qr_material = QRCodeGenerator.create_qr_material(f"QR_{qr_type}_Material")
    # qr_object.data.materials.append(qr_material)

    # Name the object to indicate its type
    qr_object.name = f"QR_Code_{qr_type}"

    return qr_object


def generate_text_qr_for_card(content: str) -> Optional[Object]:
    """Generate a text/URL QR code for card placement."""
    return generate_qr_for_card(QRCodeGenerator.QR_TYPE_TEXT, content=content)


def generate_wifi_qr_for_card(
    ssid: str, password: str = "", security: str = "WPA"
) -> Optional[Object]:
    """Generate a WiFi QR code for card placement."""
    return generate_qr_for_card(
        QRCodeGenerator.QR_TYPE_WIFI, ssid=ssid, password=password, security=security
    )


def generate_contact_qr_for_card(
    name: str, phone: str = "", email: str = "", url: str = "", org: str = ""
) -> Optional[Object]:
    """Generate a contact vCard QR code for card placement."""
    return generate_qr_for_card(
        QRCodeGenerator.QR_TYPE_CONTACT,
        name=name,
        phone=phone,
        email=email,
        url=url,
        org=org,
    )


# ============================================================================
# BLENDER OPERATORS FOR QR CODE GENERATION
# ============================================================================


class OBJECT_OT_nfc_toggle_qr_mode(Operator):
    """Toggle QR code generation mode for a design slot"""

    bl_idname = "object.nfc_toggle_qr_mode"
    bl_label = "Toggle QR Mode"
    bl_description = "Toggle between SVG import and QR code generation mode"
    bl_options = {"REGISTER", "UNDO"}

    # Design number (1 or 2)
    design_num: bpy.props.IntProperty(
        name="Design Number",
        description="Which design slot to toggle (1 or 2)",
        default=1,
        min=1,
        max=2,
    )

    # Enable QR mode (True) or SVG mode (False)
    enable_qr: bpy.props.BoolProperty(
        name="Enable QR Mode",
        description="Whether to enable QR mode (True) or SVG mode (False)",
        default=True,
    )

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene is set up."""
        return context.scene.nfc_card_props.scene_setup

    def execute(self, context):
        """Set QR mode for the specified design slot."""
        props = context.scene.nfc_card_props

        if self.design_num == 1:
            props.qr_mode_1 = self.enable_qr
            # Reset design status when switching modes
            if props.qr_mode_1 != self.enable_qr:
                props.has_design_1 = False
        else:
            props.qr_mode_2 = self.enable_qr
            # Reset design status when switching modes
            if props.qr_mode_2 != self.enable_qr:
                props.has_design_2 = False

        return {"FINISHED"}


class OBJECT_OT_nfc_generate_qr(Operator):
    """Generate a QR code and process it through the SVG pipeline"""

    bl_idname = "object.nfc_generate_qr"
    bl_label = "Generate QR Code"
    bl_description = "Generate a QR code based on the selected type and settings"
    bl_options = {"REGISTER", "UNDO"}

    # Design number (1 or 2)
    design_num: bpy.props.IntProperty(
        name="Design Number",
        description="Which design slot to use (1 or 2)",
        default=1,
        min=1,
        max=2,
    )

    @classmethod
    def poll(cls, context) -> bool:
        """Only allow if scene is set up and segno is available."""
        if not context.scene.nfc_card_props.scene_setup:
            return False
        return QRCodeGenerator.is_segno_available()

    def execute(self, context):
        """Generate QR code and process it."""
        props = context.scene.nfc_card_props

        # Get QR settings for the design slot
        if self.design_num == 1:
            qr_type = props.qr_type_1
            error_correction = props.qr_error_correction_1
        else:
            qr_type = props.qr_type_2
            error_correction = props.qr_error_correction_2

        # Prepare QR generation parameters
        qr_params = {"error_correction": error_correction}

        # Add type-specific parameters
        if qr_type == "TEXT":
            if self.design_num == 1:
                content = props.qr_text_content_1
            else:
                content = props.qr_text_content_2

            if not content.strip():
                self.report({"ERROR"}, "Please enter text or URL content")
                return {"CANCELLED"}

            qr_params["content"] = content

        elif qr_type == "WIFI":
            if self.design_num == 1:
                ssid = props.qr_wifi_ssid_1
                password = props.qr_wifi_password_1
                security = props.qr_wifi_security_1
                hidden = props.qr_wifi_hidden_1
            else:
                ssid = props.qr_wifi_ssid_2
                password = props.qr_wifi_password_2
                security = props.qr_wifi_security_2
                hidden = props.qr_wifi_hidden_2

            if not ssid.strip():
                self.report({"ERROR"}, "Please enter WiFi network name (SSID)")
                return {"CANCELLED"}

            qr_params.update(
                {
                    "ssid": ssid,
                    "password": password,
                    "security": security,
                    "hidden": hidden,
                }
            )

        elif qr_type == "CONTACT":
            if self.design_num == 1:
                name = props.qr_contact_name_1
                phone = props.qr_contact_phone_1
                email = props.qr_contact_email_1
                url = props.qr_contact_url_1
                org = props.qr_contact_org_1
            else:
                name = props.qr_contact_name_2
                phone = props.qr_contact_phone_2
                email = props.qr_contact_email_2
                url = props.qr_contact_url_2
                org = props.qr_contact_org_2

            if not name.strip():
                self.report({"ERROR"}, "Please enter contact name")
                return {"CANCELLED"}

            qr_params.update(
                {"name": name, "phone": phone, "email": email, "url": url, "org": org}
            )

        # Generate QR code
        print(f"[QR Debug] Generating {qr_type} QR code with params: {qr_params}")
        qr_code = QRCodeGenerator.generate_qr_by_type(qr_type, **qr_params)
        if not qr_code:
            print("[QR Debug] Failed to generate QR code object")
            self.report({"ERROR"}, f"Failed to generate {qr_type} QR code")
            return {"CANCELLED"}

        print(f"[QR Debug] QR code generated successfully, version: {qr_code.version}")

        # Save QR code to temporary SVG file
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".svg", delete=False
            ) as temp_file:
                temp_svg_path = temp_file.name

            print(f"[QR Debug] Temporary SVG path: {temp_svg_path}")

            # Create our own SVG with filled rectangles instead of using Segno's SVG export
            print("[QR Debug] Creating custom SVG with filled rectangles...")

            # Get the QR code matrix
            matrix = []
            for row in qr_code.matrix:
                matrix.append(list(row))

            qr_size = len(matrix)
            module_size = 1.0  # Size of each QR module in SVG units

            # Create SVG content with filled rectangles (NO white background)
            svg_width = qr_size * module_size
            svg_height = qr_size * module_size

            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
'''

            # Add ONLY black rectangles for each dark module (no white background)
            for row_idx, row in enumerate(matrix):
                for col_idx, is_dark in enumerate(row):
                    if is_dark:  # Dark module only
                        x = col_idx * module_size
                        y = row_idx * module_size
                        svg_content += f'<rect x="{x}" y="{y}" width="{module_size}" height="{module_size}" fill="black"/>\n'

            svg_content += "</svg>"

            # Write the custom SVG
            with open(temp_svg_path, "w") as f:
                f.write(svg_content)

            print(f"[QR Debug] Custom SVG created with {qr_size}x{qr_size} modules")

            # Import and process the SVG using the proper pipeline
            print("[QR Debug] Processing SVG through proper pipeline...")
            from . import svg_import

            success = svg_import.process_svg_to_mesh(temp_svg_path, self.design_num)

            if success:
                print("[QR Debug] QR SVG processed successfully!")

                # Set the design status
                if self.design_num == 1:
                    props.has_design_1 = True
                else:
                    props.has_design_2 = True

                self.report(
                    {"INFO"},
                    f"QR code generated successfully for Design {self.design_num}",
                )
            else:
                print("[QR Debug] Failed to process QR SVG")
                self.report({"ERROR"}, "Failed to process QR code SVG")
                return {"CANCELLED"}

            # Clean up temporary file
            try:
                os.unlink(temp_svg_path)
                print("[QR Debug] Temporary file cleaned up")
            except Exception:
                print("[QR Debug] Failed to clean up temporary file")

        except Exception as e:
            print(f"[QR Debug] Exception during QR generation: {e}")
            import traceback

            traceback.print_exc()
            self.report({"ERROR"}, f"Failed to generate QR code: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}


def register() -> None:
    """Register QR code generation functionality."""
    if not QRCodeGenerator.is_segno_available():
        print(
            "Warning: segno library not available. QR code generation will be disabled."
        )
        print("To enable QR codes, install the segno wheel in the add-on directory.")

    # Register operators
    bpy.utils.register_class(OBJECT_OT_nfc_toggle_qr_mode)
    bpy.utils.register_class(OBJECT_OT_nfc_generate_qr)


def unregister() -> None:
    """Unregister QR code generation functionality."""
    # Unregister operators
    bpy.utils.unregister_class(OBJECT_OT_nfc_generate_qr)
    bpy.utils.unregister_class(OBJECT_OT_nfc_toggle_qr_mode)

    # Clean up any materials or other resources created during QR generation
    # TODO: Implement cleanup of QR materials when add-on is disabled
    pass
