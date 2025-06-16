"""
Scene State Saver - Blender Plugin
A modular addon for saving and loading scene states in Blender.

Author: Scene State Saver Team
Version: 1.0.0
License: GPL-3.0
"""

bl_info = {
    "name": "Scene State Saver",
    "author": "Scene State Saver Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N-Panel > Scene States",
    "description": "Save and load scene states (object transforms and visibility)",
    "warning": "",
    "doc_url": "",
    "category": "Scene",
}

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import PropertyGroup, AddonPreferences, Panel, Operator
import json
import datetime
import os
from typing import Dict, Any, List, Optional

# ============================================================================
# CONSTANTS
# ============================================================================

PLUGIN_NAME = "Scene State Saver"
PLUGIN_VERSION = "1.0.0"
JSON_EXTENSION = ".json"
STATES_SUFFIX = "_states"
DEFAULT_STATE_NAME = "New State"
PERFORMANCE_WARNING_THRESHOLD = 100
PANEL_CATEGORY = "Scene States"
PANEL_LABEL = "Scene States"
JSON_SCHEMA_VERSION = "1.0"

# Error Messages
ERROR_UNSAVED_BLEND = "Please save your .blend file before creating states"
ERROR_STATE_EXISTS = "State with this name already exists"
ERROR_STATE_NOT_FOUND = "State not found"

# Success Messages
SUCCESS_STATE_SAVED = "State saved successfully"
SUCCESS_STATE_LOADED = "State loaded successfully"
SUCCESS_STATE_UPDATED = "State updated successfully"
SUCCESS_STATE_DELETED = "State deleted successfully"

# Warning Messages
WARNING_PERFORMANCE = "Large scene detected ({} objects). Processing may take time."
WARNING_MISSING_OBJECTS = "Some objects from the state were not found in the current scene"

# ============================================================================
# FILE MANAGER
# ============================================================================

class FileManager:
    """Manages file operations and path handling for state files."""
    
    @staticmethod
    def get_blend_file_path():
        """Get the current .blend file path."""
        return bpy.data.filepath
    
    @staticmethod
    def is_blend_file_saved():
        """Check if the current .blend file is saved."""
        return bool(bpy.data.filepath)
    
    @staticmethod
    def get_blend_file_name():
        """Get the current .blend file name without extension."""
        if not FileManager.is_blend_file_saved():
            return None
        
        blend_path = FileManager.get_blend_file_path()
        return os.path.splitext(os.path.basename(blend_path))[0]
    
    @staticmethod
    def get_blend_directory():
        """Get the directory containing the current .blend file."""
        if not FileManager.is_blend_file_saved():
            return None
        
        blend_path = FileManager.get_blend_file_path()
        return os.path.dirname(blend_path)
    
    @staticmethod
    def get_states_file_path():
        """Get the full path to the states JSON file."""
        if not FileManager.is_blend_file_saved():
            return None
        
        blend_name = FileManager.get_blend_file_name()
        blend_dir = FileManager.get_blend_directory()
        
        if not blend_name or not blend_dir:
            return None
        
        states_filename = f"{blend_name}{STATES_SUFFIX}{JSON_EXTENSION}"
        return os.path.join(blend_dir, states_filename)
    
    @staticmethod
    def states_file_exists():
        """Check if the states file exists."""
        states_path = FileManager.get_states_file_path()
        return states_path and os.path.exists(states_path)
    
    @staticmethod
    def validate_blend_file_saved():
        """Validate that the .blend file is saved, raise exception if not."""
        if not FileManager.is_blend_file_saved():
            raise ValueError(ERROR_UNSAVED_BLEND)
    
    @staticmethod
    def ensure_directory_exists(file_path):
        """Ensure the directory for the given file path exists."""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

# ============================================================================
# DATA HANDLER
# ============================================================================

class DataHandler:
    """Handles data transformation and validation for state files."""
    
    @staticmethod
    def create_empty_states_data(blend_filename: str) -> Dict[str, Any]:
        """Create an empty states data structure."""
        return {
            "version": JSON_SCHEMA_VERSION,
            "created": datetime.datetime.now().isoformat(),
            "blend_file": blend_filename,
            "states": {}
        }
    
    @staticmethod
    def create_state_data(objects_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a state data structure from objects data."""
        now = datetime.datetime.now().isoformat()
        return {
            "created": now,
            "updated": now,
            "objects": objects_data
        }
    
    @staticmethod
    def update_state_data(state_data: Dict[str, Any], objects_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Update existing state data with new objects data."""
        state_data["updated"] = datetime.datetime.now().isoformat()
        state_data["objects"] = objects_data
        return state_data
    
    @staticmethod
    def serialize_to_json(data: Dict[str, Any]) -> str:
        """Serialize data to JSON string."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def deserialize_from_json(json_string: str) -> Dict[str, Any]:
        """Deserialize JSON string to data."""
        return json.loads(json_string)
    
    @staticmethod
    def validate_states_data(data: Dict[str, Any]) -> bool:
        """Validate the structure of states data."""
        required_keys = ["version", "created", "blend_file", "states"]
        
        if not isinstance(data, dict):
            return False
        
        for key in required_keys:
            if key not in data:
                return False
        
        if not isinstance(data["states"], dict):
            return False
        
        return True
    
    @staticmethod
    def get_state_names(states_data: Dict[str, Any]) -> List[str]:
        """Get list of state names from states data."""
        if not DataHandler.validate_states_data(states_data):
            return []
        
        return list(states_data["states"].keys())
    
    @staticmethod
    def state_exists(states_data: Dict[str, Any], state_name: str) -> bool:
        """Check if a state exists in the states data."""
        if not DataHandler.validate_states_data(states_data):
            return False
        
        return state_name in states_data["states"]

# ============================================================================
# OBJECT CAPTURE
# ============================================================================

class ObjectCapture:
    """Captures object transforms and visibility from the current scene."""
    
    @staticmethod
    def get_all_objects() -> List[bpy.types.Object]:
        """Get all objects in the current scene."""
        return list(bpy.context.scene.objects)
    
    @staticmethod
    def capture_object_data(obj: bpy.types.Object) -> Dict[str, Any]:
        """Capture transform and visibility data for a single object."""
        data = {
            "location": list(obj.location),
            "rotation_euler": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "hide_viewport": obj.hide_viewport,
            "hide_render": obj.hide_render,
            "hide_set": obj.hide_get()  # Capture the actual hide_set() status
        }
        
        # Capture bone poses for armatures
        if obj.type == 'ARMATURE' and obj.pose:
            data["bone_poses"] = ObjectCapture.capture_bone_poses(obj)
        
        return data
    
    @staticmethod
    def capture_bone_poses(armature_obj: bpy.types.Object) -> Dict[str, Dict[str, Any]]:
        """Capture bone pose data for an armature object."""
        if armature_obj.type != 'ARMATURE' or not armature_obj.pose:
            return {}
        
        bone_data = {}
        for pose_bone in armature_obj.pose.bones:
            # Get the current rotation values based on the rotation mode
            if pose_bone.rotation_mode == 'QUATERNION':
                # For quaternion mode, use the quaternion values
                current_quat = pose_bone.rotation_quaternion.copy()
                # Convert to euler for backup
                current_euler = current_quat.to_euler()
            else:
                # For euler modes, use the euler values
                current_euler = pose_bone.rotation_euler.copy()
                # Convert to quaternion for backup
                current_quat = current_euler.to_quaternion()
            
            bone_data[pose_bone.name] = {
                "location": list(pose_bone.location),
                "rotation_euler": list(current_euler),
                "rotation_quaternion": list(current_quat),
                "scale": list(pose_bone.scale),
                "rotation_mode": pose_bone.rotation_mode
            }
        
        return bone_data
    
    @staticmethod
    def capture_all_objects() -> Dict[str, Dict[str, Any]]:
        """Capture data for all objects in the scene."""
        objects = ObjectCapture.get_all_objects()
        
        # Performance warning
        if len(objects) >= PERFORMANCE_WARNING_THRESHOLD:
            print(WARNING_PERFORMANCE.format(len(objects)))
        
        objects_data = {}
        for obj in objects:
            objects_data[obj.name] = ObjectCapture.capture_object_data(obj)
        
        return objects_data
    
    @staticmethod
    def apply_object_data(obj: bpy.types.Object, obj_data: Dict[str, Any]) -> bool:
        """Apply captured data to an object."""
        try:
            # Apply transforms
            obj.location = obj_data["location"]
            obj.rotation_euler = obj_data["rotation_euler"]
            obj.scale = obj_data["scale"]
            
            # Apply visibility properly
            hide_viewport = obj_data["hide_viewport"]
            hide_render = obj_data["hide_render"]
            
            # Set visibility properties
            obj.hide_viewport = hide_viewport
            obj.hide_render = hide_render
            
            # Apply the hide_set status (Eye-Button status)
            if "hide_set" in obj_data:
                hide_set_status = obj_data["hide_set"]
                obj.hide_set(hide_set_status)
            else:
                # Fallback for older states without hide_set data
                obj.hide_set(hide_viewport)
            
            # Apply bone poses for armatures
            if obj.type == 'ARMATURE' and "bone_poses" in obj_data:
                ObjectCapture.apply_bone_poses(obj, obj_data["bone_poses"])
            
            return True
            
        except Exception as e:
            print(f"Error applying data to object {obj.name}: {e}")
            return False
    
    @staticmethod
    def apply_bone_poses(armature_obj: bpy.types.Object, bone_poses: Dict[str, Dict[str, Any]]) -> bool:
        """Apply bone pose data to an armature object."""
        if armature_obj.type != 'ARMATURE' or not armature_obj.pose:
            return False
        
        try:
            for bone_name, bone_data in bone_poses.items():
                pose_bone = armature_obj.pose.bones.get(bone_name)
                if pose_bone:
                    # Apply transforms
                    pose_bone.location = bone_data["location"]
                    pose_bone.scale = bone_data["scale"]
                    
                    # Set rotation mode first, then apply rotation
                    if "rotation_mode" in bone_data:
                        target_mode = bone_data["rotation_mode"]
                        pose_bone.rotation_mode = target_mode
                        
                        # Apply rotation based on the target mode
                        if target_mode == 'QUATERNION':
                            pose_bone.rotation_quaternion = bone_data["rotation_quaternion"]
                        else:
                            pose_bone.rotation_euler = bone_data["rotation_euler"]
                    else:
                        # Fallback: apply both and let Blender handle conversion
                        pose_bone.rotation_euler = bone_data["rotation_euler"]
                        if pose_bone.rotation_mode == 'QUATERNION':
                            pose_bone.rotation_quaternion = bone_data["rotation_quaternion"]
            
            return True
            
        except Exception as e:
            print(f"Error applying bone poses to {armature_obj.name}: {e}")
            return False
    
    @staticmethod
    def apply_all_objects(objects_data: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Apply captured data to all objects in the scene."""
        results = {}
        missing_objects = []
        
        for obj_name, obj_data in objects_data.items():
            obj = bpy.context.scene.objects.get(obj_name)
            if obj:
                results[obj_name] = ObjectCapture.apply_object_data(obj, obj_data)
            else:
                missing_objects.append(obj_name)
                results[obj_name] = False
        
        # Force complete scene and viewport update
        bpy.context.view_layer.update()
        
        # Force update of all view layers
        for scene in bpy.data.scenes:
            for view_layer in scene.view_layers:
                view_layer.update()
        
        # Force redraw of all areas
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
        
        # Force depsgraph update
        bpy.context.evaluated_depsgraph_get().update()
        
        # Report missing objects
        if missing_objects:
            print(WARNING_MISSING_OBJECTS)
            print(f"Missing objects: {', '.join(missing_objects)}")
        
        return results

# ============================================================================
# STATE MANAGER
# ============================================================================

class StateManager:
    """Central coordinator for all state operations."""
    
    def load_states_data(self) -> Optional[Dict[str, Any]]:
        """Load states data from file."""
        try:
            FileManager.validate_blend_file_saved()
            
            states_path = FileManager.get_states_file_path()
            if not states_path or not FileManager.states_file_exists():
                # Create empty states data if file doesn't exist
                blend_name = FileManager.get_blend_file_name()
                return DataHandler.create_empty_states_data(blend_name)
            
            with open(states_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
            
            data = DataHandler.deserialize_from_json(json_content)
            
            if not DataHandler.validate_states_data(data):
                raise ValueError("Invalid states file format")
            
            return data
            
        except Exception as e:
            print(f"Error loading states: {e}")
            return None
    
    def save_states_data(self, states_data: Dict[str, Any]) -> bool:
        """Save states data to file."""
        try:
            FileManager.validate_blend_file_saved()
            
            if not DataHandler.validate_states_data(states_data):
                raise ValueError("Invalid states data format")
            
            states_path = FileManager.get_states_file_path()
            if not states_path:
                return False
            
            FileManager.ensure_directory_exists(states_path)
            
            json_content = DataHandler.serialize_to_json(states_data)
            
            with open(states_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            return True
            
        except Exception as e:
            print(f"Error saving states: {e}")
            return False
    
    def get_state_names(self) -> List[str]:
        """Get list of all state names."""
        states_data = self.load_states_data()
        if not states_data:
            return []
        
        return DataHandler.get_state_names(states_data)
    
    def save_state(self, state_name: str, overwrite: bool = False) -> bool:
        """Save the current scene state with the given name."""
        try:
            # Validate blend file is saved
            FileManager.validate_blend_file_saved()
            
            # Load existing states data
            states_data = self.load_states_data()
            if not states_data:
                return False
            
            # Check if state already exists
            if DataHandler.state_exists(states_data, state_name) and not overwrite:
                print(f"Error: {ERROR_STATE_EXISTS}")
                return False
            
            # Capture current scene data
            objects_data = ObjectCapture.capture_all_objects()
            
            # Create state data
            state_data = DataHandler.create_state_data(objects_data)
            
            # Add to states data
            states_data["states"][state_name] = state_data
            
            # Save to file
            success = self.save_states_data(states_data)
            
            if success:
                print(f"{SUCCESS_STATE_SAVED}: {state_name}")
            
            return success
            
        except Exception as e:
            print(f"Error saving state '{state_name}': {e}")
            return False
    
    def load_state(self, state_name: str) -> bool:
        """Load a saved state and apply it to the current scene."""
        try:
            # Load states data
            states_data = self.load_states_data()
            if not states_data:
                return False
            
            # Check if state exists
            if not DataHandler.state_exists(states_data, state_name):
                print(f"Error: {ERROR_STATE_NOT_FOUND}")
                return False
            
            # Get state data
            state_data = states_data["states"][state_name]
            objects_data = state_data["objects"]
            
            # Apply to scene
            results = ObjectCapture.apply_all_objects(objects_data)
            
            # Check results
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            print(f"{SUCCESS_STATE_LOADED}: {state_name} ({success_count}/{total_count} objects)")
            
            return True
            
        except Exception as e:
            print(f"Error loading state '{state_name}': {e}")
            return False
    
    def update_state(self, state_name: str) -> bool:
        """Update an existing state with current scene data."""
        try:
            # Load states data
            states_data = self.load_states_data()
            if not states_data:
                return False
            
            # Check if state exists
            if not DataHandler.state_exists(states_data, state_name):
                print(f"Error: {ERROR_STATE_NOT_FOUND}")
                return False
            
            # Capture current scene data
            objects_data = ObjectCapture.capture_all_objects()
            
            # Update state data
            state_data = states_data["states"][state_name]
            states_data["states"][state_name] = DataHandler.update_state_data(state_data, objects_data)
            
            # Save to file
            success = self.save_states_data(states_data)
            
            if success:
                print(f"{SUCCESS_STATE_UPDATED}: {state_name}")
            
            return success
            
        except Exception as e:
            print(f"Error updating state '{state_name}': {e}")
            return False
    
    def delete_state(self, state_name: str) -> bool:
        """Delete a saved state."""
        try:
            # Load states data
            states_data = self.load_states_data()
            if not states_data:
                return False
            
            # Check if state exists
            if not DataHandler.state_exists(states_data, state_name):
                print(f"Error: {ERROR_STATE_NOT_FOUND}")
                return False
            
            # Remove state
            del states_data["states"][state_name]
            
            # Save to file
            success = self.save_states_data(states_data)
            
            if success:
                print(f"{SUCCESS_STATE_DELETED}: {state_name}")
            
            return success
            
        except Exception as e:
            print(f"Error deleting state '{state_name}': {e}")
            return False

# Global instance
state_manager = StateManager()

# ============================================================================
# PROPERTIES
# ============================================================================

class StateNameItem(PropertyGroup):
    """Property group for individual state names in the collection."""
    name: StringProperty(
        name="State Name",
        description="Name of the state"
    )

class SceneStateProperties(PropertyGroup):
    """Properties for Scene State Saver stored in scene."""
    
    new_state_name: StringProperty(
        name="State Name",
        description="Name for the new state",
        default=DEFAULT_STATE_NAME,
        maxlen=64
    )
    
    selected_state_index: IntProperty(
        name="Selected State Index",
        description="Index of the currently selected state in the list",
        default=0,
        min=0
    )
    
    current_active_state: StringProperty(
        name="Current Active State",
        description="Name of the currently active (loaded) state",
        default=""
    )
    
    state_names_collection: bpy.props.CollectionProperty(
        type=StateNameItem,
        name="State Names Collection",
        description="Collection of state names for the UIList"
    )

class SceneStatePreferences(AddonPreferences):
    """Addon preferences for Scene State Saver."""
    
    bl_idname = __name__
    
    show_performance_warnings: BoolProperty(
        name="Show Performance Warnings",
        description="Show warnings for scenes with many objects",
        default=True
    )
    
    performance_threshold: IntProperty(
        name="Performance Warning Threshold",
        description="Number of objects that triggers a performance warning",
        default=100,
        min=10,
        max=1000
    )
    
    def draw(self, context):
        """Draw the preferences panel."""
        layout = self.layout
        
        box = layout.box()
        box.label(text="Performance Settings:")
        box.prop(self, "show_performance_warnings")
        box.prop(self, "performance_threshold")

# ============================================================================
# UI LIST
# ============================================================================

class SCENE_STATE_UL_states_list(bpy.types.UIList):
    """UIList for displaying scene states."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Draw a single item in the list."""
        scene_props = context.scene.scene_state_saver
        state_name = item.name  # item is a StateNameItem with .name property
        
        # Check if this is the currently active state
        is_active = (state_name == scene_props.current_active_state)
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Show state name with icon
            if is_active:
                layout.label(text=state_name, icon='RADIOBUT_ON')
            else:
                layout.label(text=state_name, icon='RADIOBUT_OFF')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='PRESET')

# ============================================================================
# OPERATORS
# ============================================================================

class SCENE_STATE_OT_save_state(Operator):
    """Save current scene state."""
    
    bl_idname = "scene_state.save_state"
    bl_label = "Save State"
    bl_description = "Save current scene state with transforms and visibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the save operation."""
        try:
            # Check if blend file is saved
            if not FileManager.is_blend_file_saved():
                self.report({'ERROR'}, "Please save your .blend file first")
                return {'CANCELLED'}
            
            # Get state name from scene properties
            scene_props = context.scene.scene_state_saver
            state_name = scene_props.new_state_name.strip()
            
            # Validate state name
            if not state_name or state_name == DEFAULT_STATE_NAME:
                self.report({'ERROR'}, "Please enter a valid state name")
                return {'CANCELLED'}
            
            # Save the state
            success = state_manager.save_state(state_name)
            
            if success:
                # Set the newly saved state as the current active state
                scene_props.current_active_state = state_name
                self.report({'INFO'}, f"State '{state_name}' saved successfully")
                # Clear the input field
                scene_props.new_state_name = DEFAULT_STATE_NAME
                # Refresh the collection after saving
                bpy.ops.scene_state.refresh_list()
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to save state '{state_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error saving state: {str(e)}")
            return {'CANCELLED'}

class SCENE_STATE_OT_load_state(Operator):
    """Load the selected scene state from the list."""
    
    bl_idname = "scene_state.load_state"
    bl_label = "Load State"
    bl_description = "Load the selected scene state"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the load operation."""
        try:
            scene_props = context.scene.scene_state_saver
            state_names = state_manager.get_state_names()
            
            # Check if there are any states
            if not state_names:
                self.report({'ERROR'}, "No states available")
                return {'CANCELLED'}
            
            # Check if selection is valid
            if scene_props.selected_state_index >= len(state_names):
                self.report({'ERROR'}, "No state selected")
                return {'CANCELLED'}
            
            # Get selected state name
            state_name = state_names[scene_props.selected_state_index]
            
            # Load the state
            success = state_manager.load_state(state_name)
            
            if success:
                # Update current active state
                scene_props.current_active_state = state_name
                self.report({'INFO'}, f"State '{state_name}' loaded successfully")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to load state '{state_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error loading state: {str(e)}")
            return {'CANCELLED'}

class SCENE_STATE_OT_update_state(Operator):
    """Update the selected scene state with current scene data."""
    
    bl_idname = "scene_state.update_state"
    bl_label = "Update State"
    bl_description = "Update the selected scene state with current scene data"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute the update operation."""
        try:
            scene_props = context.scene.scene_state_saver
            state_names = state_manager.get_state_names()
            
            # Check if there are any states
            if not state_names:
                self.report({'ERROR'}, "No states available")
                return {'CANCELLED'}
            
            # Check if selection is valid
            if scene_props.selected_state_index >= len(state_names):
                self.report({'ERROR'}, "No state selected")
                return {'CANCELLED'}
            
            # Get selected state name
            state_name = state_names[scene_props.selected_state_index]
            
            # Update the state
            success = state_manager.update_state(state_name)
            
            if success:
                self.report({'INFO'}, f"State '{state_name}' updated successfully")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to update state '{state_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error updating state: {str(e)}")
            return {'CANCELLED'}

class SCENE_STATE_OT_delete_state(Operator):
    """Delete the selected scene state."""
    
    bl_idname = "scene_state.delete_state"
    bl_label = "Delete State"
    bl_description = "Delete the selected scene state"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        """Show confirmation dialog."""
        scene_props = context.scene.scene_state_saver
        state_names = state_manager.get_state_names()
        
        # Check if there are any states and selection is valid
        if not state_names or scene_props.selected_state_index >= len(state_names):
            self.report({'ERROR'}, "No state selected")
            return {'CANCELLED'}
        
        # Get selected state name for confirmation
        state_name = state_names[scene_props.selected_state_index]
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        """Execute the delete operation."""
        try:
            scene_props = context.scene.scene_state_saver
            state_names = state_manager.get_state_names()
            
            # Check if there are any states
            if not state_names:
                self.report({'ERROR'}, "No states available")
                return {'CANCELLED'}
            
            # Check if selection is valid
            if scene_props.selected_state_index >= len(state_names):
                self.report({'ERROR'}, "No state selected")
                return {'CANCELLED'}
            
            # Get selected state name
            state_name = state_names[scene_props.selected_state_index]
            
            # Delete the state
            success = state_manager.delete_state(state_name)
            
            if success:
                # Clear current active state if it was deleted
                if scene_props.current_active_state == state_name:
                    scene_props.current_active_state = ""
                
                # Refresh the collection after deletion
                bpy.ops.scene_state.refresh_list()
                
                self.report({'INFO'}, f"State '{state_name}' deleted successfully")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, f"Failed to delete state '{state_name}'")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error deleting state: {str(e)}")
            return {'CANCELLED'}

class SCENE_STATE_OT_select_state(Operator):
    """Select a state in the list."""
    
    bl_idname = "scene_state.select_state"
    bl_label = "Select State"
    bl_description = "Select this state in the list"
    bl_options = {'REGISTER'}
    
    state_index: IntProperty(
        name="State Index",
        description="Index of the state to select"
    )
    
    def execute(self, context):
        """Execute the selection."""
        scene_props = context.scene.scene_state_saver
        scene_props.selected_state_index = self.state_index
        return {'FINISHED'}

class SCENE_STATE_OT_refresh_list(Operator):
    """Refresh the states list."""
    
    bl_idname = "scene_state.refresh_list"
    bl_label = "Refresh List"
    bl_description = "Refresh the states list"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Execute the refresh operation."""
        scene_props = context.scene.scene_state_saver
        state_names = state_manager.get_state_names()
        
        # Clear and rebuild the collection
        scene_props.state_names_collection.clear()
        for state_name in state_names:
            item = scene_props.state_names_collection.add()
            item.name = state_name
        
        # Ensure selection index is valid
        if scene_props.selected_state_index >= len(state_names):
            scene_props.selected_state_index = max(0, len(state_names) - 1)
        
        return {'FINISHED'}

# ============================================================================
# PANELS
# ============================================================================

class SCENE_STATE_PT_main_panel(Panel):
    """Main panel for Scene State Saver in N-Panel."""
    
    bl_label = PANEL_LABEL
    bl_idname = "SCENE_STATE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY
    bl_context = "objectmode"
    
    def draw(self, context):
        """Draw the main panel."""
        layout = self.layout
        scene = context.scene
        scene_props = scene.scene_state_saver
        
        # Check if .blend file is saved
        if not FileManager.is_blend_file_saved():
            box = layout.box()
            box.label(text="Save .blend file first", icon='ERROR')
            box.label(text="States require a saved project")
            return
        
        # Show current .blend file info
        blend_name = FileManager.get_blend_file_name()
        if blend_name:
            box = layout.box()
            box.label(text=f"Project: {blend_name}", icon='FILE_BLEND')
        
        # State creation section
        box = layout.box()
        box.label(text="Create New State:", icon='ADD')
        
        # State name input
        row = box.row()
        row.prop(scene_props, "new_state_name", text="Name")
        
        # Save button
        row = box.row()
        row.operator("scene_state.save_state", text="Save State", icon='FILE_TICK')
        
        # States list section
        box = layout.box()
        box.label(text="Saved States:", icon='PRESET')
        
        # Get list of saved states
        state_names = state_manager.get_state_names()
        
        if state_names:
            # Native Blender UIList (like in your screenshot)
            row = box.row()
            row.template_list(
                "SCENE_STATE_UL_states_list",  # UIList class
                "",  # list_id
                scene_props,  # dataptr (object containing the collection)
                "state_names_collection",  # propname (collection property name)
                scene_props,  # active_dataptr (object containing active index)
                "selected_state_index",  # active_propname (active index property)
                rows=4,  # Number of visible rows
                maxrows=8  # Maximum rows before scrolling
            )
            
            # Action buttons below the list
            row = box.row(align=True)
            row.operator("scene_state.load_state", text="Load", icon='IMPORT')
            row.operator("scene_state.update_state", text="Update", icon='FILE_REFRESH')
            row.operator("scene_state.delete_state", text="Delete", icon='TRASH')
            
        else:
            box.label(text="No states saved yet", icon='INFO')

# ============================================================================
# REGISTRATION
# ============================================================================

classes = [
    StateNameItem,
    SceneStateProperties,
    SceneStatePreferences,
    SCENE_STATE_UL_states_list,
    SCENE_STATE_OT_save_state,
    SCENE_STATE_OT_load_state,
    SCENE_STATE_OT_update_state,
    SCENE_STATE_OT_delete_state,
    SCENE_STATE_OT_select_state,
    SCENE_STATE_OT_refresh_list,
    SCENE_STATE_PT_main_panel,
]

def register():
    """Register all addon classes."""
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
        
        # Add properties to scene
        bpy.types.Scene.scene_state_saver = bpy.props.PointerProperty(type=SceneStateProperties)
        
        print(f"Scene State Saver v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]} registered successfully")
        
    except Exception as e:
        print(f"Error registering Scene State Saver: {e}")
        unregister()
        raise

def unregister():
    """Unregister all addon classes."""
    try:
        # Remove properties from scene
        if hasattr(bpy.types.Scene, 'scene_state_saver'):
            del bpy.types.Scene.scene_state_saver
        
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
                
        print("Scene State Saver unregistered successfully")
        
    except Exception as e:
        print(f"Error unregistering Scene State Saver: {e}")

if __name__ == "__main__":
    register()
