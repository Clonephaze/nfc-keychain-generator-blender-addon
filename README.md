# NFC Card & Keychain Generator (Blender Add-on)

## Project Overview

This Blender add-on makes it easy to design fully customizable, 3D-printable NFC cards and keychains. Combine practical features like NFC cavities, magnet slots, and QR codes with your own graphics or logos. Ideal for influencers sharing their socials, Wi-Fi share cards, branded giveaways, or just a conversation piece for your fridge.

---

## Features

- **Shape Presets**: Rectangle or circle, with optional keychain loop
- **Flexible Dimensions**: Control size, thickness, corner rounding, and bevel style
- **Smart Cutouts**: Add an NFC slot (card or round tag) and magnet holes (circle or hex, with taper options)
- **Graphics Integration**: Import custom SVG designs or generate QR codes on the fly (Wi-Fi, vCards, URLs, text)
- **Multi-material Ready**: Inset designs for engraving or multi-color printing
- **Live Updates**: All parameters update instantly using Geometry Nodes
- **Export**: One-click STL export for printing

---

## Quickstart

1. Open Blender and enable the add-on
2. In the 3D Viewport sidebar, open the "NFC Cards" tab
3. Click **Prep Scene** to initialize the geometry setup
4. Choose a shape preset, adjust dimensions, and add optional NFC or magnet cutouts
5. Import an SVG logo or generate a QR code in the Design panel
6. Adjust placement, scale, and style of your design
7. Export as STL for 3D printing

---

## Example Uses

- A tap-to-join Wi-Fi card with QR backup for iPhone users
- Custom keychains with your logo, handle, or contact details
- NFC-enabled business cards linking to a portfolio or vCard
- Branded or decorative fridge magnets

---

## Installation

After downloading `nfcCardGen.zip` drap the zip onto blenders window and confirm the addon installation. You can find the addon in the layout tab in the n-panel tab called "NFC Cards"

## Requirements

- Blender 4.2.0 or later
- This addon zip

---

## Advanced: Multi-Color Printing with Orca Slicer

After exporting your STL, you can use [Orca Slicer](https://orcaslicer.com/) to split the model for color assignment:

1. Import the STL into Orca
2. Use "Split to Parts" (NOT "Split to Objects") to separate body and designs, OR you can choose to manually paint the parts yourself and skip to step 5.
3. In the objects menu choose part 2, right click and change type, choose negative part
4. Set object 1 to one color, set objects 3+ to your second color
5. Adjust print settings for filament swaps or multi-material printing, the tool produces default measurements suited for .2 mm increments
6. Slice and preview

Tips:
- Use the "Inset Designs" option in the add-on for clean multi-color regions, flip the card in your slicer for an even cleaner top surface!

---

## License

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

---

## Support & Feedback

For questions, issues, or feature requests, please visit the project repository or contact me at jack@clonecore.net.

