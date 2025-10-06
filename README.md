# 3D-Printable & Customizable Tags, Cards, & Keychains

NFC chips and QR codes are powerful tools – they can share your socials or contact card, let guests tap to join your Wi-Fi, or even trigger automations with a single scan. However on their own, NFC chips don’t look great, and a paper QR code isn’t much better.

This add-on lets you design 3D-printable housings for NFC chips. You can add your own logos or icons (Wi-Fi symbol, social media logo, etc.), or use the built-in QR generator to put a backup code directly on the surface of the print.

---

## Main Features

* **Versatile shapes** – Cards, dots, or keychains with adjustable height, bevels, rounded corners, and optional magnet slots.  
* **SVG support** – Import any SVG logo and turn it into an object on your housing, with the option to inset designs for flush multi-color prints.  
* **QR fallback** – Generate QR codes for links, vCards, Wi-Fi details, or plain text and place them like any other logo.  
* **Magnet slots** – Choose between hexagonal or circular cutouts, set width/height, and let the tool auto-adjust the housing height.  
* **NFC optional** – Disable the NFC cutout to create solid cards or keychains without cavities.  

---

## Quickstart

1. Install and enable the add-on.  
2. Open the **NFC Cards** tab in the N-panel (press `N` in the 3D Viewport).  
3. Click **Prep Scene** to generate the base card and clear any interfering objects.  
4. Choose shape, dimensions, and optional NFC or magnet cutouts.  
5. Import an SVG logo or generate a QR code, adjusting scale and offsets as needed.  
6. Export your customized housing as an STL ready for printing.  

---

## Multi-Color Printing & NFC Slot Setup in Orca Slicer

1. Import the STL into Orca.  
2. Right click the object > Split > to Parts (*not* to Objects).  
3. In the left panel, open the **Objects** tab (next to **Process**). You’ll see a list of numbered objects.  
4. Right click object 2 > Change Type > set to Negative Object.  
5. For objects 3 and up, right click > Change Filament Type > assign your second color.  
   - Optional: If the design is inset, flip the STL 180° for a cleaner top surface.  
6. Slice and scrub the slider to the layer just before the NFC cavity gets covered. Right click > Add Pause.  
7. Re-slice and save/send g-code to your printer.  

---

## Requirements & Manual Installation

You need:  
* Blender 4.2.0 or later  

Manual install:  
* Download `nfcCardGen.zip`.  
* Drag and drop it into Blender, then enable the extension.  
* Or go to **Edit > Preferences > Add-ons > Install from Disk**, select the zip, and enable it.  

---

## License

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

---

## Support & Feedback

For questions, issues, or feature requests, please open an issue in the project repository or contact me at **jack@clonecore.net**.
