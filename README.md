# Scene State Saver - Blender Plugin

A powerful Blender addon for saving and restoring complete scene states including object transforms and visibility settings.

## 🎯 Features

### ✅ Complete Scene State Management
- **Save scene states** with all object transforms (location, rotation, scale)
- **Full visibility support** including Eye-Button visibility (`hide_set()`)
- **Viewport and render visibility** preservation
- **Automatic state management** with active state tracking

### ✅ Native Blender UI Integration
- **Native Blender UIList** with professional blue selection bars
- **Radio button indicators** for active states
- **Seamless N-Panel integration** in the Scene States tab
- **Intuitive user experience** matching Blender's design standards

### ✅ Robust Data Management
- **JSON-based storage** alongside your .blend files
- **Automatic file management** with blend file association
- **Error handling** and user feedback
- **Performance optimization** for large scenes

## 🚀 Installation

1. **Download** the `scene_state_saver.py` file
2. **Open Blender** and go to `Edit > Preferences > Add-ons`
3. **Click "Install..."** and select the downloaded file
4. **Enable** the "Scene State Saver" addon
5. **Find the panel** in the N-Panel under "Scene States"

## 📖 Usage

### Creating States
1. **Arrange your scene** with desired object positions and visibility
2. **Enter a state name** in the "Create New State" section
3. **Click "Save State"** to capture the current scene

### Loading States
1. **Select a state** from the list using the native Blender UIList
2. **Click "Load"** to restore the scene to that state
3. **Active states** are indicated with filled radio buttons (●)

### Managing States
- **Update**: Overwrite an existing state with current scene data
- **Delete**: Remove a state permanently (with confirmation dialog)
- **Auto-refresh**: List updates automatically after operations

## 🔧 Technical Details

### Supported Data
- **Object Transforms**: Location, rotation, scale
- **Viewport Visibility**: `hide_viewport` property
- **Render Visibility**: `hide_render` property  
- **Eye-Button Visibility**: `hide_set()` status (complete visibility control)

### File Structure
States are saved as JSON files alongside your .blend file:
```
my_project.blend
my_project_states.json
```

### Compatibility
- **Blender Version**: 3.0+ (tested with 4.4)
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Scene Types**: All scene types supported

## 🎨 User Interface

The addon provides a clean, native Blender interface:

```
┌─ Create New State ─┐
│ Name: [State Name] │
│ [Save State]       │
└────────────────────┘
┌─ Saved States ─────┐
│ ┌────────────────┐ │
│ │ ○ State 1      │ │
│ │ ● State 2      │ │ ← Active state (blue selection)
│ │ ○ State 3      │ │
│ └────────────────┘ │
│ [Load] [Update] [Delete] │
└────────────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

GPL-3.0 - This plugin is free and open source.

---

**Made with ❤️ for the Blender community**
