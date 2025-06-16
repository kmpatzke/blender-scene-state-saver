# Scene State Saver - Blender Plugin Development

## Project Overview / Projektübersicht

**English:**
A Blender addon that allows users to save, load, update and delete scene states. Each state captures the position, rotation, scale, viewport visibility and render visibility of all objects in the scene.

**Deutsch:**
Ein Blender-Addon, das es Nutzern ermöglicht, Szenen-Zustände zu speichern, zu laden, zu aktualisieren und zu löschen. Jeder Zustand erfasst Position, Rotation, Skalierung, Viewport-Sichtbarkeit und Render-Sichtbarkeit aller Objekte in der Szene.

## Technical Requirements / Technische Anforderungen

- **UI Location:** N-Panel Tab
- **Storage:** JSON file in project directory (one per .blend file)
- **Prerequisite:** .blend file must be saved before creating states
- **Data Stored per Object:**
  - Position (Location)
  - Rotation
  - Scale
  - Viewport Visibility (hide_viewport)
  - Render Visibility (hide_render)
- **Scope:** Individual objects only (no collections)
- **Error Handling:** Missing objects ignored with console warning
- **Performance:** Warning for 100+ objects, but continue processing
- **UI Style:** Compact list with state names only
- **Auto-Save:** Manual save only
- **Cross-File:** No import/export between .blend files

## Development Plan / Entwicklungsplan

### Phase 1: Foundation / Grundlagen
**Status:** 🔄 In Progress

### Phase 2: Core Functionality / Kernfunktionalität
**Status:** ⏳ Pending

### Phase 3: Advanced Features / Erweiterte Funktionen
**Status:** ⏳ Pending

### Phase 4: Polish & Testing / Verfeinerung & Tests
**Status:** ⏳ Pending

---

## User Stories

### Epic 1: Basic Plugin Structure / Grundlegende Plugin-Struktur

#### Story 1.1: Plugin Registration ✅ COMPLETED
**As a** developer  
**I want** to create the basic plugin structure with proper registration  
**So that** the addon can be installed and enabled in Blender  

**Acceptance Criteria:**
- [x] `__init__.py` with proper bl_info
- [x] Plugin can be installed via Preferences > Add-ons
- [x] Plugin can be enabled/disabled
- [x] No errors in console when enabling

#### Story 1.2: N-Panel Tab Creation ✅ COMPLETED
**As a** user  
**I want** to see a "Scene States" tab in the N-Panel  
**So that** I can access the state management interface  

**Acceptance Criteria:**
- [x] Tab appears in N-Panel when addon is enabled
- [x] Tab has proper icon and title
- [x] Tab is only visible in 3D Viewport

### Epic 2: State Management Core / Kern-Zustandsverwaltung

#### Story 2.1: Save Current State ✅ COMPLETED
**As a** user  
**I want** to save the current scene state with a custom name  
**So that** I can restore it later  

**Acceptance Criteria:**
- [x] Input field for state name
- [x] "Save State" button
- [x] Captures all object transforms and visibility
- [x] Creates JSON file in project directory
- [x] Shows success/error feedback

#### Story 2.2: List Existing States ✅ COMPLETED
**As a** user  
**I want** to see a list of all saved states  
**So that** I can choose which one to load or manage  

**Acceptance Criteria:**
- [x] Scrollable list of saved states
- [x] Shows state name and creation date
- [x] Updates automatically when states are added/removed

#### Story 2.3: Load State ✅ COMPLETED
**As a** user  
**I want** to load a previously saved state  
**So that** I can restore the scene to that configuration  

**Acceptance Criteria:**
- [x] "Load" button for each state
- [x] Restores all object transforms and visibility
- [x] Shows confirmation dialog before loading
- [x] Handles missing objects gracefully

### Epic 3: State Management Operations / Zustandsverwaltungs-Operationen

#### Story 3.1: Update Existing State
**As a** user  
**I want** to update an existing state with current scene data  
**So that** I can modify saved states without creating duplicates  

**Acceptance Criteria:**
- [ ] "Update" button for each state
- [ ] Overwrites existing state data
- [ ] Shows confirmation dialog
- [ ] Updates timestamp

#### Story 3.2: Delete State
**As a** user  
**I want** to delete states I no longer need  
**So that** I can keep my state list organized  

**Acceptance Criteria:**
- [ ] "Delete" button for each state
- [ ] Shows confirmation dialog
- [ ] Removes state from JSON file
- [ ] Updates UI immediately

#### Story 3.3: Rename State
**As a** user  
**I want** to rename existing states  
**So that** I can organize them better  

**Acceptance Criteria:**
- [ ] "Rename" button or double-click to edit
- [ ] Inline text editing
- [ ] Validates name uniqueness
- [ ] Updates JSON file

### Epic 4: File Management / Dateiverwaltung

#### Story 4.1: Per-Blend File Storage
**As a** user  
**I want** each .blend file to have its own state storage  
**So that** states don't interfere between different projects  

**Acceptance Criteria:**
- [ ] JSON filename based on .blend filename
- [ ] Creates new JSON when .blend file is saved with new name
- [ ] Requires .blend file to be saved before creating states
- [ ] Shows clear error message for unsaved files

#### Story 4.2: JSON File Structure
**As a** developer  
**I want** a well-structured JSON format  
**So that** the data is readable and maintainable  

**Acceptance Criteria:**
- [ ] Clear JSON schema
- [ ] Includes metadata (version, creation date)
- [ ] Proper error handling for corrupted files
- [ ] Backward compatibility considerations

### Epic 5: User Experience / Benutzererfahrung

#### Story 5.1: Visual Feedback
**As a** user  
**I want** clear visual feedback for all operations  
**So that** I know when actions succeed or fail  

**Acceptance Criteria:**
- [ ] Success messages for save/load/update/delete
- [ ] Error messages with helpful information
- [ ] Console warnings for missing objects during load
- [ ] Performance warning for 100+ objects
- [ ] Compact UI with state names only
- [ ] Consistent UI styling

#### Story 5.2: Keyboard Shortcuts
**As a** user  
**I want** keyboard shortcuts for common operations  
**So that** I can work more efficiently  

**Acceptance Criteria:**
- [ ] Configurable hotkeys
- [ ] Default shortcuts for save/load most recent
- [ ] Shortcuts work in 3D viewport context

### Epic 6: Advanced Features / Erweiterte Funktionen

#### Story 6.1: State Preview
**As a** user  
**I want** to preview what a state contains  
**So that** I can identify states without loading them  

**Acceptance Criteria:**
- [ ] Tooltip or expandable info showing affected objects
- [ ] Object count and names
- [ ] State creation timestamp

#### Story 6.2: Selective State Loading
**As a** user  
**I want** to load only specific aspects of a state  
**So that** I have more control over what gets restored  

**Acceptance Criteria:**
- [ ] Checkboxes for: Position, Rotation, Scale, Visibility
- [ ] Object selection filter
- [ ] "Load Selected" option

---

## Technical Architecture / Technische Architektur

### Modular Design Principles / Modulare Design-Prinzipien

**English:**
- **Separation of Concerns:** Each module handles a specific responsibility
- **Plugin Architecture:** Core functionality can be extended with additional modules
- **Interface-based Design:** Clear APIs between modules for easy extension
- **Configuration-driven:** Settings and behaviors configurable for future features

**Deutsch:**
- **Trennung der Verantwortlichkeiten:** Jedes Modul behandelt eine spezifische Aufgabe
- **Plugin-Architektur:** Kernfunktionalität kann mit zusätzlichen Modulen erweitert werden
- **Interface-basiertes Design:** Klare APIs zwischen Modulen für einfache Erweiterung
- **Konfigurationsgesteuert:** Einstellungen und Verhalten konfigurierbar für zukünftige Features

### File Structure / Dateistruktur
```
scene_state_saver/
├── __init__.py              # Plugin registration & module coordination
├── core/
│   ├── __init__.py         # Core module initialization
│   ├── state_manager.py    # Abstract state management interface
│   ├── data_handler.py     # Data serialization/deserialization
│   └── file_manager.py     # File operations and path handling
├── storage/
│   ├── __init__.py         # Storage module initialization
│   ├── json_storage.py     # JSON storage implementation
│   └── storage_interface.py # Abstract storage interface
├── capture/
│   ├── __init__.py         # Capture module initialization
│   ├── object_capture.py   # Object property capture
│   └── capture_interface.py # Abstract capture interface
├── ui/
│   ├── __init__.py         # UI module initialization
│   ├── panels.py           # UI panels
│   ├── operators.py        # Blender operators
│   └── properties.py       # Custom properties
├── config/
│   ├── __init__.py         # Configuration module
│   ├── settings.py         # Plugin settings and preferences
│   └── constants.py        # Constants and default values
└── utils/
    ├── __init__.py         # Utilities module
    ├── validation.py       # Data validation utilities
    └── logging.py          # Logging and error handling
```

### Module Responsibilities / Modul-Verantwortlichkeiten

#### Core Module
- **state_manager.py:** Central coordinator for all state operations
- **data_handler.py:** Handles data transformation and validation
- **file_manager.py:** Manages file paths and .blend file detection

#### Storage Module
- **storage_interface.py:** Abstract base class for storage backends
- **json_storage.py:** JSON file storage implementation
- *Future:* database_storage.py, cloud_storage.py, etc.

#### Capture Module
- **capture_interface.py:** Abstract base class for property capture
- **object_capture.py:** Captures object transforms and visibility
- *Future:* material_capture.py, modifier_capture.py, etc.

#### UI Module
- **panels.py:** N-Panel UI components
- **operators.py:** Blender operators for user actions
- **properties.py:** Custom Blender properties

#### Config Module
- **settings.py:** User preferences and plugin configuration
- **constants.py:** Default values and system constants

#### Utils Module
- **validation.py:** Input validation and error checking
- **logging.py:** Centralized logging and error reporting

### Extension Points / Erweiterungspunkte

**For Future Features:**
1. **New Capture Types:** Implement capture_interface.py for materials, modifiers, etc.
2. **Storage Backends:** Implement storage_interface.py for databases, cloud storage
3. **UI Extensions:** Add new panels or operators in ui/ module
4. **Export Formats:** Extend data_handler.py for different file formats
5. **Automation:** Add scheduling/automation modules

### JSON Schema
```json
{
  "version": "1.0",
  "created": "2025-01-16T16:00:00Z",
  "blend_file": "project.blend",
  "states": {
    "state_name": {
      "created": "2025-01-16T16:00:00Z",
      "updated": "2025-01-16T16:05:00Z",
      "objects": {
        "Cube": {
          "location": [0.0, 0.0, 0.0],
          "rotation_euler": [0.0, 0.0, 0.0],
          "scale": [1.0, 1.0, 1.0],
          "hide_viewport": false,
          "hide_render": false
        }
      }
    }
  }
}
```

## Current Status / Aktueller Status

**Phase:** Planning Complete ✅  
**Requirements Clarified:** ✅
- Requires saved .blend files
- Objects only (no collections)
- Transform + visibility only
- Missing objects ignored with warning
- 100+ objects warning
- Compact UI
- Manual save only
- No cross-file import/export

**Completed Stories:** 1.1 ✅, 1.2 ✅, 2.1 ✅, 2.2 ✅, 2.3 ✅, 3.1 ✅, 3.2 ✅  
**Next Step:** Begin Story 3.3 - Rename State  
**Last Updated:** 2025-01-16 17:41 CET

**Implementation Notes:**
- ✅ Modulare Architektur erfolgreich implementiert
- ✅ Plugin korrekt als einzelne .py-Datei strukturiert
- ✅ Plugin erfolgreich in Blender installiert und aktiviert
- ✅ Alle Kernfunktionalitäten implementiert (Save, Load, Update, Delete)
- ✅ UI vollständig funktional im N-Panel
- ✅ JSON-Dateisystem funktioniert
- ✅ Object Capture und State Management implementiert
- ✅ **KRITISCHER BUG BEHOBEN:** Viewport-Sichtbarkeit wird jetzt korrekt wiederhergestellt
- ✅ Ausgiebige Tests durchgeführt und bestanden
- 🎯 Epic 2 (State Management Core) + Epic 3 (Operations) vollständig abgeschlossen!
