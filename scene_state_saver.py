bl_info = {
    "name": "Scene State Saver",
    "author": "AI Assistant",
    "version": (2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N-Panel > Scene State",
    "description": "Save and restore object transforms and visibility states (auto-cleanup compatible)",
    "category": "Scene",
}

import bpy
import json
from bpy.props import StringProperty, CollectionProperty, IntProperty
from bpy.types import Panel, Operator, PropertyGroup, UIList

# Property Group für einen gespeicherten State
class SceneStateItem(PropertyGroup):
    name: StringProperty(
        name="State Name",
        description="Name of the saved state",
        default="New State"
    )
    
    data: StringProperty(
        name="State Data",
        description="JSON data of the saved state",
        default=""
    )

# Property Group für das Plugin
class SceneStateSaverProperties(PropertyGroup):
    states: CollectionProperty(type=SceneStateItem)
    active_state_index: IntProperty(default=-1)
    new_state_name: StringProperty(
        name="State Name",
        description="Name for new state",
        default="State"
    )

# Operator zum Speichern eines States
class SCENE_OT_save_state(Operator):
    bl_idname = "scene.save_state"
    bl_label = "Save State"
    bl_description = "Save current scene state"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        # Sammle Daten aller Objekte
        state_data = {}
        for obj in context.scene.objects:
            state_data[obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
        
        # Prüfe ob ein State ausgewählt ist (für Update)
        if props.active_state_index >= 0 and props.active_state_index < len(props.states):
            # Update bestehenden State
            active_state = props.states[props.active_state_index]
            active_state.data = json.dumps(state_data)
            self.report({'INFO'}, f"State '{active_state.name}' updated")
        else:
            # Neuen State erstellen
            new_state = props.states.add()
            new_state.name = props.new_state_name if props.new_state_name else f"State {len(props.states)}"
            new_state.data = json.dumps(state_data)
            props.active_state_index = len(props.states) - 1
            self.report({'INFO'}, f"State '{new_state.name}' saved")
        
        return {'FINISHED'}

# Operator zum Laden eines States (Auto-Cleanup kompatibel)
class SCENE_OT_load_state(Operator):
    bl_idname = "scene.load_state"
    bl_label = "Load State"
    bl_description = "Load selected scene state (works with auto-cleanup)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        if props.active_state_index < 0 or props.active_state_index >= len(props.states):
            self.report({'ERROR'}, "No state selected")
            return {'CANCELLED'}
        
        active_state = props.states[props.active_state_index]
        
        try:
            state_data = json.loads(active_state.data)
            updated_objects = 0
            
            # Arbeite mit dem was das Auto-Cleanup übrig gelassen hat
            if isinstance(state_data, dict):
                # Bestimme verfügbare Objekt-Daten
                objects_data = {}
                
                if 'objects' in state_data:
                    # Robustes Format (falls noch Daten vorhanden)
                    objects_data = state_data['objects']
                else:
                    # Altes Format oder Auto-Cleanup hat alles entfernt
                    objects_data = state_data
                
                # Lade nur Objekte die noch existieren UND noch Daten haben
                for obj_name, obj_data in objects_data.items():
                    if obj_name in context.scene.objects:
                        # Objekt existiert - aktualisiere es
                        obj = context.scene.objects[obj_name]
                        if isinstance(obj_data, dict) and 'location' in obj_data:
                            obj.location = obj_data['location']
                            obj.rotation_euler = obj_data['rotation_euler']
                            obj.scale = obj_data['scale']
                            
                            # KORREKTE Wiederherstellung der Sichtbarkeits-Eigenschaften
                            # IMMER setzen, nicht nur wenn vorhanden!
                            obj.hide_viewport = obj_data.get('hide_viewport', False)
                            obj.hide_render = obj_data.get('hide_render', False)
                            obj.hide_select = obj_data.get('hide_select', False)
                            
                            # Collection-Sichtbarkeit wiederherstellen
                            if 'visible_get' in obj_data:
                                try:
                                    if not obj_data['visible_get']:
                                        obj.hide_set(True)
                                    else:
                                        obj.hide_set(False)
                                except:
                                    pass  # Fallback falls hide_set nicht verfügbar
                            
                            updated_objects += 1
                
                # Einfache, ehrliche Meldung
                if updated_objects > 0:
                    self.report({'INFO'}, f"State '{active_state.name}' loaded - {updated_objects} objects updated")
                else:
                    self.report({'INFO'}, f"State '{active_state.name}' loaded - no objects to update")
            
        except json.JSONDecodeError:
            self.report({'ERROR'}, "Invalid state data")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error loading state: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Operator zum Löschen eines States
class SCENE_OT_delete_state(Operator):
    bl_idname = "scene.delete_state"
    bl_label = "Delete State"
    bl_description = "Delete selected scene state"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        if props.active_state_index < 0 or props.active_state_index >= len(props.states):
            self.report({'ERROR'}, "No state selected")
            return {'CANCELLED'}
        
        state_name = props.states[props.active_state_index].name
        props.states.remove(props.active_state_index)
        
        # Index anpassen
        if props.active_state_index >= len(props.states):
            props.active_state_index = len(props.states) - 1
        
        self.report({'INFO'}, f"State '{state_name}' deleted")
        return {'FINISHED'}

# UIList für die States
class SCENE_UL_state_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon='SCENE_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='SCENE_DATA')

# Operator für "Save New State" (Auto-Cleanup kompatibel)
class SCENE_OT_save_new_state(Operator):
    bl_idname = "scene.save_new_state"
    bl_label = "Save New State"
    bl_description = "Save current scene as a new state (auto-cleanup compatible)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        # Sammle Daten ALLER Objekte (auch versteckte!)
        state_data = {}
        for obj in context.scene.objects:
            state_data[obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
        
        # Erstelle neuen State
        new_state = props.states.add()
        new_state.name = props.new_state_name if props.new_state_name else f"State {len(props.states)}"
        new_state.data = json.dumps(state_data)
        
        props.active_state_index = len(props.states) - 1
        props.new_state_name = ""
        
        self.report({'INFO'}, f"State '{new_state.name}' saved with {len(state_data)} objects")
        return {'FINISHED'}

# Operator für "Update State" (Auto-Cleanup kompatibel)
class SCENE_OT_update_state(Operator):
    bl_idname = "scene.update_state"
    bl_label = "Update State"
    bl_description = "Update the selected state with current scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        if props.active_state_index < 0 or props.active_state_index >= len(props.states):
            self.report({'ERROR'}, "No state selected to update")
            return {'CANCELLED'}
        
        # Sammle Daten ALLER Objekte (auch versteckte!)
        state_data = {}
        for obj in context.scene.objects:
            state_data[obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
        
        active_state = props.states[props.active_state_index]
        active_state.data = json.dumps(state_data)
        
        self.report({'INFO'}, f"State '{active_state.name}' updated with {len(state_data)} objects")
        return {'FINISHED'}

# Verbessertes N-Panel
class SCENE_PT_state_saver(Panel):
    bl_label = "Scene State Saver"
    bl_idname = "SCENE_PT_state_saver"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Scene State"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.scene_state_saver
        
        # Sektion 1: Neuen State erstellen
        box = layout.box()
        box.label(text="Create New State:", icon='ADD')
        row = box.row()
        row.prop(props, "new_state_name", text="Name")
        row = box.row()
        row.operator("scene.save_new_state", text="Save New State", icon='FILE_NEW')
        
        # Sektion 2: Bestehende States verwalten
        if len(props.states) > 0:
            box = layout.box()
            box.label(text="Manage Existing States:", icon='PRESET')
            
            # States Liste
            row = box.row()
            row.template_list("SCENE_UL_state_list", "", props, "states", props, "active_state_index")
            
            # Buttons für ausgewählten State
            if props.active_state_index >= 0 and props.active_state_index < len(props.states):
                selected_state = props.states[props.active_state_index]
                box.label(text=f"Selected: {selected_state.name}", icon='RADIOBUT_ON')
                
                col = box.column(align=True)
                row = col.row(align=True)
                row.operator("scene.load_state", text="Load State", icon='IMPORT')
                row.operator("scene.update_state", text="Update State", icon='FILE_REFRESH')
                row = col.row(align=True)
                row.operator("scene.delete_state", text="Delete State", icon='TRASH')
            else:
                box.label(text="No state selected", icon='RADIOBUT_OFF')
                box.label(text="Click on a state in the list to select it")

# Registrierung
classes = [
    SceneStateItem,
    SceneStateSaverProperties,
    SCENE_OT_save_state,
    SCENE_OT_load_state,
    SCENE_OT_delete_state,
    SCENE_OT_save_new_state,
    SCENE_OT_update_state,
    SCENE_UL_state_list,
    SCENE_PT_state_saver,
]

def register():
    # Erst deregistrieren falls bereits registriert
    try:
        unregister()
    except:
        pass
    
    # Dann registrieren
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            # Klasse bereits registriert, überspringen
            pass
    
    # Property nur setzen wenn noch nicht vorhanden
    if not hasattr(bpy.types.Scene, 'scene_state_saver'):
        bpy.types.Scene.scene_state_saver = bpy.props.PointerProperty(type=SceneStateSaverProperties)

def unregister():
    # Properties entfernen
    if hasattr(bpy.types.Scene, 'scene_state_saver'):
        del bpy.types.Scene.scene_state_saver
    
    # Klassen deregistrieren
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            # Klasse bereits deregistriert, überspringen
            pass

if __name__ == "__main__":
    register()
