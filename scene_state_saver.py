bl_info = {
    "name": "Scene State Saver",
    "author": "AI Assistant",
    "version": (2, 1),
    "blender": (3, 0, 0),
    "location": "View3D > N-Panel > Scene State",
    "description": "Save and restore object transforms, visibility states, and armature poses (auto-cleanup compatible)",
    "category": "Scene",
}

import bpy
import json
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty
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
    
    include_poses: BoolProperty(
        name="Include Poses",
        description="Whether this state includes armature poses",
        default=True
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
    save_armature_poses: BoolProperty(
        name="Save Armature Poses",
        description="Include armature poses when saving states",
        default=True
    )
    load_armature_poses: BoolProperty(
        name="Load Armature Poses",
        description="Restore armature poses when loading states",
        default=True
    )

def save_armature_pose_data(armature_obj):
    """Save pose data for an armature object"""
    if armature_obj.type != 'ARMATURE' or not armature_obj.pose:
        return None
    
    pose_data = {}
    for bone_name, pose_bone in armature_obj.pose.bones.items():
        pose_data[bone_name] = {
            'location': list(pose_bone.location),
            'rotation_euler': list(pose_bone.rotation_euler),
            'rotation_quaternion': list(pose_bone.rotation_quaternion),
            'scale': list(pose_bone.scale),
            'rotation_mode': pose_bone.rotation_mode
        }
    
    return pose_data

def restore_armature_pose_data(armature_obj, pose_data):
    """Restore pose data for an armature object"""
    if armature_obj.type != 'ARMATURE' or not armature_obj.pose or not pose_data:
        return False
    
    # Wechsle temporär in Pose Mode
    current_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    bpy.context.view_layer.objects.active = armature_obj
    
    try:
        bpy.ops.object.mode_set(mode='POSE')
        
        for bone_name, bone_data in pose_data.items():
            if bone_name in armature_obj.pose.bones:
                pose_bone = armature_obj.pose.bones[bone_name]
                
                # Setze Rotation Mode zuerst
                pose_bone.rotation_mode = bone_data.get('rotation_mode', 'XYZ')
                
                # Restore transform data
                pose_bone.location = bone_data.get('location', [0, 0, 0])
                pose_bone.scale = bone_data.get('scale', [1, 1, 1])
                
                # Restore rotation based on mode
                if pose_bone.rotation_mode == 'QUATERNION':
                    pose_bone.rotation_quaternion = bone_data.get('rotation_quaternion', [1, 0, 0, 0])
                else:
                    pose_bone.rotation_euler = bone_data.get('rotation_euler', [0, 0, 0])
        
        # Zurück zum ursprünglichen Mode
        bpy.ops.object.mode_set(mode=current_mode)
        return True
        
    except Exception as e:
        print(f"Error restoring pose for {armature_obj.name}: {e}")
        try:
            bpy.ops.object.mode_set(mode=current_mode)
        except:
            pass
        return False

# Operator zum Speichern eines States
class SCENE_OT_save_state(Operator):
    bl_idname = "scene.save_state"
    bl_label = "Save State"
    bl_description = "Save current scene state"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.scene_state_saver
        
        # Sammle Daten aller Objekte
        state_data = {
            'objects': {},
            'armature_poses': {},
            'version': '2.1'
        }
        
        for obj in context.scene.objects:
            # Standard Objekt-Daten
            state_data['objects'][obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
            
            # Armature Pose Daten
            if props.save_armature_poses and obj.type == 'ARMATURE':
                pose_data = save_armature_pose_data(obj)
                if pose_data:
                    state_data['armature_poses'][obj.name] = pose_data
        
        # Prüfe ob ein State ausgewählt ist (für Update)
        if props.active_state_index >= 0 and props.active_state_index < len(props.states):
            # Update bestehenden State
            active_state = props.states[props.active_state_index]
            active_state.data = json.dumps(state_data)
            active_state.include_poses = props.save_armature_poses
            
            pose_count = len(state_data['armature_poses'])
            pose_info = f" (with {pose_count} armature poses)" if pose_count > 0 else ""
            self.report({'INFO'}, f"State '{active_state.name}' updated{pose_info}")
        else:
            # Neuen State erstellen
            new_state = props.states.add()
            new_state.name = props.new_state_name if props.new_state_name else f"State {len(props.states)}"
            new_state.data = json.dumps(state_data)
            new_state.include_poses = props.save_armature_poses
            props.active_state_index = len(props.states) - 1
            
            pose_count = len(state_data['armature_poses'])
            pose_info = f" (with {pose_count} armature poses)" if pose_count > 0 else ""
            self.report({'INFO'}, f"State '{new_state.name}' saved{pose_info}")
        
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
            restored_poses = 0
            
            # Handle different data formats (backward compatibility)
            if isinstance(state_data, dict):
                # New format with version info
                if 'version' in state_data and state_data['version'] == '2.1':
                    objects_data = state_data.get('objects', {})
                    poses_data = state_data.get('armature_poses', {})
                elif 'objects' in state_data:
                    # Older format but with objects key
                    objects_data = state_data['objects']
                    poses_data = {}
                else:
                    # Legacy format - all data is object data
                    objects_data = state_data
                    poses_data = {}
                
                # Restore object transforms and visibility
                for obj_name, obj_data in objects_data.items():
                    if obj_name in context.scene.objects:
                        obj = context.scene.objects[obj_name]
                        if isinstance(obj_data, dict) and 'location' in obj_data:
                            obj.location = obj_data['location']
                            obj.rotation_euler = obj_data['rotation_euler']
                            obj.scale = obj_data['scale']
                            
                            # Restore visibility
                            obj.hide_viewport = obj_data.get('hide_viewport', False)
                            obj.hide_render = obj_data.get('hide_render', False)
                            obj.hide_select = obj_data.get('hide_select', False)
                            
                            # Collection visibility
                            if 'visible_get' in obj_data:
                                try:
                                    if not obj_data['visible_get']:
                                        obj.hide_set(True)
                                    else:
                                        obj.hide_set(False)
                                except:
                                    pass
                            
                            updated_objects += 1
                
                # Restore armature poses if enabled
                if props.load_armature_poses and poses_data:
                    for armature_name, pose_data in poses_data.items():
                        if armature_name in context.scene.objects:
                            armature_obj = context.scene.objects[armature_name]
                            if restore_armature_pose_data(armature_obj, pose_data):
                                restored_poses += 1
                
                # Report results
                message_parts = []
                if updated_objects > 0:
                    message_parts.append(f"{updated_objects} objects updated")
                if restored_poses > 0:
                    message_parts.append(f"{restored_poses} armature poses restored")
                
                if message_parts:
                    message = f"State '{active_state.name}' loaded - " + ", ".join(message_parts)
                else:
                    message = f"State '{active_state.name}' loaded - no objects to update"
                
                self.report({'INFO'}, message)
            
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
            row = layout.row()
            row.prop(item, "name", text="", emboss=False, icon='SCENE_DATA')
            # Zeige Icon wenn Poses enthalten sind
            if item.include_poses:
                row.label(text="", icon='ARMATURE_DATA')
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
        state_data = {
            'objects': {},
            'armature_poses': {},
            'version': '2.1'
        }
        
        for obj in context.scene.objects:
            # Standard Objekt-Daten
            state_data['objects'][obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
            
            # Armature Pose Daten
            if props.save_armature_poses and obj.type == 'ARMATURE':
                pose_data = save_armature_pose_data(obj)
                if pose_data:
                    state_data['armature_poses'][obj.name] = pose_data
        
        # Erstelle neuen State
        new_state = props.states.add()
        new_state.name = props.new_state_name if props.new_state_name else f"State {len(props.states)}"
        new_state.data = json.dumps(state_data)
        new_state.include_poses = props.save_armature_poses
        
        props.active_state_index = len(props.states) - 1
        props.new_state_name = ""
        
        object_count = len(state_data['objects'])
        pose_count = len(state_data['armature_poses'])
        pose_info = f" and {pose_count} armature poses" if pose_count > 0 else ""
        
        self.report({'INFO'}, f"State '{new_state.name}' saved with {object_count} objects{pose_info}")
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
        state_data = {
            'objects': {},
            'armature_poses': {},
            'version': '2.1'
        }
        
        for obj in context.scene.objects:
            # Standard Objekt-Daten
            state_data['objects'][obj.name] = {
                'type': obj.type,
                'location': list(obj.location),
                'rotation_euler': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'hide_select': obj.hide_select,
                'visible_get': obj.visible_get()
            }
            
            # Armature Pose Daten
            if props.save_armature_poses and obj.type == 'ARMATURE':
                pose_data = save_armature_pose_data(obj)
                if pose_data:
                    state_data['armature_poses'][obj.name] = pose_data
        
        active_state = props.states[props.active_state_index]
        active_state.data = json.dumps(state_data)
        active_state.include_poses = props.save_armature_poses
        
        object_count = len(state_data['objects'])
        pose_count = len(state_data['armature_poses'])
        pose_info = f" and {pose_count} armature poses" if pose_count > 0 else ""
        
        self.report({'INFO'}, f"State '{active_state.name}' updated with {object_count} objects{pose_info}")
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
        
        # Armature Pose Settings
        box = layout.box()
        box.label(text="Armature Pose Settings:", icon='ARMATURE_DATA')
        col = box.column()
        col.prop(props, "save_armature_poses", text="Save Armature Poses")
        col.prop(props, "load_armature_poses", text="Load Armature Poses")
        
        # Count armatures in scene
        armature_count = len([obj for obj in context.scene.objects if obj.type == 'ARMATURE'])
        if armature_count > 0:
            box.label(text=f"Found {armature_count} armature(s) in scene", icon='INFO')
        else:
            box.label(text="No armatures found in scene", icon='ERROR')
        
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
                
                # State Info
                info_box = box.box()
                info_box.label(text=f"Selected: {selected_state.name}", icon='RADIOBUT_ON')
                
                # Zeige State Details
                try:
                    state_data = json.loads(selected_state.data)
                    if isinstance(state_data, dict):
                        if 'version' in state_data and state_data['version'] == '2.1':
                            obj_count = len(state_data.get('objects', {}))
                            pose_count = len(state_data.get('armature_poses', {}))
                            info_box.label(text=f"Objects: {obj_count}, Poses: {pose_count}")
                        else:
                            obj_count = len(state_data.get('objects', state_data))
                            info_box.label(text=f"Objects: {obj_count} (legacy format)")
                except:
                    info_box.label(text="State data format unknown")
                
                # Action Buttons
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
