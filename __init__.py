
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Blender File Splitter For Godot",
    "author" : "Mitchell Palmer",
    "description" : "Generate multiple files for Godot form the current .blend file",
    "blender" : (4, 0, 3),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "File"
}

import bpy
import os
from bpy.props import EnumProperty, CollectionProperty, BoolProperty, StringProperty, PointerProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel, Menu

objects_that_need_to_be_hidden_again = []
debug_prevent_file_export = False

def make_gltf_file_for_collection(file_path, collection, seperate_meshes):
    no_objs = True
    for obj in collection.objects:
        #print(dir(obj))
        if not obj.show_instancer_for_viewport:
            obj.show_instancer_for_viewport = True
            objects_that_need_to_be_hidden_again.append(obj)
        try:
            obj.select_set(True)
            no_objs = False
        except AttributeError:
            pass
        if(seperate_meshes):
            print('export',file_path+'\\'+obj.name, ' : ', collection.name,' - ', obj.name)
            if not debug_prevent_file_export:
                # Make sure path exists
                t_file_path = file_path + '\\'+obj.name
                #os.makedirs(t_file_path, exist_ok=True)
                bpy.ops.wm.obj_export(filepath=t_file_path+'.obj', export_selected_objects=True, export_materials=False)
            bpy.ops.object.select_all(action='DESELECT')

    #print(file_path)
    if not no_objs and not seperate_meshes:
        print('export', collection.name)
        if not debug_prevent_file_export:
            bpy.ops.wm.obj_export(filepath=file_path+'.obj', export_selected_objects=True, export_materials=False)
        
    for obj in objects_that_need_to_be_hidden_again:
        obj.show_instancer_for_viewport = False
    
    
def export_files_for_godot(self, context, export_path, collection, seperate_meshes=True):
    # Make sure path exists
    os.makedirs(export_path+collection.name, exist_ok=True)
    print('export_files_for_godot: ',export_path+collection.name+'\\')

    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            
    # Deselect
    bpy.ops.object.select_all(action='DESELECT')
    
    for child in collection.children:        
        export_files_for_godot(self,context,export_path+collection.name+'\\', child, seperate_meshes)
    
    make_gltf_file_for_collection(export_path+collection.name, collection, seperate_meshes)

"""
OPERATIONS
"""
class export_collections_for_godot(Operator):
    """Export collections in selected root collections as seperate files for Godot"""
    bl_idname = 'scene.export_collections_for_godot'
    bl_label = "Export Collections For Godot"
    
    def execute(self, context):         
        # Make sure dir is set
        if(context.scene.godot_collections_export_path == ''):
            raise TypeError('Must set export path for your godot files')
        root_collection = context.scene.godot_root_collection
        export_path = context.scene.godot_collections_export_path
        #print('obj split :',context.scene.godot_split_each_mesh_into_a_file)
        export_files_for_godot(self, context, export_path, root_collection, context.scene.godot_split_each_mesh_into_a_file)
         
        
        
        return {'FINISHED'}
        

"""Panels"""
class VIEW3D_PT_export_collections_for_godot(Panel):
    """Export Collections For Godot"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Godot"
    bl_label = "Export Collections For Godot"

    def draw(self, context):
        layout = self.layout
        scene = bpy.data.scenes[0]
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column(align=True, heading="")
        col.prop(scene,"godot_collections_export_path")
        col.prop(scene,"godot_root_collection")
        col.prop(scene,"godot_split_each_mesh_into_a_file")
        col.operator("scene.export_collections_for_godot", text="Export")

classes = [export_collections_for_godot, VIEW3D_PT_export_collections_for_godot]

def register():
    # clear console 
    os.system("cls")

    """Register properties"""
    bpy.types.Scene.godot_collections_export_path = StringProperty(
        name='Export Path', subtype='DIR_PATH',
        description='Location for files to be generated')
        
    bpy.types.Scene.godot_root_collection = bpy.props.PointerProperty(type=bpy.types.Collection,name='Root Collection')
    
    bpy.types.Scene.godot_split_each_mesh_into_a_file = BoolProperty(
        name='Split each mesh out', default=True,
        description='When checked each mesh gets a file, otherwise one file per collection')
    
    """Register classes"""
    for cls in classes:
        bpy.utils.register_class(cls)
        print(cls.__name__ +" registered")
    
def unregister():
    """Unregister classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    """Unregister properties"""
    del bpy.types.Scene.godot_collections_export_path
    del bpy.types.Scene.godot_root_collection
    del bpy.types.Scene.godot_split_each_mesh_into_a_file

if __name__ == "__main__":
    register()