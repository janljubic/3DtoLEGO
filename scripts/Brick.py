import sys
# change path to your scripts folder
sys.path.append("./scripts")
from mathutils import Euler
from pathlib import Path
import bpy
import numpy as np
from math import radians
from enum import Enum


# adds a bevel to each brick so they look closer to actual LEGO models (can crash Blender sometimes)
def add_bevel_to_brick(brick_object, bevel_value):
    # switch blender to edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # merge all the faces of the brick
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    
    # switch blender back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # add and apply the bevel modifier to the brick
    bevel_modifier = brick_object.modifiers.new(name="Bevel", type='BEVEL')
    bevel_modifier.width = bevel_value

class Windscreen:
    def __init__(self, length, width, height, filename):
        self.length = length
        self.width = width
        self.height = height
        self.index_position = None
        self.filename = filename
        self.windscreen_reference = None

    # spawns the windscreen on the input coordinates
    def spawn_windscreen(self, x, y, z):
        file_path = f"C:\\FRI\\DIPLOMA\\Bricks\\glTF\\{self.filename}"

        # check if the brick file exists
        if (Path(file_path).is_file()):
            # import the brick file with the filepath
            bpy.ops.import_scene.gltf(filepath=file_path)
            
            # select the imported object
            imported_object = bpy.context.selected_objects[0]
            
            # add the windscreen original object to the other collection
            bpy.context.scene.collection.objects.unlink(imported_object)
            other_collection = bpy.data.collections.get("Other")
            other_collection.objects.link(imported_object)
            
            # adjust the scale of the object
            imported_object.scale = (0.05, 0.05, 0.05) 
            imported_object.rotation_mode = "XYZ" 
            # move the object to the appropriate position
            imported_object.location = (x, y, z * 0.4) 

            # save the index position of the windscreen
            self.index_position = (x, y, z)
        else:
            print(f"File with the name '{self.filename}' doesn't exist!")

class Wheel:
    id = 0

    def __init__(self, diameter, width, filename):
        self.diameter = diameter
        self.width = width
        self.filename = filename
        self.wheel_reference = None

    # spawn the wheel and tire on the input coordinates
    def spawn_wheel(self, wheel_center, voxel_grid):
        # create a brick with a reference if one doesn't exist yet
        if self.wheel_reference == None:
            file_path = f"C:\\FRI\\DIPLOMA\\Bricks\\glTF\\{self.filename}"

            # check if the brick file exists
            if (Path(file_path).is_file()):
                # import the brick file with the filepath
                bpy.ops.import_scene.gltf(filepath=file_path)

                # get the last imported object (the newly created brick)
                imported_object = bpy.context.selected_objects[0]
                
                # add the original object to the invisible collection
                bpy.context.scene.collection.objects.unlink(imported_object)
                invisible_collection = bpy.data.collections.get("Invisible")
                invisible_collection.objects.link(imported_object)

                # move the object to a position and set the scale
                imported_object.scale = (0.05, 0.05, 0.05) 
                
                # save a reference to the preloaded brick
                self.wheel_reference = imported_object

                # hide the brick in the scene
                imported_object.hide_set(True)

                # duplicate the preloaded brick
                duplicated_wheel = self.wheel_reference.copy()
                duplicated_wheel.data = self.wheel_reference.data.copy()
            else:
                print(f"File with the name '{self.filename}' doesn't exist!")

        # duplicate the preloaded brick
        duplicated_wheel = self.wheel_reference.copy()
        duplicated_wheel.data = self.wheel_reference.data.copy()

        # link the wheel to the wheels collection
        wheels_collection = bpy.data.collections.get("Wheels")
        wheels_collection.objects.link(duplicated_wheel)

        # set the position,rotation and adjust the scale of the object
        duplicated_wheel.rotation_mode = "XYZ"

        # extract the wheel coordinates
        x, y, z = wheel_center

        # adjust the brick rotation (in the X axis) depending on the side of the car
        if x > voxel_grid.shape[0] / 2:   
            duplicated_wheel.rotation_euler = Euler((0, 0, radians(90)), 'XYZ')
            x += 0.1
        else:
            duplicated_wheel.rotation_euler = Euler((0, 0, radians(270)), 'XYZ')
            x -= 0.1
        
        # move the object to a position
        duplicated_wheel.location = (x, y, z) 

class BrickType(Enum):
    THICK = 0
    THIN = 1

class Smooth(Enum):
    NONE = 0
    SLOPED = 1
    NORMAL = 2

class Color(Enum):
    NONE = (0, 0, 0, 0)
    RED = (1, 0, 0, 1)
    GREEN = (0, 1, 0, 1)
    BLUE = (0, 0, 1, 1)
    YELLOW = (1, 1, 0, 1)
    CYAN = (0, 1, 1, 1)
    MAGENTA = (1, 0, 1, 1)
    ORANGE = (1, 0.5, 0, 1)
    PURPLE = (0.5, 0, 0.5, 1)
    PINK = (1, 0.75, 0.8, 1)
    BROWN = (0.6, 0.3, 0, 1)
    BLACK = (0, 0, 0, 1)
    LIME = (0.7, 1, 0, 1)
    TEAL = (0, 0.5, 0.5, 1)
    VIOLET = (0.56, 0, 1, 1)
    GOLD = (1, 0.84, 0, 1)
    TURQUOISE = (0.25, 0.88, 0.82, 1)
    CRIMSON = (0.86, 0.08, 0.24, 1)
    INDIGO = (0.29, 0, 0.51, 1)
    NAVY = (0, 0, 0.5, 1)
    CHARTREUSE = (0.5, 1, 0, 1)

class Orientation(Enum):
    NORTH_SOUTH = 0
    EAST_WEST = 1
    NONE = 2

    # returns an untested orientation (for symmetrical bricks)
    def get_untested_orientation(tried_orientations):
        if Orientation.NORTH_SOUTH not in tried_orientations:
            return Orientation.NORTH_SOUTH
        elif Orientation.EAST_WEST not in tried_orientations:
            return Orientation.EAST_WEST

class SlopedOrientation(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

    # returns an untested orientation (for non symmetrical bricks)
    def get_untested_orientation(tried_orientations):
        if SlopedOrientation.NORTH not in tried_orientations:
            return SlopedOrientation.NORTH
        elif SlopedOrientation.SOUTH not in tried_orientations:
            return SlopedOrientation.SOUTH
        elif SlopedOrientation.EAST not in tried_orientations:
            return SlopedOrientation.EAST
        elif SlopedOrientation.WEST not in tried_orientations:
            return SlopedOrientation.WEST

class Material:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.material = self.create_material()
    
    # creates a material for the brick
    def create_material(self):
        material = bpy.data.materials.new(name=self.name)
        material.use_nodes = True
        nodes = material.node_tree.nodes

        # access the Principled BSDF shader node
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            # set the color using the desired RGBA value
            bsdf.inputs["Base Color"].default_value = self.color.value
        
        return material
    
    # applies the created material to the brick (as ID)
    def apply_to_brick_by_id(self, brick_id):
        brick = bpy.data.objects[str(brick_id)]
        brick.data.materials[0] = self.material

    # applies the created material to the brick (as object)
    def apply_to_object(self, obj):
        obj.data.materials[0] = self.material
                
class Brick:
    id = 0

    def __init__(self, length, width, height, filename, orientation=Orientation, smooth_brick=Smooth.NONE,
                  custom_kernel=None, custom_kernel_origins=None, custom_rotation_angle=None):
        self.length = length
        self.width = width
        self.height = height
        self.filename = filename
        self.brick_reference = None
        self.orientation = self.determine_orientation(orientation)
        self.rotation_angle = self.create_starting_rotation_angle(orientation, custom_rotation_angle)
        self.custom_kernel = custom_kernel
        self.brick_kernel = self.create_brick_kernel() if orientation is Orientation else self.create_irregular_brick_kernel()
        self.custom_kernel_origins = custom_kernel_origins
        self.kernel_origin = self.calculate_kernel_origin() if orientation is Orientation else self.calculate_sloped_kernel_origin()
        self.connected_bricks = set()
        self.neighbouring_bricks = set()
        self.id = Brick.id
        self.smooth_brick = smooth_brick
        self.material = None

    # adjusts the brick rotation to a custom angle (depending on its type)
    def create_starting_rotation_angle(self, orientation, custom_rotation_angle):
        # custom rotation angle for the roof bricks
        if custom_rotation_angle is not None:
            return custom_rotation_angle
        else:
            return -180 if orientation is Orientation else -90
    
    # applies the default orientation to the brick depending on the brick type
    def determine_orientation(self, orientation):
        # orientation of the rectangular (normal) bricks
        if orientation is Orientation:
            return Orientation.EAST_WEST if self.length != self.width else Orientation.NONE
        # orientation for the non rectangular (sloped) bricks
        elif orientation is SlopedOrientation:
            return SlopedOrientation.NORTH

    # returns the offset for the brick kernel
    def calculate_kernel_origin(self):
        # calculates the center index for each dimension
        def calculate_dimension_origin(dimension_size):
            if dimension_size % 2 == 0:
                # even size -> center is one index to the left of the middle index
                return dimension_size // 2 - 1
            else:
                # odd size -> center is the middle index
                return dimension_size // 2
            
        x = calculate_dimension_origin(self.length)
        y = calculate_dimension_origin(self.width)
        z = calculate_dimension_origin(self.height)

        return (x, y, z)

    # creates a kernel for the brick
    def create_brick_kernel(self):
        return np.ones((self.length, self.width, self.height), dtype=np.int64)

    # returns the offset for the irregular brick kernel
    def calculate_sloped_kernel_origin(self):
        if len(self.custom_kernel_origins) < 4:
            print(f"Error! Not enough custom kernel origins present for brick {self.filename}")
            return (0, 0, 0)

        # get the custom kernel origin for a specific orientation
        if self.orientation == SlopedOrientation.NORTH:
            return self.custom_kernel_origins[0]
        elif self.orientation == SlopedOrientation.SOUTH:
            return self.custom_kernel_origins[1]
        elif self.orientation == SlopedOrientation.WEST:
            return self.custom_kernel_origins[2]
        elif self.orientation == SlopedOrientation.EAST:
            return self.custom_kernel_origins[3]

    # creates a kernel for the irregular (sloped) brick
    def create_irregular_brick_kernel(self):
        # brick is rotated north (default) or has the same width and length
        if self.length > self.width or self.length == self.width:
            temp_kernel = np.zeros((self.length, self.width, self.height), dtype=np.int64)
        # brick is rotated west (create the kernel in the same direction as the north one because we transpose it later)
        else:
            temp_kernel = np.zeros((self.width, self.length, self.height), dtype=np.int64)

        # nark the correct voxels as filled in the kernel
        if self.custom_kernel is not None:
            for x, y, z in self.custom_kernel:
                temp_kernel[x, y, z] = 1

        kernel = temp_kernel

        # transpose the kernel to accommodate east/west orientation
        if self.orientation in [SlopedOrientation.EAST, SlopedOrientation.WEST]:
            kernel = np.transpose(temp_kernel, (1, 0, 2))
    
        # flip the kernel for the mirrored orientations
        if self.orientation == SlopedOrientation.SOUTH:
            kernel = np.flip(kernel, axis=0)  # flip the kernel on the X axis
        elif self.orientation == SlopedOrientation.EAST:
            kernel = np.flip(kernel, axis=1)  # flip the kernel on the Y axis
            
        return kernel

    # rotates the brick to a new orientation
    def change_orientation(self, new_orientation):
        if self.orientation == Orientation.NONE:
            print("Orientation error: The brick has the same length and width!")
            return

        # if the new orientation is valid change the required values
        if new_orientation != self.orientation:
            self.length, self.width = self.width, self.length 
            self.orientation = new_orientation 
            self.rotation_angle = -90 if new_orientation == Orientation.NORTH_SOUTH else -180
            self.kernel_origin = self.calculate_kernel_origin()
            self.brick_kernel = self.create_brick_kernel()
        else:
            print("Orientation error: Current orientation is the same!")

    # rotates the irregular (sloped) brick to a new orientation
    def change_sloped_orientation(self, new_orientation):
        if self.orientation == Orientation.NONE:
            print("Orientation error: The brick has the same length and width!")
            return 
        
        # rotate the brick depending on the input orientation
        if new_orientation != self.orientation:
            if new_orientation == SlopedOrientation.NORTH:
                if self.orientation != SlopedOrientation.SOUTH:
                    self.length, self.width = self.width, self.length 
                self.orientation = new_orientation 
                self.rotation_angle = -90
            elif new_orientation == SlopedOrientation.SOUTH:
                if self.orientation != SlopedOrientation.NORTH:
                    self.length, self.width = self.width, self.length 
                self.orientation = new_orientation 
                self.rotation_angle = -270
            elif new_orientation == SlopedOrientation.EAST:
                if self.orientation != SlopedOrientation.WEST:
                    self.length, self.width = self.width, self.length 
                self.orientation = new_orientation 
                self.rotation_angle = -180
            elif new_orientation == SlopedOrientation.WEST:
                if self.orientation != SlopedOrientation.EAST:
                    self.length, self.width = self.width, self.length 
                self.orientation = new_orientation 
                self.rotation_angle = 0

            # adjust the kernel and kernel origin of the rotated brick
            self.kernel_origin = self.calculate_sloped_kernel_origin()
            self.brick_kernel = self.create_irregular_brick_kernel()
        else:
            print("Orientation error: Current orientation is the same!")

    # spawns the brick in the scene
    def spawn_brick(self, x, y, z, material):
        # create a brick with a reference if one doesn't exist yet
        if self.brick_reference == None:
            file_path = f"C:\\FRI\\DIPLOMA\\Bricks\\glTF\\{self.filename}"

            # check if the brick file exists
            if (Path(file_path).is_file()):
                # import the brick file with the filepath
                bpy.ops.import_scene.gltf(filepath=file_path)

                # get the last imported object (the newly created brick)
                imported_object = bpy.context.selected_objects[0]

                #add_bevel_to_brick(imported_object, 0.15)

                # add the original object to the invisible collection
                bpy.context.scene.collection.objects.unlink(imported_object)
                invisible_collection = bpy.data.collections.get("Invisible")
                invisible_collection.objects.link(imported_object)

                # move the object to a position and set the scale
                imported_object.location = (x, y, z) 
                imported_object.scale = (0.05, 0.05, 0.05) 
                
                # save a reference to the preloaded brick
                self.brick_reference = imported_object

                # hide the brick in the scene
                imported_object.hide_set(True)
            else:
                print(f"File with the name '{self.filename}' doesn't exist!")
                return

        # set a new brick id
        Brick.id += 1

        if (Brick.id == 8):
            x = 5

        # duplicate the preloaded brick
        duplicated_brick = self.brick_reference.copy()
        duplicated_brick.data = self.brick_reference.data.copy()
        duplicated_brick.name = str(Brick.id)

        material.apply_to_object(duplicated_brick)

        # set the position and rotation
        if self.orientation in Orientation:
            if self.orientation == Orientation.EAST_WEST:
                duplicated_brick.location = (x, y, z * 0.4)
            elif self.orientation == Orientation.NORTH_SOUTH:
                duplicated_brick.location = (x + self.length, y, z * 0.4)
            else:
                duplicated_brick.location = (x, y, z * 0.4)
        elif self.orientation in SlopedOrientation:
            if self.orientation == SlopedOrientation.NORTH:
                duplicated_brick.location = (x, y, z * 0.4)
            elif self.orientation == SlopedOrientation.SOUTH:
                duplicated_brick.location = (x + self.length, y + self.width, z * 0.4)
            elif self.orientation == SlopedOrientation.EAST:
                duplicated_brick.location = (x, y + self.width, z * 0.4)
            elif self.orientation == SlopedOrientation.WEST:
                duplicated_brick.location = (x + self.length, y, z * 0.4)
                

        duplicated_brick.rotation_mode = "XYZ"
        duplicated_brick.rotation_euler = Euler((0, 0, radians(self.rotation_angle)), 'XYZ')
        
        # link the brick to the bricks collection
        bricks_collection = bpy.data.collections.get("Bricks")
        bricks_collection.objects.link(duplicated_brick)

        return Brick(self.length, self.width, self.height, self.filename)
    
    # removes the brick from the scene
    def remove_brick(self):
        for object in bpy.data.objects:
            if object.name == str(self.id):
                bpy.data.objects.remove(object, do_unlink=True)
                break
        else:

            print(f"No brick found with ID {self.id}.")
