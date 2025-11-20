# Changelog
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

- **[1.2.0]** - Text overlay and custom font support
- **[1.1.8]** - .blend file size optimization
- **[1.1.7]** - Viewport camera controls and automation
- **[1.1.6]** - Core functionality and features