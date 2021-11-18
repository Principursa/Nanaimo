import bpy
import random
import os
import json
bl_info = {
    "name": "Nanaimo",
    "description": "Add-on to help automate 3D NFT production.",
    "author": "Principursa",
    "version": (1, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > Nanaimo",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Render",
    }

def CreateJson(traits,filepath,id,name):
    data = {
        "name": f"{name}_{id}",
        "image": "placeholder",

    }
    data["attributes"] = []
    for x in traits.keys():
        data["attributes"].append({
        "trait_type": f"{x}",
        "value": f"{traits.get(x)}"        
        
        
        
        
        })
    bpath = bpy.path.abspath(filepath)    
    file = os.path.join(bpath,f"{name}_data_{id}.json")    
    jsonString = json.dumps(data, indent=4)
    jsonFile = open(file,"w")
    jsonFile.write(jsonString)
    jsonFile.close()

            

class NanaimoPropertyGroup(bpy.types.PropertyGroup):
    render_amount: bpy.props.IntProperty(name="Render Amount",description="Amount of images to render",soft_min=0,soft_max=10000,default=5)
    render_name: bpy.props.StringProperty(name="Name",description="Name of NFT collection",default="")
    render_collection: bpy.props.StringProperty(name="Group",description="Collection to choose Traits from",default="Traits")
    render_filepath : bpy.props.StringProperty(name="Image Filepath",description="Filepath to save images to",default="",subtype="DIR_PATH")
    json_filepath : bpy.props.StringProperty(name="Json Filepath",description="Filepath to save JSON files to",default="",subtype="DIR_PATH")
    
    
    
    
def render(context,amount,collection_name,filepath,render_name,jsonfilepath):
    Items = bpy.data.collections[collection_name].children


    for key in Items.keys():
        objects = [obj.name for obj in bpy.data.collections[key].all_objects]
        for object in objects:
            bpy.data.objects[object].hide_render = True

    for x in range(amount):
        traitsdict = {}
        render_path = "//"
        character_ray = []
        for key in Items.keys():
            rarityweights = [y.get("Rarity",1) for y in bpy.data.collections[key].all_objects]
            collection = bpy.data.collections[key].all_objects
            ran_choice = random.choices(collection,weights=rarityweights,k=1)
            print(ran_choice[0].get("Rarity",1))
            character_ray.append(bpy.data.objects[ran_choice[0].name])
            traitsdict[key] = ran_choice[0].name
        for item in character_ray:
            print(item.name)
            item.hide_render = False
        file = os.path.join(filepath, f"{render_name}_{x}")
        bpy.context.scene.render.filepath = file
        bpy.ops.render.render( write_still=True,use_viewport=True)
        CreateJson(traitsdict,jsonfilepath,x,render_name)
        for item in character_ray:
            item.hide_render = True

class renderOperator(bpy.types.Operator):
    """Render images and export JSON files"""
    bl_idname = "object.nft_render"
    bl_label = "Nanaimo"


    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        props = context.scene.NanaimoProps
        render(context,props.render_amount,props.render_collection,props.render_filepath,props.render_name,props.json_filepath)
        return {'FINISHED'}


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Nanaimo"
    bl_idname = "SCENE_PT_RENDER"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nanaimo"

    def draw(self, context):
        
        layout = self.layout

        scene = context.scene
        props = scene.NanaimoProps


        layout.label(text=" Settings:")
        

        row = layout.row()
        sub = row.row()
        row.prop(props,"render_name")
        row = layout.row()
        
        op = row.prop(props,"render_amount")
        row = layout.row()
        row.prop(props,"render_collection", icon="OUTLINER_COLLECTION")

        row = layout.row()
        row.prop(props,"render_filepath")
        row = layout.row()
        row.prop(props,"json_filepath")
   
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.nft_render", text = "Render")

def register():
    bpy.utils.register_class(NanaimoPropertyGroup)
    bpy.types.Scene.NanaimoProps = bpy.props.PointerProperty(type=NanaimoPropertyGroup)
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(renderOperator)


def unregister():
    del bpy.types.Scene.NanaimoProps
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(renderOperator)
    


if __name__ == "__main__":
    register()
