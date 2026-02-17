# Changelog
## [1.2.0]

### Added
- 3MF export with per-face material colours for multi-colour slicing in Orca Slicer / BambuStudio / PrusaSlicer
- Automatic detection of the ThreeMF-io extension (soft dependency — 3MF option only shown when installed)
- Export format toggle in the UI (3MF / STL) with info text explaining 3MF benefits
- Boolean solver choice (Exact / Fast) for design boolean operations in the UI
- Diagnostic error reporting for SVG-to-mesh pipeline failures (logo placer node group, design input node, assignment errors)

### Fixed
- NFC cavity choice modifier sync error on file reload ("Could not sync 1 modifier values: NFC_CAVITY_CHOICE")
- QR mode toggle not resetting the design flag when switching between QR and SVG modes
- ROUNDED QR module style rendering incorrectly
- SVG import now extrudes each path individually before joining, producing correct geometry for multi-path designs
- Boolean self-union applied to imported SVG meshes to resolve overlapping shell issues
- QR code mesh Z-origin now centred for proper card placement

### Changed
- QR code generation rewritten to use direct BMesh construction instead of SVG intermediary
- SVG import pipeline dramatically faster — per-path extrusion and manifold-making now completes most tested designs in under a second
- Modifier-to-property sync rewritten with dictionary-based enum conversion for robustness

## [1.1.8]
### Optimized
- Reduced .blend file size by using Quick Asset Saver Add-on for saving the card to a clean small asset file. 
- AppendInfo.blend goes from 5.4mb to 378kb
- Backed up the original .blend file to originalcard.blend, used QuickAssetSaver Add-on to save the card in a much smaller library file. 

### Added
- Text overlay support for Design 1 and Design 2
- Custom font loading for both designs (.ttf and .otf support)
- Comprehensive text controls: size, character/word/line spacing
- Text box dimension controls (width and height)
- Text positioning with X/Y offset controls
- Collapsible text panels in UI for clean organization
- Cross-platform font file browser integration

## [1.1.7] 

### Added
- Viewport camera control operators for better workflow
- Automatic viewport positioning on scene setup (top angle view)
- Quick view presets: Full, Top, Top Angle, Bottom, Side, and Side X-Ray views
- X-ray toggle option for transparent viewing of internal features

### Changed
- Refactored view switching logic to use match-case statements (Python 3.10+)
- Improved viewport framing calculations for better object visibility
- Enhanced user experience with automatic camera positioning

### Fixed
- Viewport not centering on card object after setup
- View distance calculations for proper object framing

## [1.1.6]

### Added
- Base shapes: cards and circles with keychain loop options
- Configurable dimensions with rounded corners
- NFC cavity shapes: rectangle, circle, and double circle
- Magnet hole cutouts with hexagon and circle options
- Taper control for easier 3D printing
- Edge beveling with adjustable segments
- Logo/QR code placement workflows

### Features
- SVG import pipeline for custom graphics
- Built-in QR code generation using Segno library
- Geometry Nodes-based parametric design
- Real-time preview updates
- STL export functionality

### Technical
- Blender 4.2.0+ compatibility
- Python 3.10+ requirement
- Geometry Nodes and modifier-based architecture

---

## Version History

- **[1.2.0]** - Boolean solver UI, QR BMesh rewrite, dead code cleanup, bug fixes
- **[1.1.8]** - .blend file size optimization
- **[1.1.7]** - Viewport camera controls and automation
- **[1.1.6]** - Core functionality and features