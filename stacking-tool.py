##############################################################################
###                            Stacking-Tool                               ###
###                                                                        ###
###       A script for stacking multiple meshes ontop of each other        ###
###                       Written by: Florian Wolf                         ###
###                                                                        ###
##############################################################################

bl_info = {
    "name": "Stacking Tool",
    "author": "Florian Wolf, flowo.de",
    "version": (1,0,0),
    "blender": (2, 90, 0),
    "category": "Object",
    "description": "Stack multiple selected meshes into a desired direction. You can randomly rotate or reorder the stacked objects using seeds or create an offset between each object.",
}

import bpy
import math
import numpy
import random
from mathutils import Matrix, Vector
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty


# this class contains the actual addon logic
class StackObjects(bpy.types.Operator):
    """Stack multiple selected meshes ontop of each other. You can randomly rotate or reorder the stacked objects using seeds or create an offset between each object. The active selected object (yellow outline) will the the base of the stack."""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.stacking_tool"      # Unique identifier for buttons and menu items to reference.
    bl_label = "Stack Objects"              # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}       # Enable undo for the operator.


    def axis_type_callback(self, context):
        return (
            ('X', 'X', 'Objects will be transformed along the X-Axis'),
            ('Y', 'Y', 'Objects will be transformed along the Y-Axis'),
            ('Z', 'Z', 'Objects will be transformed along the Z-Axis'),
        )

    # properties exposed in the tool popup
    stacking_axis_type : EnumProperty(
        items=axis_type_callback,
        name="Axis",
        description="The axis the selected objects should be stacked on",
        default=2,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None
    )

    rotation_axis_type : EnumProperty(
        items=axis_type_callback,
        name="Axis",
        description="The axis the selected objects should be locally rotated around",
        default=2,
    )

    center_objects = BoolProperty(  
        name="Center Objects on Axis",  
        default=True,  
        description="Align all objects with the active object, so that they are all directly ontop of each other"  
    ) 

    offset = FloatProperty(  
        name="Offset",  
        default=0,  
        subtype='DISTANCE',  
        unit='LENGTH',  
        description="The distance between the stacked objects"  
    ) 

    shuffle_objects_seed = IntProperty(  
        name="Stacking Order Seed",  
        min=1,
        max=10000,
        default=1,  
        description="Shuffles the objects, so that the objects will have a different position in the stack"  
    )

    enable_rotation = BoolProperty(  
        name="Enable Rotation",  
        default=True,  
        description="Randomly rotate all objects around the specified rotation axis"  
    ) 

    rotate_base = BoolProperty(  
        name="Rotate Active Base Object",  
        default=True,  
        description="Rotate the base as well as the top objects"  
    ) 
   
    rotation_angle_step = FloatProperty(  
        name="Rotation Angle Step",  
        default=math.radians(90),
        unit="ROTATION",
        description="The angle which objects should get randomly rotated at"  
    )  
    
    rotation_seed = IntProperty(  
        name="Rotation Seed",  
        min=1,
        max=10000,
        default=1,  
        description="Different seeds result in different rotations"  
    )  

    # get the furthest vertex position of an object along the specified axis in world space
    def get_top_location(self, obj, axis_type):
        axis_maximum = self.get_global_extremes(obj, axis_type)[1]
        if axis_type == 'X':
            return Vector((axis_maximum, obj.location.y, obj.location.z))
        elif axis_type == 'Y':
            return Vector((obj.location.x, axis_maximum, obj.location.z))
        elif axis_type == 'Z':
            return Vector((obj.location.x, obj.location.y, axis_maximum))

    # Find the lowest and highest Z value amongst the object's verticies in world space
    def get_global_extremes(self, obj, axis_type):
        #mw = obj.matrix_world      # object's world matrix
        #glob_vertex_coordinates = [ mw @ v.co for v in obj.data.vertices ] # Global coordinates of vertices

        glob_vertex_coordinates = [(obj.matrix_world @ v.co) for v in obj.data.vertices]

        print(obj, "axis_type:", axis_type, "globalCoords: ", glob_vertex_coordinates)

        minimum = 0
        maximum = 0
        if axis_type == 'X':
            minimum = min( [ co.x for co in glob_vertex_coordinates ] )  
            maximum = max( [ co.x for co in glob_vertex_coordinates ] )  
        elif axis_type == 'Y':
            minimum = min( [ co.y for co in glob_vertex_coordinates ] )  
            maximum = max( [ co.y for co in glob_vertex_coordinates ] )  
        elif axis_type == 'Z':
            minimum = min( [ co.z for co in glob_vertex_coordinates ] )  
            maximum = max( [ co.z for co in glob_vertex_coordinates ] )  
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!")
            print("ERROR")
        return [minimum, maximum] # lowest point on our axis, highest point on our axis


    # get the value of a mathutils.Vector given a axis type enum value
    def get_vector_value_by_axis(self, vector, axis_type):
        if axis_type == 'X':
            return vector.x
        elif axis_type == 'Y':
            return vector.y
        elif axis_type == 'Z':
            return vector.z

    # addon lifecycle method - only if poll returns True the tool can be used from the 'Object' menu. If it returns False, it is greyed out in the 'Object' menu
    @classmethod
    def poll(cls, context):
        only_meshes_selected = True
        for obj in context.selected_objects:
            if obj.type != "MESH":
                only_meshes_selected = False
                break
        return context.object.select_get() and len(context.selected_objects) > 1 and only_meshes_selected and context.object.mode == "OBJECT"    # only allow using this tool if multiple meshes are selected, of which one is actively selected (yellow) and we are currently in 'Object' mode

    # addon lifecycle method - styles the tool panel 
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box_row = box.row()
        box_row.label(text="Stacking")
        box_row.prop(self, "stacking_axis_type")
        box.prop(self, "center_objects")
        box_row = box.row()
        box_row.prop(self, "offset")
        box_row.prop(self, "shuffle_objects_seed")


        box_2 = layout.box()
        box_2_row = box_2.row()
        box_2_row.label(text="Rotation")
        box_2_row.prop(self, "rotation_axis_type")
        box_2.prop(self, "enable_rotation")
        box_2.prop(self, "rotate_base")

        box_2_row_2 = box_2.row()
        box_2_row_2.prop(self, "rotation_angle_step")
        box_2_row_2.prop(self, "rotation_seed")

    # addon lifecycle method - adds an "OK" button to the tool panel. When clicked or values are changed after clicking, execute is invoked
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360)

    # addon lifecycle method - called when running the operator, i.e. by the panel dialog
    def execute(self, context):
        print("---")
        # get the active object
        active_obj = context.active_object

        # rotate objects
        # we need seperate loops for rotating and stacking. If we were to rotate and stack in the same loop, the reordering would change the indexes of the objects, which would change their rotations whenever we reorder.
        obj_id = 0
        objects_count = len(context.selected_objects)
        for obj in context.selected_objects:
            if self.enable_rotation and (obj != active_obj or (obj == active_obj and self.rotate_base)):
                # rotate by our seeded angle around our specified axis
                seededRandomAngle = self.rotation_angle_step * random.Random(self.rotation_seed + obj_id).randint(0, 360)

                if self.rotation_axis_type == 'X':
                    obj.rotation_euler[0] = seededRandomAngle
                elif self.rotation_axis_type == 'Y':
                    obj.rotation_euler[1] = seededRandomAngle
                elif self.rotation_axis_type == 'Z':
                    obj.rotation_euler[2] = seededRandomAngle

            obj_id += objects_count * 100      # increment an index, which is used for the seeded rotation to get unique, but reproducable rotations for each object. Make sure to increment it a lot, so that when changing seeds there is no doubeling of rotations

        # apply the new rotations. If this is not done, then the global vertex positions are not updated after rotating and objects will be positioned disregarding their new rotation.
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=False)

        # reorder objects before stacking them
        reordered_selected_objects = context.selected_objects
        random.Random(self.shuffle_objects_seed).shuffle(reordered_selected_objects)

        # get the furthest location of the active object along our axis
        stack_length = self.get_vector_value_by_axis(self.get_top_location(active_obj, self.stacking_axis_type), self.stacking_axis_type) + self.offset

        # stack objects
        for obj in reordered_selected_objects:
            # skip the active object, since we do not need to edit its location
            if obj != active_obj:
                # Calculate the objects height
                # obj.dimensions are only correct for non-rotated objects. For rotated objects, we need to calculate the height manually by getting the position of the highest/lowest verticies.
                extremes = self.get_global_extremes(obj, self.stacking_axis_type)
                length = extremes[1] - extremes[0]

                print(obj.name, "extremes: ", extremes)

                # set the location by offsetting the object using its origin and extremes, so that it "lays" ontop of the last element
                new_location = obj.location
                if self.stacking_axis_type == 'X':
                    new_location.x =  stack_length + (obj.location.x - extremes[0])
                    if self.center_objects:
                        new_location.y = active_obj.location.y
                        new_location.z = active_obj.location.z
                elif self.stacking_axis_type == 'Y':
                    new_location.y =  stack_length + (obj.location.y - extremes[0])
                    if self.center_objects:
                        new_location.x = active_obj.location.x
                        new_location.z = active_obj.location.z
                elif self.stacking_axis_type == 'Z':
                    new_location.z =  stack_length + (obj.location.z - extremes[0])
                    if self.center_objects:
                        new_location.x = active_obj.location.x
                        new_location.y = active_obj.location.y
                obj.location = new_location

                # save the new stack length for the next element in the collection, so that it can append it it
                stack_length += length + self.offset

        return {'FINISHED'}            # Lets Blender know the operator finished successfully. 
            
            
# addon lifecycle method - Adds a button the the "Objects" menu to open the tool panel
def add_object_button(self, context):  
    self.layout.operator(  
        StackObjects.bl_idname,  
        text="Stack Objects",  
        icon='SORTSIZE')  

# addon lifecycle method - Registers the addon and its functions
def register():
    bpy.utils.register_class(StackObjects)
    bpy.types.VIEW3D_MT_object.append(add_object_button)  

# addon lifecycle method - Unregisters the addon and its functions
def unregister():
    bpy.utils.unregister_class(StackObjects)
    
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
