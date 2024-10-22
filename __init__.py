bl_info = {
    "name": "Fast Paint Proxies",
    "author": "CDMJ",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "Toolbar > Paint > Paint Proxies",
    "description": "Hack to use copies of selected objects to enable uniform painting",
    "warning": "",
    "category": "Paint"
}



import bpy

# Function to check if an object has an image texture
def object_has_image_texture(obj):
    if obj.type != 'MESH':
        return False
    if obj.data.materials:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        return True
    return False

# Operator to create paint proxies
class PAINT_OT_CreatePaintProxies(bpy.types.Operator):
    bl_idname = "paint.create_paint_proxies"
    bl_label = "Create Paint Proxies"
    bl_description = "Create paint proxies for selected mesh objects with image textures"
    
    @classmethod
    def poll(cls, context):
        # Ensure more than one mesh object is selected and they have image textures
        selected_objects = context.selected_objects
        return (
            len(selected_objects) > 1 and
            all(obj.type == 'MESH' and object_has_image_texture(obj) for obj in selected_objects)
        )

    def execute(self, context):
        original_selection = context.selected_objects

        # Create 'original selection' collection
        if "original selection" not in bpy.data.collections:
            original_coll = bpy.data.collections.new("original selection")
            context.scene.collection.children.link(original_coll)
        else:
            original_coll = bpy.data.collections["original selection"]

        # Move selected objects to 'original selection' collection
        for obj in original_selection:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            original_coll.objects.link(obj)

        # Duplicate selected objects
        bpy.ops.object.duplicate()

        # Create 'paint proxies' collection
        if "paint proxies" not in bpy.data.collections:
            proxies_coll = bpy.data.collections.new("paint proxies")
            context.scene.collection.children.link(proxies_coll)
        else:
            proxies_coll = bpy.data.collections["paint proxies"]

        paint_proxies = context.selected_objects
        for obj in paint_proxies:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            proxies_coll.objects.link(obj)

        # Exclude 'original selection' collection from View Layer
        context.view_layer.layer_collection.children[original_coll.name].exclude = True

        # Join duplicated objects in 'paint proxies' collection
        bpy.context.view_layer.objects.active = paint_proxies[0]
        bpy.ops.object.convert(target='MESH')

        bpy.ops.object.join()

        # Switch to Texture Paint mode
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')

        return {'FINISHED'}

# Panel for the button in the Paint category
class PAINT_PT_PaintProxiesPanel(bpy.types.Panel):
    bl_label = "Paint Proxies"
    bl_idname = "PAINT_PT_paint_proxies_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Paint'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("paint.create_paint_proxies", text="Create Paint Proxies")

# Register and Unregister functions
def register():
    bpy.utils.register_class(PAINT_OT_CreatePaintProxies)
    bpy.utils.register_class(PAINT_PT_PaintProxiesPanel)

def unregister():
    bpy.utils.unregister_class(PAINT_OT_CreatePaintProxies)
    bpy.utils.unregister_class(PAINT_PT_PaintProxiesPanel)

if __name__ == "__main__":
    register()
