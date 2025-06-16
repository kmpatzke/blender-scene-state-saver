# Changelog

All notable changes to the Scene State Saver plugin will be documented in this file.

## [2.0] - 2025-06-16

### Added
- Complete rewrite with improved architecture
- Auto-cleanup compatibility for robust state management
- Undo support for all operations (`bl_options = {'REGISTER', 'UNDO'}`)
- Enhanced visibility state management (viewport, render, select, collection)
- Improved error handling and user feedback
- Comprehensive documentation in English and German
- Extensive testing suite with performance metrics

### Changed
- Improved N-Panel interface with better organization
- Better state management with separate "Save New" and "Update" operations
- Enhanced JSON data structure for better compatibility
- More robust object identification and handling

### Fixed
- Visibility state restoration now works correctly
- Better handling of missing or deleted objects
- Improved state selection and management
- Fixed registration/unregistration issues

### Technical Improvements
- Performance optimization (<1ms for 23+ objects)
- Better memory management
- Improved code structure and documentation
- Enhanced error handling and edge case management

## [1.0] - Initial Version

### Added
- Basic save/load functionality
- Simple N-Panel interface
- Transform data storage (location, rotation, scale)
- Basic visibility state management
- Multiple states support

### Known Issues in v1.0
- Limited visibility state support
- No undo functionality
- Basic error handling
- Performance not optimized

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Future Versions

### Planned for v2.1
- Object recreation for deleted objects
- Extended property support (materials, modifiers)
- State categories and tags

### Planned for v3.0
- Import/export functionality
- Automatic snapshots
- State comparison tools
- Advanced filtering options