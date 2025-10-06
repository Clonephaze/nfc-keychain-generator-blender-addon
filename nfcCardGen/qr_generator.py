"""
QR Code generation functionality for the NFC Card & Keychain Generator.

This module handles generating different types of QR codes using the segno library:
- Text/URL QR codes for general content
- WiFi QR codes for network sharing
- Contact (vCard) QR codes for contact information
"""

import os
import traceback
from typing import Optional

import bmesh
import bpy
import numpy as np
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


def _get_temp_svg_path(design_num: int) -> str:
    """
    Get a temporary SVG file path for QR code processing.
    
    Uses the extension's user directory with a unique filename to ensure proper permissions
    and automatic cleanup. Files are intended to be deleted immediately after use.
    
    Args:
        design_num: Which design slot this is for (1 or 2)
        
    Returns:
        Full path to the temporary SVG file
    """
    import time
    import random
    
    temp_dir = bpy.utils.extension_path_user(__package__, path="temp", create=True)
    # Create unique filename with timestamp and random component to avoid conflicts
    timestamp = int(time.time() * 1000)  # milliseconds
    random_id = random.randint(1000, 9999)
    filename = f"qr_design_{design_num}_{timestamp}_{random_id}.svg"
    return os.path.join(temp_dir, filename)


def _cleanup_old_temp_files() -> None:
    """
    Clean up any old temporary SVG files that may have been left behind.
    
    This is called during addon initialization to ensure no accumulation
    of temporary files over time.
    """
    try:
        temp_dir = bpy.utils.extension_path_user(__package__, path="temp", create=False)
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                if filename.startswith("qr_design_") and filename.endswith(".svg"):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        os.unlink(file_path)
                    except Exception:
                        pass  # Ignore errors when cleaning up
    except Exception:
        pass  # Ignore errors if temp directory doesn't exist or can't be accessed


class QRCodeGenerator:
    """
    Handler for generating different types of QR codes and converting them to 3D geometry.

    Supports:
    - Text/URL QR codes for general content
    - WiFi QR codes for network credentials
    - Contact (vCard) QR codes for contact information
    """

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
            if not password:
                security = "nopass"

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
            # segno's make_vcard requires both 'name' and 'displayname' as first two parameters
            qr = helpers.make_vcard(
                name=name,
                displayname=name,
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

        matrix = [list(row) for row in qr_data.matrix]
        qr_size = len(matrix)
        module_size = size / qr_size

        mesh = bpy.data.meshes.new("QR_Code")
        qr_object = bpy.data.objects.new("QR_Code", mesh)
        bpy.context.collection.objects.link(qr_object)

        bm = bmesh.new()

        try:
            for row_idx, row in enumerate(matrix):
                for col_idx, is_dark in enumerate(row):
                    if is_dark:
                        x = (col_idx - qr_size / 2) * module_size
                        y = (row_idx - qr_size / 2) * module_size
                        z = 0

                        # 0.9 scale creates small gaps between modules for better definition
                        bmesh.ops.create_cube(
                            bm,
                            size=module_size * 0.9,
                            matrix=bpy.utils.Matrix.Translation((x, y, z)),
                        )

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
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True

        nodes = material.node_tree.nodes
        nodes.clear()

        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        output = nodes.new(type="ShaderNodeOutputMaterial")

        # Dark, matte material ensures good contrast and scannability
        bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = 0.9

        material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

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

        bbox_corners = [
            qr_object.matrix_world @ vertex.co for vertex in qr_object.bound_box
        ]
        current_size = max(
            max(corner.x for corner in bbox_corners)
            - min(corner.x for corner in bbox_corners),
            max(corner.y for corner in bbox_corners)
            - min(corner.y for corner in bbox_corners),
        )

        if current_size > 0:
            scale_factor = target_size / current_size
            qr_object.scale = (scale_factor, scale_factor, scale_factor)

        qr_object.location = (0, 0, 0)
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

    qr_data = QRCodeGenerator.generate_qr_by_type(qr_type, **qr_params)
    if not qr_data:
        print(f"Failed to generate {qr_type} QR code")
        return None

    qr_object = QRCodeGenerator.create_qr_mesh_from_data(qr_data, size=0.02)
    if not qr_object:
        print("Failed to create QR code mesh")
        return None

    QRCodeGenerator.prepare_qr_for_card(qr_object)
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


class OBJECT_OT_nfc_toggle_qr_mode(Operator):
    """Toggle QR code generation mode for a design slot"""

    bl_idname = "object.nfc_toggle_qr_mode"
    bl_label = "Toggle QR Mode"
    bl_description = "Toggle between SVG import and QR code generation mode"
    bl_options = {"REGISTER", "UNDO"}

    design_num: bpy.props.IntProperty(
        name="Design Number",
        description="Which design slot to toggle (1 or 2)",
        default=1,
        min=1,
        max=2,
    )

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
            if props.qr_mode_1 != self.enable_qr:
                props.has_design_1 = False
        else:
            props.qr_mode_2 = self.enable_qr
            if props.qr_mode_2 != self.enable_qr:
                props.has_design_2 = False

        return {"FINISHED"}


# QR Code Shape Styling Constants
SQUIRCLE_MAGIC_K = 0.85  # Cubic Bézier control point multiplier for super-ellipse approximation
MODULE_SCALE_FACTOR = 0.9  # Scale down modules slightly for visual separation
FINDER_PATTERN_SIZE = 7  # Finder patterns are 7x7 modules
FINDER_CENTER_SIZE = 3  # Finder pattern centers are 3x3 modules
ROUNDED_CORNER_RADIUS = 0.3  # Corner radius for rounded adaptive style (fraction of module size)


class OBJECT_OT_nfc_generate_qr(Operator):
    """Generate a QR code and process it through the SVG pipeline"""

    bl_idname = "object.nfc_generate_qr"
    bl_label = "Generate QR Code"
    bl_description = "Generate a QR code based on the selected type and settings"
    bl_options = {"REGISTER", "UNDO"}

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

    def _get_qr_settings(self, props, design_num: int):
        """Helper to get QR settings for a design slot."""
        if design_num == 1:
            return {
                "qr_type": props.qr_type_1,
                "error_correction": props.qr_error_correction_1,
                "text_content": props.qr_text_content_1,
                "wifi_ssid": props.qr_wifi_ssid_1,
                "wifi_password": props.qr_wifi_password_1,
                "wifi_security": props.qr_wifi_security_1,
                "wifi_hidden": props.qr_wifi_hidden_1,
                "contact_name": props.qr_contact_name_1,
                "contact_phone": props.qr_contact_phone_1,
                "contact_email": props.qr_contact_email_1,
                "contact_url": props.qr_contact_url_1,
                "contact_org": props.qr_contact_org_1,
            }
        else:
            return {
                "qr_type": props.qr_type_2,
                "error_correction": props.qr_error_correction_2,
                "text_content": props.qr_text_content_2,
                "wifi_ssid": props.qr_wifi_ssid_2,
                "wifi_password": props.qr_wifi_password_2,
                "wifi_security": props.qr_wifi_security_2,
                "wifi_hidden": props.qr_wifi_hidden_2,
                "contact_name": props.qr_contact_name_2,
                "contact_phone": props.qr_contact_phone_2,
                "contact_email": props.qr_contact_email_2,
                "contact_url": props.qr_contact_url_2,
                "contact_org": props.qr_contact_org_2,
            }

    def _build_qr_params(self, qr_type: str, settings: dict):
        """Helper to build QR parameters based on type."""
        qr_params = {"error_correction": settings["error_correction"]}

        if qr_type == "TEXT":
            content = settings["text_content"]
            if not content.strip():
                return None, "Please enter text or URL content"
            qr_params["content"] = content

        elif qr_type == "WIFI":
            ssid = settings["wifi_ssid"]
            if not ssid.strip():
                return None, "Please enter WiFi network name (SSID)"
            qr_params.update(
                {
                    "ssid": ssid,
                    "password": settings["wifi_password"],
                    "security": settings["wifi_security"],
                    "hidden": settings["wifi_hidden"],
                }
            )

        elif qr_type == "CONTACT":
            name = settings["contact_name"]
            if not name.strip():
                return None, "Please enter contact name"
            qr_params.update(
                {
                    "name": name,
                    "phone": settings["contact_phone"],
                    "email": settings["contact_email"],
                    "url": settings["contact_url"],
                    "org": settings["contact_org"],
                }
            )

        return qr_params, None

    def execute(self, context):
        """Generate QR code and process it."""
        props = context.scene.nfc_card_props

        settings = self._get_qr_settings(props, self.design_num)
        qr_type = settings["qr_type"]

        qr_params, error_msg = self._build_qr_params(qr_type, settings)
        if error_msg:
            self.report({"ERROR"}, error_msg)
            return {"CANCELLED"}

        qr_code = QRCodeGenerator.generate_qr_by_type(qr_type, **qr_params)
        if not qr_code:
            self.report({"ERROR"}, f"Failed to generate {qr_type} QR code")
            return {"CANCELLED"}

        try:
            # Get extension-specific temp file path for SVG processing
            temp_svg_path = _get_temp_svg_path(self.design_num)

            matrix = [list(row) for row in qr_code.matrix]
            svg_content = self._create_qr_svg(matrix, len(matrix), 1.0)

            with open(temp_svg_path, "w") as f:
                f.write(svg_content)

            from . import svg_import

            success = svg_import.process_svg_to_mesh(
                temp_svg_path, self.design_num, self.report
            )

            if success:
                if self.design_num == 1:
                    props.has_design_1 = True
                else:
                    props.has_design_2 = True
            else:
                self.report({"ERROR"}, "Failed to process QR code SVG")
                return {"CANCELLED"}

            # Clean up temporary SVG file
            try:
                if os.path.exists(temp_svg_path):
                    os.unlink(temp_svg_path)
            except Exception:
                pass

        except Exception as e:
            traceback.print_exc()
            self.report({"ERROR"}, f"Failed to generate QR code: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

    def _create_qr_svg(self, matrix, qr_size: int, module_size: float) -> str:
        """Create SVG content from QR matrix with custom styling."""
        props = bpy.context.scene.nfc_card_props
        
        if self.design_num == 1:
            module_style = props.qr_module_style_1
            finder_style = props.qr_finder_style_1
        else:
            module_style = props.qr_module_style_2
            finder_style = props.qr_finder_style_2
        
        finder_border_style = self._determine_border_style(finder_style)
        svg_width = qr_size * module_size
        svg_height = qr_size * module_size
        finder_positions = self._get_finder_positions(qr_size)
        
        # Pre-analyze neighbors for rounded style (batch operation)
        corner_map = {}
        if module_style == "ROUNDED":
            corner_map = self._analyze_neighbors(matrix)
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
'''
        
        for finder_pos in finder_positions:
            svg_content += self._create_finder_pattern(
                finder_pos, module_size, finder_style, finder_border_style
            )

        for row_idx, row in enumerate(matrix):
            for col_idx, is_dark in enumerate(row):
                if is_dark and not self._is_in_finder_area(row_idx, col_idx, finder_positions):
                    x = col_idx * module_size
                    y = row_idx * module_size
                    
                    # Pass corner info for rounded style
                    corners = corner_map.get((row_idx, col_idx), None)
                    svg_content += self._create_shape(x, y, module_size, module_style, corners)

        svg_content += "</svg>"
        return svg_content
    
    def _determine_border_style(self, finder_style: str) -> str:
        """Determine border style based on finder center style."""
        if finder_style in ("SQUARE", "CIRCLE"):
            return finder_style
        return "SQUIRCLE"
    
    def _get_finder_positions(self, qr_size: int) -> list:
        """Get positions of the three finder patterns."""
        offset = FINDER_PATTERN_SIZE // 2
        return [
            {"row": offset, "col": offset},
            {"row": offset, "col": qr_size - offset - 1},
            {"row": qr_size - offset - 1, "col": offset},
        ]
    
    def _is_in_finder_area(self, row: int, col: int, finder_positions: list) -> bool:
        """Check if a module is within any finder pattern area."""
        half_size = FINDER_PATTERN_SIZE // 2
        for finder in finder_positions:
            if (abs(row - finder["row"]) <= half_size and 
                abs(col - finder["col"]) <= half_size):
                return True
        return False
    
    def _analyze_neighbors(self, matrix) -> dict:
        """Analyze QR matrix to determine which corners should be rounded.
        
        Uses NumPy array slicing for efficient neighbor detection.
        Returns dict mapping (row, col) to rounded corner flags.
        """
        arr = np.array(matrix, dtype=bool)
        height, width = arr.shape
        padded = np.pad(arr, pad_width=1, mode='constant', constant_values=False)
        
        north = padded[:-2, 1:-1]
        south = padded[2:, 1:-1]
        west = padded[1:-1, :-2]
        east = padded[1:-1, 2:]
        
        corners = {}
        filled = np.argwhere(arr)
        
        for row, col in filled:
            round_corners = {
                'tl': not north[row, col] and not west[row, col],
                'tr': not north[row, col] and not east[row, col],
                'br': not south[row, col] and not east[row, col],
                'bl': not south[row, col] and not west[row, col],
            }
            if any(round_corners.values()):
                corners[(row, col)] = round_corners
        
        return corners
    
    def _create_rounded_rect_path(self, x: float, y: float, size: float, 
                                   round_corners: dict) -> str:
        """Create SVG path for rectangle with adaptive rounded corners."""
        r = size * ROUNDED_CORNER_RADIUS
        start_x = x + (r if round_corners['tl'] else 0)
        
        path = f'M {start_x},{y} '
        
        if round_corners['tr']:
            path += f'L {x + size - r},{y} Q {x + size},{y} {x + size},{y + r} '
        else:
            path += f'L {x + size},{y} '
        
        if round_corners['br']:
            path += f'L {x + size},{y + size - r} Q {x + size},{y + size} {x + size - r},{y + size} '
        else:
            path += f'L {x + size},{y + size} '
        
        if round_corners['bl']:
            path += f'L {x + r},{y + size} Q {x},{y + size} {x},{y + size - r} '
        else:
            path += f'L {x},{y + size} '
        
        if round_corners['tl']:
            path += f'L {x},{y + r} Q {x},{y} {x + r},{y} '
        else:
            path += f'L {x},{y} '
        
        path += 'z'
        return path
    
    def _create_squircle_path(self, cx: float, cy: float, size: float) -> str:
        """Generate SVG path for a squircle (super-ellipse)."""
        half = size / 2
        d = half * SQUIRCLE_MAGIC_K
        
        path = f'M {cx},{cy - half} '
        path += f'C {cx + d},{cy - half} {cx + half},{cy - d} {cx + half},{cy} '
        path += f'C {cx + half},{cy + d} {cx + d},{cy + half} {cx},{cy + half} '
        path += f'C {cx - d},{cy + half} {cx - half},{cy + d} {cx - half},{cy} '
        path += f'C {cx - half},{cy - d} {cx - d},{cy - half} {cx},{cy - half} z'
        return path
    
    def _create_finder_pattern(self, finder_pos: dict, module_size: float, 
                                center_style: str, border_style: str) -> str:
        """Create a complete finder pattern as cohesive shapes."""
        row = finder_pos["row"]
        col = finder_pos["col"]
        half_size = FINDER_PATTERN_SIZE // 2
        half_center = FINDER_CENTER_SIZE // 2
        
        center_x = (col - half_center) * module_size
        center_y = (row - half_center) * module_size
        center_size = FINDER_CENTER_SIZE * module_size
        
        border_x = (col - half_size) * module_size
        border_y = (row - half_size) * module_size
        border_outer_size = FINDER_PATTERN_SIZE * module_size
        border_inner_size = (FINDER_PATTERN_SIZE - 2) * module_size
        border_inner_x = border_x + module_size
        border_inner_y = border_y + module_size
        
        svg_content = ""
        
        if border_style == "SQUARE":
            svg_content += '<path fill-rule="evenodd" fill="black" d="'
            svg_content += f'M {border_x},{border_y} h {border_outer_size} v {border_outer_size} h -{border_outer_size} z '
            svg_content += f'M {border_inner_x},{border_inner_y} h {border_inner_size} v {border_inner_size} h -{border_inner_size} z'
            svg_content += '"/>\n'
            
        elif border_style == "CIRCLE":
            cx = border_x + border_outer_size / 2
            cy = border_y + border_outer_size / 2
            outer_r = border_outer_size / 2
            inner_r = border_inner_size / 2
            svg_content += '<path fill-rule="evenodd" fill="black" d="'
            svg_content += f'M {cx - outer_r},{cy} a {outer_r},{outer_r} 0 1,0 {outer_r * 2},0 a {outer_r},{outer_r} 0 1,0 -{outer_r * 2},0 z '
            svg_content += f'M {cx - inner_r},{cy} a {inner_r},{inner_r} 0 1,1 {inner_r * 2},0 a {inner_r},{inner_r} 0 1,1 -{inner_r * 2},0 z'
            svg_content += '"/>\n'
            
        elif border_style == "SQUIRCLE":
            outer_cx = border_x + border_outer_size / 2
            outer_cy = border_y + border_outer_size / 2
            inner_cx = border_inner_x + border_inner_size / 2
            inner_cy = border_inner_y + border_inner_size / 2
            
            svg_content += '<path fill-rule="evenodd" fill="black" d="'
            svg_content += self._create_squircle_path(outer_cx, outer_cy, border_outer_size) + ' '
            svg_content += self._create_squircle_path(inner_cx, inner_cy, border_inner_size)
            svg_content += '"/>\n'
        
        svg_content += self._create_large_shape(center_x, center_y, center_size, center_style)
        
        return svg_content
    
    def _create_large_shape(self, x: float, y: float, size: float, style: str) -> str:
        """Create a shape for finder pattern centers (3x3 area)."""
        cx = x + size / 2
        cy = y + size / 2
        
        if style == "SQUARE":
            return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="black"/>\n'
        elif style == "CIRCLE":
            return f'<circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="black"/>\n'
        elif style == "SQUIRCLE":
            return f'<path fill="black" d="{self._create_squircle_path(cx, cy, size)}"/>\n'
        
        return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="black"/>\n'
    
    def _create_shape(self, x: float, y: float, size: float, style: str, 
                      round_corners: dict = None) -> str:
        """Create an SVG shape for individual QR modules."""
        cx = x + size / 2
        cy = y + size / 2
        
        if style == "SQUARE":
            return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="black"/>\n'
        elif style == "CIRCLE":
            scaled_r = size / 2 * MODULE_SCALE_FACTOR
            return f'<circle cx="{cx}" cy="{cy}" r="{scaled_r}" fill="black"/>\n'
        elif style == "SQUIRCLE":
            scaled_size = size * MODULE_SCALE_FACTOR
            return f'<path fill="black" d="{self._create_squircle_path(cx, cy, scaled_size)}"/>\n'
        elif style == "ROUNDED":
            if round_corners and any(round_corners.values()):
                return f'<path fill="black" d="{self._create_rounded_rect_path(x, y, size, round_corners)}"/>\n'
            else:
                return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="black"/>\n'
        
        return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="black"/>\n'


def register() -> None:
    if not QRCodeGenerator.is_segno_available():
        print(
            "Warning: segno library not available. QR code generation will be disabled."
        )
        print("To enable QR codes, install the segno wheel in the add-on directory.")

    # Clean up any old temporary files from previous sessions
    _cleanup_old_temp_files()

    bpy.utils.register_class(OBJECT_OT_nfc_toggle_qr_mode)
    bpy.utils.register_class(OBJECT_OT_nfc_generate_qr)


def unregister() -> None:
    bpy.utils.unregister_class(OBJECT_OT_nfc_generate_qr)
    bpy.utils.unregister_class(OBJECT_OT_nfc_toggle_qr_mode)
