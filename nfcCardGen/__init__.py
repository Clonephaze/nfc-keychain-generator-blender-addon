"""
NFC Card & Keychain Generator Add-on for Blender 4.2+

An add-on for generating customizable 3D-printable cards, tags, and keychains
using Geometry Nodes and modifiers for maximum flexibility.
"""

from . import (
    operators,
    properties,
    qr_generator,
    svg_import,
    ui_panels,
)

_modules = [
    operators,
    properties,
    qr_generator,
    svg_import,
    ui_panels,
]


def register() -> None:
    for module in _modules:
        if hasattr(module, "register"):
            module.register()


def unregister() -> None:
    for module in reversed(_modules):
        if hasattr(module, "unregister"):
            module.unregister()
