"""
QR Code generation functionality for the NFC Card & Keychain Generator.

This module handles generating different types of QR codes using the segno library:
- Text/URL QR codes for general content
- WiFi QR codes for network sharing
- Contact (vCard) QR codes for contact information
- Email QR codes for pre-filled email messages
"""

import math
import traceback
from typing import Optional

import numpy as np

import bmesh
import bpy
from bpy.types import Object, Operator
from mathutils import Matrix

try:
    import segno
    from segno import helpers

    # print(f"[NFC Addon] Segno loaded: {segno.__version__}")
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
    - Email QR codes for pre-filled email messages
    """

    QR_TYPE_TEXT = "TEXT"
    QR_TYPE_WIFI = "WIFI"
    QR_TYPE_CONTACT = "CONTACT"
    QR_TYPE_EMAIL = "EMAIL"

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
            # Validate content length to prevent impractically large QR codes
            if len(content) > 2000:
                print(f"QR content too long ({len(content)} chars, max 2000).")
                return None

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

            # Use _data helper to get content string, then create QR with custom error correction
            wifi_data = helpers.make_wifi_data(
                ssid=ssid, password=password, security=security, hidden=hidden
            )
            qr = segno.make(wifi_data, error=error_correction)
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
            # Use _data helper to get vCard string, then create QR with custom error correction
            vcard_data = helpers.make_vcard_data(
                name=name,
                displayname=name,
                phone=phone or None,
                email=email or None,
                url=url or None,
                org=org or None,
            )
            qr = segno.make(vcard_data, error=error_correction)
            return qr
        except Exception as e:
            print(f"Contact QR code generation failed: {e}")
            return None

    @classmethod
    def generate_email_qr(
        cls,
        to: str,
        cc: str = "",
        bcc: str = "",
        subject: str = "",
        body: str = "",
        error_correction: str = "M",
    ) -> Optional[segno.QRCode]:
        """
        Generate an email QR code using segno's email helper.

        Args:
            to: The email address (recipient).
            cc: The carbon copy recipient (optional).
            bcc: The blind carbon copy recipient (optional).
            subject: The email subject (optional).
            body: The message body (optional).
            error_correction: Error correction level ('L', 'M', 'Q', 'H').

        Returns:
            Email QR code object, or None if generation failed.
        """
        if not cls.is_segno_available():
            return None

        try:
            # Convert empty strings to None for optional parameters
            cc_list = cc.split(",") if cc.strip() else None
            bcc_list = bcc.split(",") if bcc.strip() else None

            # Clean up email lists by stripping whitespace
            if cc_list:
                cc_list = [email.strip() for email in cc_list if email.strip()]
                cc_list = cc_list if cc_list else None

            if bcc_list:
                bcc_list = [email.strip() for email in bcc_list if email.strip()]
                bcc_list = bcc_list if bcc_list else None

            # Use _data helper to get mailto string, then create QR with custom error correction
            email_data = helpers.make_make_email_data(
                to=to,
                cc=cc_list,
                bcc=bcc_list,
                subject=subject or None,
                body=body or None,
            )
            qr = segno.make(email_data, error=error_correction)
            return qr
        except Exception as e:
            print(f"Email QR code generation failed: {e}")
            return None

    @classmethod
    def generate_qr_by_type(cls, qr_type: str, **kwargs) -> Optional[segno.QRCode]:
        """
        Generate QR code based on type with appropriate parameters.

        Args:
            qr_type: Type of QR code ('TEXT', 'WIFI', 'CONTACT', 'EMAIL').
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
        elif qr_type == cls.QR_TYPE_EMAIL:
            return cls.generate_email_qr(
                to=kwargs.get("to", ""),
                cc=kwargs.get("cc", ""),
                bcc=kwargs.get("bcc", ""),
                subject=kwargs.get("subject", ""),
                body=kwargs.get("body", ""),
                error_correction=kwargs.get("error_correction", "M"),
            )
        else:
            print(f"Unknown QR code type: {qr_type}")
            return None

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
            was_qr = props.qr_mode_1
            props.qr_mode_1 = self.enable_qr
            if was_qr != self.enable_qr:
                props.has_design_1 = False
        else:
            was_qr = props.qr_mode_2
            props.qr_mode_2 = self.enable_qr
            if was_qr != self.enable_qr:
                props.has_design_2 = False

        return {"FINISHED"}


# QR Code Shape Styling Constants
SQUIRCLE_MAGIC_K = (
    0.85  # Cubic Bézier control point multiplier for super-ellipse approximation
)
MODULE_SCALE_FACTOR = 0.9  # Scale down modules slightly for visual separation
FINDER_PATTERN_SIZE = 7  # Finder patterns are 7x7 modules
FINDER_CENTER_SIZE = 3  # Finder pattern centers are 3x3 modules
ROUNDED_CORNER_RADIUS = (
    0.3  # Corner radius for rounded adaptive style (fraction of module size)
)

# Direct BMesh QR construction constants
CIRCLE_SEGMENTS = 32       # polygon segments for circle approximation
BEZIER_SAMPLES = 8         # samples per cubic-Bézier quarter-arc (32 verts/squircle)
CORNER_ARC_SAMPLES = 6     # samples per quadratic-Bézier rounded corner
QR_EXTRUDE_HEIGHT = 0.6    # mm – extrusion thickness for QR modules
QR_TARGET_SIZE = 40.0      # mm – final QR mesh scaled to fit this dimension
ROUNDED_MERGE_DIST = 0.0001  # vertex merge distance for ROUNDED blob welding


# ---------------------------------------------------------------------------
#  Geometry helpers – polygon vertex generators & BMesh extrusion utilities
# ---------------------------------------------------------------------------

def _cubic_bezier(p0, p1, p2, p3, t):
    """Evaluate cubic Bézier at parameter *t* ∈ [0, 1]."""
    u = 1.0 - t
    return (
        u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
        u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1],
    )


def _quadratic_bezier(p0, p1, p2, t):
    """Evaluate quadratic Bézier at parameter *t* ∈ [0, 1]."""
    u = 1.0 - t
    return (
        u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
        u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1],
    )


def _square_verts(
    cx: float, cy: float, half: float,
) -> list[tuple[float, float]]:
    """CCW square vertices centred at (*cx*, *cy*)."""
    return [
        (cx - half, cy - half),
        (cx + half, cy - half),
        (cx + half, cy + half),
        (cx - half, cy + half),
    ]


def _circle_verts(
    cx: float, cy: float, radius: float,
    segments: int = CIRCLE_SEGMENTS,
) -> list[tuple[float, float]]:
    """CCW regular polygon approximating a circle."""
    tau = 2.0 * math.pi
    return [
        (cx + radius * math.cos(tau * i / segments),
         cy + radius * math.sin(tau * i / segments))
        for i in range(segments)
    ]


def _squircle_verts(
    cx: float, cy: float, size: float,
    samples: int = BEZIER_SAMPLES,
) -> list[tuple[float, float]]:
    """Super-ellipse (squircle) vertices via cubic-Bézier sampling."""
    half = size / 2.0
    d = half * SQUIRCLE_MAGIC_K
    # Four Bézier quarter-arcs starting at top, going clockwise
    curves = [
        ((cx, cy - half), (cx + d, cy - half), (cx + half, cy - d), (cx + half, cy)),
        ((cx + half, cy), (cx + half, cy + d), (cx + d, cy + half), (cx, cy + half)),
        ((cx, cy + half), (cx - d, cy + half), (cx - half, cy + d), (cx - half, cy)),
        ((cx - half, cy), (cx - half, cy - d), (cx - d, cy - half), (cx, cy - half)),
    ]
    verts: list[tuple[float, float]] = []
    for p0, p1, p2, p3 in curves:
        for i in range(samples):
            verts.append(_cubic_bezier(p0, p1, p2, p3, i / samples))
    return verts


def _rounded_rect_verts(
    x: float, y: float, size: float, round_corners: dict,
    r_frac: float = ROUNDED_CORNER_RADIUS,
    arc_n: int = CORNER_ARC_SAMPLES,
) -> list[tuple[float, float]]:
    """Rectangle with selectively rounded corners.

    *x*, *y* is the top-left corner of the bounding square.
    *round_corners* maps ``'tl'``, ``'tr'``, ``'br'``, ``'bl'`` → bool.
    """
    r = size * r_frac
    verts: list[tuple[float, float]] = []

    # Start at top-left
    if round_corners.get("tl"):
        verts.append((x + r, y))
    else:
        verts.append((x, y))

    # Top-right corner
    if round_corners.get("tr"):
        p0, p1, p2 = (x + size - r, y), (x + size, y), (x + size, y + r)
        verts.append(p0)
        for i in range(1, arc_n + 1):
            verts.append(_quadratic_bezier(p0, p1, p2, i / arc_n))
    else:
        verts.append((x + size, y))

    # Bottom-right corner
    if round_corners.get("br"):
        p0 = (x + size, y + size - r)
        p1 = (x + size, y + size)
        p2 = (x + size - r, y + size)
        verts.append(p0)
        for i in range(1, arc_n + 1):
            verts.append(_quadratic_bezier(p0, p1, p2, i / arc_n))
    else:
        verts.append((x + size, y + size))

    # Bottom-left corner
    if round_corners.get("bl"):
        p0 = (x + r, y + size)
        p1 = (x, y + size)
        p2 = (x, y + size - r)
        verts.append(p0)
        for i in range(1, arc_n + 1):
            verts.append(_quadratic_bezier(p0, p1, p2, i / arc_n))
    else:
        verts.append((x, y + size))

    # Top-left corner (closing arc)
    if round_corners.get("tl"):
        p0 = (x, y + r)
        p1 = (x, y)
        p2 = (x + r, y)
        verts.append(p0)
        for i in range(1, arc_n):  # exclude last – coincides with start vertex
            verts.append(_quadratic_bezier(p0, p1, p2, i / arc_n))

    return verts


def _shape_verts_for_style(
    cx: float, cy: float, size: float, style: str,
) -> list[tuple[float, float]]:
    """Return polygon vertices for a shape *style* (no module scale applied)."""
    half = size / 2.0
    if style == "SQUARE":
        return _square_verts(cx, cy, half)
    if style == "CIRCLE":
        return _circle_verts(cx, cy, half)
    if style == "SQUIRCLE":
        return _squircle_verts(cx, cy, size)
    return _square_verts(cx, cy, half)  # fallback


def _module_verts_for_style(
    cx: float, cy: float, size: float, style: str,
    round_corners: dict | None = None,
) -> list[tuple[float, float]]:
    """Return polygon vertices for a single QR module with MODULE_SCALE_FACTOR gap."""
    scaled = size * MODULE_SCALE_FACTOR
    half_s = scaled / 2.0
    if style == "SQUARE":
        return _square_verts(cx, cy, half_s)
    if style == "CIRCLE":
        return _circle_verts(cx, cy, half_s)
    if style == "SQUIRCLE":
        return _squircle_verts(cx, cy, scaled)
    if style == "ROUNDED":
        if round_corners and any(round_corners.values()):
            return _rounded_rect_verts(
                cx - half_s, cy - half_s, scaled, round_corners,
            )
        return _square_verts(cx, cy, half_s)
    return _square_verts(cx, cy, half_s)  # fallback


def _create_flat_face(
    bm: bmesh.types.BMesh,
    verts_2d: list[tuple[float, float]],
    z: float = 0.0,
) -> None:
    """Create a single flat face at height *z* from 2-D polygon vertices."""
    n = len(verts_2d)
    if n < 3:
        return
    bm.faces.new([bm.verts.new((x, y, z)) for x, y in verts_2d])


def _extrude_polygon(
    bm: bmesh.types.BMesh,
    verts_2d: list[tuple[float, float]],
    z_bot: float = 0.0,
    z_top: float = QR_EXTRUDE_HEIGHT,
) -> None:
    """Create a closed extruded solid from a 2-D polygon outline.

    Builds bottom face, top face and side quads – guaranteed manifold when
    the polygon is non-self-intersecting.
    """
    n = len(verts_2d)
    if n < 3:
        return
    bot = [bm.verts.new((x, y, z_bot)) for x, y in verts_2d]
    top = [bm.verts.new((x, y, z_top)) for x, y in verts_2d]
    # Bottom face – reversed winding so normal points −Z
    bm.faces.new(bot[::-1])
    # Top face – normal points +Z
    bm.faces.new(top)
    # Side quads
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([bot[i], bot[j], top[j], top[i]])


def _extrude_ring(
    bm: bmesh.types.BMesh,
    outer: list[tuple[float, float]],
    inner: list[tuple[float, float]],
    z_bot: float = 0.0,
    z_top: float = QR_EXTRUDE_HEIGHT,
) -> None:
    """Create a closed extruded annular ring (outer shell with inner hole).

    Both polygons must have the **same** vertex count and consistent winding.
    """
    n = len(outer)
    if n < 3 or len(inner) != n:
        return
    ob = [bm.verts.new((x, y, z_bot)) for x, y in outer]
    ot = [bm.verts.new((x, y, z_top)) for x, y in outer]
    ib = [bm.verts.new((x, y, z_bot)) for x, y in inner]
    it_ = [bm.verts.new((x, y, z_top)) for x, y in inner]
    for i in range(n):
        j = (i + 1) % n
        # Top annular quad
        bm.faces.new([ot[i], ot[j], it_[j], it_[i]])
        # Bottom annular quad (reversed winding)
        bm.faces.new([ob[j], ob[i], ib[i], ib[j]])
        # Outer side face
        bm.faces.new([ob[i], ob[j], ot[j], ot[i]])
        # Inner side face (inward-pointing normal)
        bm.faces.new([ib[j], ib[i], it_[i], it_[j]])


class OBJECT_OT_nfc_generate_qr(Operator):
    """Generate a QR code and build it directly as manifold BMesh geometry"""

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
        s = str(design_num)
        return {
            "qr_type": getattr(props, f"qr_type_{s}"),
            "error_correction": getattr(props, f"qr_error_correction_{s}"),
            "text_content": getattr(props, f"qr_text_content_{s}"),
            "wifi_ssid": getattr(props, f"qr_wifi_ssid_{s}"),
            "wifi_password": getattr(props, f"qr_wifi_password_{s}"),
            "wifi_security": getattr(props, f"qr_wifi_security_{s}"),
            "wifi_hidden": getattr(props, f"qr_wifi_hidden_{s}"),
            "contact_name": getattr(props, f"qr_contact_name_{s}"),
            "contact_phone": getattr(props, f"qr_contact_phone_{s}"),
            "contact_email": getattr(props, f"qr_contact_email_{s}"),
            "contact_url": getattr(props, f"qr_contact_url_{s}"),
            "contact_org": getattr(props, f"qr_contact_org_{s}"),
            "email_to": getattr(props, f"qr_email_to_{s}"),
            "email_cc": getattr(props, f"qr_email_cc_{s}"),
            "email_bcc": getattr(props, f"qr_email_bcc_{s}"),
            "email_subject": getattr(props, f"qr_email_subject_{s}"),
            "email_body": getattr(props, f"qr_email_body_{s}"),
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

        elif qr_type == "EMAIL":
            to_email = settings["email_to"]
            if not to_email.strip():
                return None, "Please enter recipient email address"
            qr_params.update(
                {
                    "to": to_email,
                    "cc": settings["email_cc"],
                    "bcc": settings["email_bcc"],
                    "subject": settings["email_subject"],
                    "body": settings["email_body"],
                }
            )

        return qr_params, None

    def execute(self, context):
        """Generate QR code, build it as direct BMesh geometry, and connect to nodes."""
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
            matrix = [list(row) for row in qr_code.matrix]
            qr_size = len(matrix)

            # Read style settings for this design slot
            if self.design_num == 1:
                module_style = props.qr_module_style_1
                finder_style = props.qr_finder_style_1
            else:
                module_style = props.qr_module_style_2
                finder_style = props.qr_finder_style_2

            # Border shape matches the finder center style
            finder_border_style = finder_style

            # Build mesh directly via BMesh – no SVG intermediary
            design_obj = self._build_qr_mesh(
                matrix, qr_size, module_style, finder_style, finder_border_style,
            )
            if not design_obj:
                self.report({"ERROR"}, "Failed to build QR code mesh")
                return {"CANCELLED"}

            # Connect to geometry-node setup
            from . import svg_import

            logo_placer = svg_import._find_logo_placer_node_group()
            if not logo_placer:
                bpy.data.objects.remove(design_obj, do_unlink=True)
                self.report(
                    {"ERROR"},
                    "Logo Placer node group not found. Ensure the scene is set up.",
                )
                return {"CANCELLED"}

            design_input = svg_import._find_design_input_node(
                logo_placer, self.design_num,
            )
            if not design_input:
                bpy.data.objects.remove(design_obj, do_unlink=True)
                self.report({"ERROR"}, "Design input node not found.")
                return {"CANCELLED"}

            design_input.inputs[0].default_value = design_obj
            design_obj.hide_viewport = True

            if self.design_num == 1:
                props.has_design_1 = True
            else:
                props.has_design_2 = True

        except Exception as e:
            traceback.print_exc()
            self.report({"ERROR"}, f"Failed to generate QR code: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

    # ------------------------------------------------------------------
    #  QR matrix analysis helpers
    # ------------------------------------------------------------------

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
            if (
                abs(row - finder["row"]) <= half_size
                and abs(col - finder["col"]) <= half_size
            ):
                return True
        return False

    def _analyze_neighbors(self, matrix) -> dict:
        """Analyze QR matrix to determine which corners should be rounded.

        Uses NumPy array slicing for efficient neighbor detection.
        Returns dict mapping (row, col) to rounded corner flags.
        """
        arr = np.array(matrix, dtype=bool)
        height, width = arr.shape
        padded = np.pad(arr, pad_width=1, mode="constant", constant_values=False)

        north = padded[:-2, 1:-1]
        south = padded[2:, 1:-1]
        west = padded[1:-1, :-2]
        east = padded[1:-1, 2:]

        corners = {}
        filled = np.argwhere(arr)

        for row, col in filled:
            round_corners = {
                "tl": not north[row, col] and not west[row, col],
                "tr": not north[row, col] and not east[row, col],
                "br": not south[row, col] and not east[row, col],
                "bl": not south[row, col] and not west[row, col],
            }
            if any(round_corners.values()):
                corners[(row, col)] = round_corners

        return corners

    # ------------------------------------------------------------------
    #  Direct BMesh QR mesh construction
    # ------------------------------------------------------------------

    def _build_qr_mesh(
        self, matrix, qr_size: int,
        module_style: str, finder_style: str, finder_border_style: str,
    ) -> Optional[Object]:
        """Build the full QR code as a manifold mesh directly in BMesh.

        For SQUARE / CIRCLE / SQUIRCLE each module is independently extruded
        with a MODULE_SCALE_FACTOR gap – guaranteed manifold by construction.

        For ROUNDED the modules are placed at full size so adjacent dark
        cells merge into continuous blobs with only the exposed corners
        rounded.  The flat faces are welded, extruded as one, then cleaned.
        """
        module_size = QR_TARGET_SIZE / qr_size
        finder_positions = self._get_finder_positions(qr_size)

        mesh = bpy.data.meshes.new(f"QR_Design_{self.design_num}")
        obj = bpy.data.objects.new(f"Design_{self.design_num}_QR", mesh)
        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()
        try:
            if module_style == "ROUNDED":
                self._build_rounded_blobs(
                    bm, matrix, qr_size, module_size, finder_positions,
                )
            else:
                # --- per-module extrusion (SQUARE / CIRCLE / SQUIRCLE) ---
                for row_idx, row in enumerate(matrix):
                    for col_idx, is_dark in enumerate(row):
                        if not is_dark:
                            continue
                        if self._is_in_finder_area(
                            row_idx, col_idx, finder_positions,
                        ):
                            continue
                        cx = (col_idx - qr_size / 2 + 0.5) * module_size
                        cy = (row_idx - qr_size / 2 + 0.5) * module_size
                        verts = _module_verts_for_style(
                            cx, cy, module_size, module_style, None,
                        )
                        _extrude_polygon(bm, verts)

            # --- finder patterns (border ring + centre fill) ---
            for fp in finder_positions:
                self._build_finder_bmesh(
                    bm, fp, module_size, qr_size,
                    finder_style, finder_border_style,
                )

            # Centre origin in Z so the mesh spans −height/2 … +height/2
            z_offset = -QR_EXTRUDE_HEIGHT / 2.0
            bmesh.ops.transform(
                bm,
                matrix=Matrix.Translation((0, 0, z_offset)),
                verts=bm.verts,
            )

            # Ensure consistent outward normals
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            mesh.update()

        except Exception:
            bpy.data.objects.remove(obj, do_unlink=True)
            raise
        finally:
            bm.free()

        return obj

    def _build_rounded_blobs(
        self, bm, matrix, qr_size: int, module_size: float,
        finder_positions: list,
    ) -> None:
        """Build ROUNDED-style data modules as continuous merged blobs.

        1. Place each dark module as a **full-size** rounded-rect flat face
           (corners without cardinal neighbours are rounded, others are sharp).
        2. Weld coincident vertices so adjacent modules share edges.
        3. Extrude the connected flat mesh upward.
        4. Clean up interior faces and recalculate normals.
        """
        corner_map = self._analyze_neighbors(matrix)
        half = module_size / 2.0

        # --- lay down flat faces at z = 0 ---------------------------------
        for row_idx, row in enumerate(matrix):
            for col_idx, is_dark in enumerate(row):
                if not is_dark:
                    continue
                if self._is_in_finder_area(row_idx, col_idx, finder_positions):
                    continue

                cx = (col_idx - qr_size / 2 + 0.5) * module_size
                cy = (row_idx - qr_size / 2 + 0.5) * module_size

                corners = corner_map.get((row_idx, col_idx))
                if corners and any(corners.values()):
                    verts = _rounded_rect_verts(
                        cx - half, cy - half, module_size, corners,
                    )
                else:
                    verts = _square_verts(cx, cy, half)
                _create_flat_face(bm, verts)

        # --- merge shared edges between adjacent modules ------------------
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=ROUNDED_MERGE_DIST)

        # --- extrude the connected flat faces upward ----------------------
        faces = bm.faces[:]
        extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
        ext_verts = [
            v for v in extruded["geom"] if isinstance(v, bmesh.types.BMVert)
        ]
        bmesh.ops.transform(
            bm,
            matrix=Matrix.Translation((0, 0, QR_EXTRUDE_HEIGHT)),
            verts=ext_verts,
        )

        # --- clean up coplanar faces & duplicate verts --------------------
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=0.085,
            verts=bm.verts,
            edges=bm.edges,
            delimit={"NORMAL"},
        )
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=ROUNDED_MERGE_DIST)

        # --- remove interior faces created by the extrude -----------------
        from .svg_import import _select_interior_faces

        interior = _select_interior_faces(bm)
        if interior:
            bmesh.ops.delete(bm, geom=interior, context="FACES")

        # Second dissolve pass + normals
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=0.085,
            use_dissolve_boundaries=False,
            verts=bm.verts,
            edges=bm.edges,
            delimit={"NORMAL"},
        )
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def _build_finder_bmesh(
        self, bm, finder_pos: dict, module_size: float, qr_size: int,
        center_style: str, border_style: str,
    ) -> None:
        """Add one finder pattern (border ring + centre fill) to *bm*."""
        fcx = (finder_pos["col"] - qr_size / 2 + 0.5) * module_size
        fcy = (finder_pos["row"] - qr_size / 2 + 0.5) * module_size

        outer_size = FINDER_PATTERN_SIZE * module_size   # 7 modules
        inner_size = (FINDER_PATTERN_SIZE - 2) * module_size  # 5 modules
        center_size = FINDER_CENTER_SIZE * module_size    # 3 modules

        # Border ring – same style for outer and inner ensures equal vertex count
        outer_v = _shape_verts_for_style(fcx, fcy, outer_size, border_style)
        inner_v = _shape_verts_for_style(fcx, fcy, inner_size, border_style)
        _extrude_ring(bm, outer_v, inner_v)

        # Centre fill
        center_v = _shape_verts_for_style(fcx, fcy, center_size, center_style)
        _extrude_polygon(bm, center_v)


def register() -> None:
    if not QRCodeGenerator.is_segno_available():
        print(
            "Warning: segno library not available. QR code generation will be disabled."
        )
        print("To enable QR codes, install the segno wheel in the add-on directory.")

    bpy.utils.register_class(OBJECT_OT_nfc_toggle_qr_mode)
    bpy.utils.register_class(OBJECT_OT_nfc_generate_qr)


def unregister() -> None:
    bpy.utils.unregister_class(OBJECT_OT_nfc_generate_qr)
    bpy.utils.unregister_class(OBJECT_OT_nfc_toggle_qr_mode)
