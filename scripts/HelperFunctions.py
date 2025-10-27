import sys
# change path to your scripts folder
sys.path.append("./scripts")
from mathutils import Vector, Euler
from Brick import Brick, Orientation
from enum import Enum
import bpy
import numpy as np
import binvox_rw
import scipy.ndimage

class Components(Enum):
    main_model = 0
    wheel_back_left = 1
    wheel_back_right = 2
    wheel_front_left = 3
    wheel_front_right = 4
    light_front_left = 5
    light_front_right = 6
    light_rear_left = 7
    light_rear_right = 8
    cabin = 9

# returns an adjusted voxel_grid (components voxels are marked filled so normal bricks don't spawn there) and
# a components_grid where each voxel contains a specific car component ID that it represents
def check_each_voxel(voxel_grid, components_grid):
    components = [child_object for child_object in bpy.context.scene.objects[0].children_recursive]

    number_of_emptied = 0

    for x in range(voxel_grid.shape[0]):
        for y in range(voxel_grid.shape[1]):
            for z in range(voxel_grid.shape[2]):
                # no need to check voxels that are not in the model
                if voxel_grid[x, y, z] == 0:
                    continue

                voxel_center = Vector((x + 0.5, y + 0.5, (z + 0.5) * 0.4))
                
                for component in components:
                    # mark the voxel as filled if it is inside the mesh of a component
                    if is_voxel_inside_object(voxel_center, component):
                        voxel_grid[x, y, z] = 0
                        components_grid[x, y, z] = Components[component.name].value
                        number_of_emptied += 1
                        break
                       
    print(f"NUMBER OF EMPTIED VOXELS TO ACCOMMODATE CAR COMPONENTS: {number_of_emptied}")

    return voxel_grid, components_grid

# creates the collections that will contain all the different car components
def create_collections():
    # delete the Collection that is defaulte
    collection_to_delete = bpy.data.collections.get("Collection")
    if collection_to_delete is not None:
        bpy.data.collections.remove(collection_to_delete)

    # create bricks collection
    new_collection = bpy.data.collections.new("Bricks")
    bpy.context.scene.collection.children.link(new_collection)

    # create wheels collection
    new_collection = bpy.data.collections.new("Wheels")
    bpy.context.scene.collection.children.link(new_collection)

    # create the invisible objects collection
    new_collection = bpy.data.collections.new("Invisible")
    bpy.context.scene.collection.children.link(new_collection)

    # create the other collection
    new_collection = bpy.data.collections.new("Other")
    bpy.context.scene.collection.children.link(new_collection)

    # create the car collection
    new_collection = bpy.data.collections.new("Car")
    bpy.context.scene.collection.children.link(new_collection)

# returns all 8 corner points (locations) of each voxel
def get_voxel_corners(voxel_center, voxel_size):
    half_size = voxel_size / 2
    corners = []
    
    for dx in [-half_size, half_size]:
        for dy in [-half_size, half_size]:
            for dz in [-half_size, half_size]:
                corner = voxel_center + Vector((dx, dy, dz * 0.4))
                corners.append(corner)
    
    return corners

# returns True if a voxel is inside an object or False if it isn't
def is_voxel_inside_object(voxel_center, obj):
    # transform voxel center to the local space
    local_origin = obj.matrix_world.inverted() @ voxel_center
    
    # directions to ray cast in local space (3 directions works better than 6 idk why)
    directions = [
        Vector((1, 0, 0)),
        Vector((0, 1, 0)),
        Vector((0, 0, 1))
    ]
    
    voxel_corners = get_voxel_corners(voxel_center, 1)

    for corner in voxel_corners:
        local_origin = obj.matrix_world.inverted() @ corner
        hits = []
    
        # raycast from the voxel to the object in different directions
        for direction in directions:
            local_direction = obj.matrix_world.inverted().to_3x3() @ direction
            result, _, _, _ = obj.ray_cast(local_origin, local_direction.normalized())

            if result:
                # the voxel is in the object in that direction
                hits.append(obj)
            else:
                # the voxel is not in the object
                continue
            
        # if the rays in all directions hit the voxel, then the voxel should be filled
        if len(hits) == len(directions):
            return True
        
    return False
# adjusts the original voxel_grid to accomodate the higher windscreen if the current voxel_grid is too short
def adjust_original_voxel_grid(layer_handler, voxel_grid_copy):
    if voxel_grid_copy.shape[2] < layer_handler.voxel_grid.shape[2]:   
        height_difference = layer_handler.voxel_grid.shape[2] - voxel_grid_copy.shape[2]
        new_layer = np.zeros((layer_handler.voxel_grid.shape[0], layer_handler.voxel_grid.shape[1]))

        for i in range(height_difference):
            voxel_grid_copy = np.concatenate((voxel_grid_copy, new_layer[:, :, np.newaxis]), axis=2)

        return np.logical_or(voxel_grid_copy, layer_handler.voxel_grid)
    else:
        return voxel_grid_copy

# spawns the windscreen of the car
def spawn_windscreen(windscreen, layer_handler, main_model_material, cabin_length, cabin_height):
    def create_cabin():
        windscreen_x, windscreen_y, windscreen_z = map(int, windscreen.index_position)
        cut_off_indices = []
        
        # cut off the top part of the model if the windscreen is shorter
        if windscreen_z + windscreen.height < layer_handler.voxel_grid.shape[2]:
            cut_off_indices = [index for index in range(windscreen_z + windscreen.height, layer_handler.voxel_grid.shape[2])]

        # set of all indices that represent the empty cabin and the windscreen
        adjusted_cabin_indices = set()

        # get the indices where the windscreen is located
        for x_windscreen in range(windscreen.length):
            for y_windscreen in range(windscreen.width):
                for z_windscreen in range(windscreen.height):
                    adjusted_cabin_indices.add((x_windscreen + windscreen_x, y_windscreen + windscreen_y, z_windscreen + windscreen_z))

        # calculate limits of the empty cabin behind the windscreen
        right_x = windscreen_x + windscreen.length - 1
        left_x = windscreen_x + 1
        front_y = windscreen_y
        back_y = front_y - cabin_length
        top_z = windscreen_z + windscreen.height
        bottom_z = top_z - cabin_height
        	
        if bottom_z <= -1:
            print("The height of the cabin is too big!")
            return

        # add the indices of the empty cabin behind the windscreen
        for x_empty in range(left_x, right_x):
            for y_empty in range(back_y, front_y):
                for z_empty in range(bottom_z, top_z):
                    adjusted_cabin_indices.add((x_empty, y_empty, z_empty))
        
        # adjust the voxel_grid and the components_grid
        original_cabin_indices = np.argwhere(layer_handler.components_grid == Components.cabin.value)

        for original_index in original_cabin_indices:
            original_x, original_y, original_z = original_index

            if (original_x, original_y, original_z) not in adjusted_cabin_indices and original_z not in cut_off_indices:
                layer_handler.update_voxel_grid_index(original_x, original_y, original_z, False)
                layer_handler.components_grid[original_x, original_y, original_z] = 0   
        
        added_layers = []

        # increase the height of the model to the top of the windscreen if the model is too low
        for _ in range(layer_handler.voxel_grid.shape[2], windscreen_z + windscreen.height + 1):
            new_layer = np.zeros((layer_handler.voxel_grid.shape[0], layer_handler.voxel_grid.shape[1]))
            new_voxel_grid = np.concatenate((layer_handler.voxel_grid, new_layer[:, :, np.newaxis]), axis=2)
            new_components_grid = np.concatenate((layer_handler.components_grid, new_layer[:, :, np.newaxis]), axis=2)
            new_used_bricks_grid = np.concatenate((layer_handler.used_bricks_grid, new_layer[:, :, np.newaxis]), axis=2)

            layer_handler.voxel_grid = new_voxel_grid
            layer_handler.components_grid = new_components_grid
            layer_handler.used_bricks_grid = new_used_bricks_grid

            added_layers.append(new_voxel_grid.shape[2] - 1)
        
        # update the height of the voxel_grid
        layer_handler.z_size = layer_handler.voxel_grid.shape[2]

        # fill the voxels of the added layers according to the dimensions input into the function
        for z in added_layers:
            for x_added in range(windscreen.length):
                for y_added in range(1, windscreen.width):
                    connecting_height_threshold = 3
                    # check and fill voxels that are empty between the added layer and the original model
                    # check if any of the voxels below are filled and if they are fill the rest of the XY voxels in the Z direction
                    if any(layer_handler.voxel_grid[windscreen_x + x_added, windscreen_y - y_added, z - connecting_height_threshold : z]) == 1:
                        # fill the inbetween voxels
                        for i in range(1, connecting_height_threshold):
                            layer_handler.update_voxel_grid_index(windscreen_x + x_added, windscreen_y - y_added, z - i, False)
                            layer_handler.update_components_grid_index(windscreen_x + x_added, windscreen_y - y_added, z - i, Components.cabin.value)

                    layer_handler.update_voxel_grid_index(windscreen_x + x_added, windscreen_y - y_added, z, False)
                    layer_handler.update_components_grid_index(windscreen_x + x_added, windscreen_y - y_added, z, Components.cabin.value)

            
    cabin_voxels = np.argwhere(layer_handler.components_grid == Components.cabin.value)

    x_coordinates = cabin_voxels[:, 0]
    y_coordinates = cabin_voxels[:, 1]
    z_coordinates = cabin_voxels[:, 2]

    #print(f"X max = {x_coordinates.max()}, X min: {x_coordinates.min()}")
    x = round((x_coordinates.max() + x_coordinates.min()) / 2) - (windscreen.length / 2)
    y = y_coordinates.max() - windscreen.width
    z = z_coordinates.min()

    # spawn the windscreen and the roof bricks above it
    windscreen.spawn_windscreen(x, y, z)
    middle_brick = Brick(3, 2, 1, "3x2x1.glb")
    middle_brick.change_orientation(Orientation.NORTH_SOUTH)
    corner_brick_left = Brick(3, 3, 1, "3x3x1_roof_tile.glb", Orientation, True, custom_rotation_angle=(-180))
    corner_brick_right = Brick(3, 3, 1, "3x3x1_roof_tile.glb", Orientation, True, custom_rotation_angle=(-270))
    
    corner_brick_left.spawn_brick(x + corner_brick_left.length, y, z + windscreen.height, main_model_material)
    corner_brick_right.spawn_brick(x + windscreen.length - corner_brick_right.length, y, z + windscreen.height, main_model_material)
    middle_brick.spawn_brick((x + windscreen.length / 2) - 1, y, z + windscreen.height, main_model_material)

    # only keep the voxels that represent the empty cabin/windscreen filled
    create_cabin()

# spawns the wheel of the car
def spawn_wheels(connecting_brick, layer_handler, wheel_bricks, brick_texture):
    def calculate_connecting_brick_spawn_position(wheel_center, voxel_grid):
        x_index = int(round(wheel_center.x))
        y_index = int(round(wheel_center.y) - connecting_brick.width / 2)
        z_index = int(round(wheel_center.z * 2.5)) - 1

        # adjust the brick placement (in the X axis) depending on the side of the car
        if x_index > voxel_grid.shape[0] / 2:
            x_index -= connecting_brick.length + 1          
        else:
            x_index += 1

        # update the global grids
        layer_handler.update_voxel_grid(connecting_brick, x_index, y_index, z_index)
        layer_handler.update_used_bricks_grid(connecting_brick, x_index, y_index, z_index)
        determine_connected_bricks(layer_handler, connecting_brick)
        # POGLEJ ZAKVA MA TAPRU SPAWNAN BRICK ORIGIN NA SRED FOR SOME REASON

        return x_index, y_index, z_index

    # get all wheels from the scene
    parent_object = bpy.context.scene.objects[0]
    wheels = [child_object for child_object in parent_object.children_recursive if "wheel_" in child_object.name]

    connecting_brick_positions = []
    origin_global_positions = []
    closest_wheels = []

    for wheel in wheels:
        # unparent the wheel component from the parent (but keep its global position intact)
        wheel.select_set(True)
        #bpy.context.view_layer.objects.active = wheel
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # set the origin of the component to the center of said component
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        wheel.select_set(False)
        # get the wheel origin in world space (global)
        origin_global_position = wheel.matrix_world @ Vector((0, 0, 0))
        origin_x, origin_y, origin_z = origin_global_position

        # change the orientation of the brick if necessary
        if connecting_brick.length > connecting_brick.width and connecting_brick.orientation == Orientation.EAST_WEST:
            connecting_brick.change_orientation(Orientation.NORTH_SOUTH)

        # calculate the spawn position of the connecting brick and add them to the spawning list
        connecting_brick_positions.append((calculate_connecting_brick_spawn_position(origin_global_position, layer_handler.voxel_grid)))

        #origin_z = (z * 0.4) + 0.8
        origin_global_positions.append((origin_x, origin_y, origin_z))

        # get the selected cylinder's diameter (1 lego unit = 8mm (the actual wheels have diameters in mm))
        wheel_bounding_box = wheel.bound_box
        diameter = (wheel_bounding_box[2][1] - wheel_bounding_box[0][1]) * 8
        width = (wheel_bounding_box[4][0] - wheel_bounding_box[0][0]) * 8

        # find the best fitting wheel
        suitable_wheels = [wheel for wheel in wheel_bricks.values() if wheel.diameter <= diameter]

        if not suitable_wheels:
            print(f"Error: No suitable wheel found!")
            return

        # first find the biggest still fitting wheel and then find the closest wheel (of that diameter) 
        # if there are multiple wheels with the same diameter
        closest_difference_wheel = min(suitable_wheels, key=lambda x: abs(x.diameter - diameter))
        closest_wheel = [wheel for wheel in suitable_wheels if wheel.diameter == closest_difference_wheel.diameter]
        
        if len(closest_wheel) > 1:
            closest_wheel = min(closest_wheel, key=lambda x: abs(x.width - width))
        else:
            closest_wheel = closest_wheel[0]

        # add the wheel to the list of wheels to spawn
        closest_wheels.append(closest_wheel)
    
    # spawn all 4 wheels with connecting components (pin, brick)
    for conecting_brick_position, origin, closest_wheel in zip(connecting_brick_positions, origin_global_positions, closest_wheels):
        # spawn the connecting brick
        x, y, z = conecting_brick_position
        connecting_brick.spawn_brick(x, y, z, brick_texture)

        # adjust the pin and wheel locations depending on the connecting brick location  
        fixed_location = (int(round(origin[0])), int(round(origin[1])), (z * 0.4) + 0.7)

        # spawn the pin and the wheel
        spawn_pin(fixed_location, layer_handler.voxel_grid, "pin1.glb")
        closest_wheel.spawn_wheel(fixed_location, layer_handler.voxel_grid)

# spawns the pin for the wheel
def spawn_pin(wheel_center, voxel_grid, filename):
    # import the brick file with the filepath
    bpy.ops.import_scene.gltf(filepath=f"C:\\FRI\\DIPLOMA\\Bricks\\glTF\\{filename}")
    
    # get the last imported object (the newly created brick)
    imported_object = bpy.context.selected_objects[0]

    # adjust the scale of the object
    imported_object.scale = (0.05, 0.05, 0.05) 
    imported_object.rotation_mode = "XYZ" 

    # extract the pin coordinates
    x, y, z = wheel_center

    # adjust the brick rotation (in the X axis) depending on the side of the car
    if x > voxel_grid.shape[0] / 2:   
        imported_object.rotation_euler = Euler((0, 0, 0), 'XYZ')
        x -= 1
    else:
        x += 1

    # move the object to a position
    imported_object.location = (x, y, z) 

    # link the pin to the other collection
    bpy.context.scene.collection.objects.unlink(imported_object)
    other_collection = bpy.data.collections.get("Other")
    other_collection.objects.link(imported_object)

# returns the shared subgrid between the two removed bricks, an empty grid of equal size and a mapping grid that converts
# local subgrid indices to global voxel_grid coordinates
def find_connection_points(disconnected_brick_id, neighboring_brick_id, used_bricks_grid):
    # get all the voxels of the two bricks from the global bricks grid
    disconnected_brick_voxels = np.argwhere(used_bricks_grid == disconnected_brick_id)
    neighboring_brick_voxels = np.argwhere(used_bricks_grid == neighboring_brick_id)

    aligned_voxels = set()

    for d in disconnected_brick_voxels:
        for n in neighboring_brick_voxels:
            # check if the bricks are alligned along the X or Y axis and that they have the same Z axis position
            if ((d[0] == n[0] or d[1] == n[1]) and d[2] == n[2]):
                # add all the voxels in a straight line if you would draw one through the neighbouring voxels of the two bricks
                # X axis
                if d[0] == n[0]:
                    aligned_voxels.update(
                        tuple(v) for v in disconnected_brick_voxels if v[0] == d[0] and v[2] == d[2]
                    )
                    aligned_voxels.update(
                        tuple(v) for v in neighboring_brick_voxels if v[0] == n[0] and v[2] == n[2]
                    )
                # Y axis
                elif d[1] == n[1]:
                    aligned_voxels.update(
                        tuple(v) for v in disconnected_brick_voxels if v[1] == d[1] and v[2] == d[2]
                    )
                    aligned_voxels.update(
                        tuple(v) for v in neighboring_brick_voxels if v[1] == n[1] and v[2] == n[2]
                    )

    # convert to a list
    aligned_voxels = np.array(list(aligned_voxels))

    if aligned_voxels.size > 0:
        x_min, y_min, z_min = aligned_voxels.min(axis=0)
        x_max, y_max, z_max = aligned_voxels.max(axis=0)
    else:
        x_min = 0
        y_min = 0
        z_min = 0
        x_max = 0
        y_max = 0
        z_max = 0

    global_locations_subgrid = []

    # get the ids of the brick that occupy the voxel and the voxel's global indices (in tuples)
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            for z in range(z_min, z_max + 1):
                if used_bricks_grid[x, y, z] != 0:
                    brick_id = used_bricks_grid[x, y, z]
                    voxel_indices = (x, y, z)
                    global_locations_subgrid.append((brick_id, voxel_indices))

    # create an empty grid of the same size (will be used in the convolution)
    empty_subgrid = np.ones((x_max - x_min + 1, y_max - y_min + 1, z_max - z_min + 1), dtype=int)

    # create a mapping subgrid to map the local empty_subgrid indices returned from convolution to the global voxel_grid
    mapping_subgrid = np.empty_like(empty_subgrid, dtype=object)

    for local_x, global_x in enumerate(range(x_min, x_max + 1)):
        for local_y, global_y in enumerate(range(y_min, y_max + 1)):
            for local_z, global_z in enumerate(range(z_min, z_max + 1)):
                mapping_subgrid[local_x, local_y, local_z] = (global_x, global_y, global_z)


    return global_locations_subgrid, empty_subgrid, mapping_subgrid

# returns all unique subgraphs (set of bricks) of bricks in the model
def find_brick_connection_subgraphs(used_bricks):
    visited_bricks = set()
    connected_subgraphs = []

    # depth-first search through the brick connections
    def dfs(brick, subgraph):
        visited_bricks.add(brick)
        subgraph.add(brick)
    
        # iterate and run dfs on all the brick's connected bricks
        for connected_brick in used_bricks[brick].connected_bricks:
            if connected_brick not in visited_bricks:
                dfs(connected_brick, subgraph)

    # run dfs() for all unvisited bricks
    for brick in used_bricks:
        if brick not in visited_bricks:
            subgraph = set()
            dfs(brick, subgraph)
            connected_subgraphs.append(subgraph)

    return connected_subgraphs

# adds the bricks connected and neighboring bricks to the correct lists
def determine_connected_bricks(layer_handler, used_brick, sloped=False):
    used_brick_indices = np.where(layer_handler.used_bricks_grid == used_brick.id)

    used_bricks = layer_handler.used_bricks
    used_bricks_grid = layer_handler.used_bricks_grid

    # check if any brick is connected to the used brick (for each voxel of the used brick)
    for layer in range(len(used_brick_indices[0])):
        x = used_brick_indices[0][layer]
        y = used_brick_indices[1][layer]
        z = used_brick_indices[2][layer]

        ### DETERMINES CONNECTED BRICKS ###
        if not sloped:
            # check for connected bricks above the added brick (within model bounds)
            if z + 1 < used_bricks_grid.shape[2]:
                above_id = used_bricks_grid[x, y, z + 1]

                # the brick cannot be nonexistent or the same brick (for thick bricks)
                if above_id != 0 and above_id != used_brick.id:
                    used_brick.connected_bricks.add(above_id)
                    # add the brick to the connected bricks
                    if above_id in used_bricks:
                        used_bricks[above_id].connected_bricks.add(used_brick.id)
                    
        # check for connected bricks below the added brick (within model bounds)
        if z - 1 >= 0:
            below_id = used_bricks_grid[x, y, z - 1]

            # the brick cannot be nonexistent or the same brick (for thick bricks)
            if below_id != 0 and below_id != used_brick.id:
                used_brick.connected_bricks.add(below_id)
                # add the brick to the connected bricks
                if below_id in used_bricks:
                    used_bricks[below_id].connected_bricks.add(used_brick.id)

        ### DETERMINES NEIGHBOURING BRICKS ###
        # check for neighbouring bricks above the added brick (within model bounds)
        if x + 1 < used_bricks_grid.shape[0]:
            right_id = used_bricks_grid[x + 1, y, z]

            # the brick cannot be nonexistent or the same brick (for thick bricks)
            if right_id != 0 and right_id != used_brick.id:
                used_brick.neighbouring_bricks.add(right_id)
                # add the brick to the connected bricks
                if right_id in used_bricks:
                    used_bricks[right_id].neighbouring_bricks.add(used_brick.id)
                    
        # check for neighbouring bricks below the added brick (within model bounds)
        if x - 1 >= 0:
            left_id = used_bricks_grid[x - 1, y, z]

            # the brick cannot be nonexistent or the same brick (for thick bricks)
            if left_id != 0 and left_id != used_brick.id:
                used_brick.neighbouring_bricks.add(left_id)
                # add the brick to the connected bricks
                if left_id in used_bricks:  
                    used_bricks[left_id].neighbouring_bricks.add(used_brick.id)

        # check for neighbouring bricks infront of the added brick (within model bounds)
        if y + 1 < used_bricks_grid.shape[1]:
            infront_id = used_bricks_grid[x, y + 1, z]

            # the brick cannot be nonexistent or the same brick
            if infront_id != 0 and infront_id != used_brick.id:
                used_brick.neighbouring_bricks.add(infront_id)
                # add the brick to the connected bricks
                if infront_id in used_bricks:
                    used_bricks[infront_id].neighbouring_bricks.add(used_brick.id)
                    
        # check for neighbouring bricks behind the added brick (within model bounds)
        if y - 1 >= 0:
            behind_id = used_bricks_grid[x, y - 1, z]

            # the brick cannot be nonexistent or the same brick
            if behind_id != 0 and behind_id != used_brick.id:
                used_brick.neighbouring_bricks.add(behind_id)
                # add the brick to the connected bricks
                if behind_id in used_bricks:
                    used_bricks[behind_id].neighbouring_bricks.add(used_brick.id)

# checks if a brick has the correct material (color) depending on what component of the car it should represents
def check_materials(layer_handler, materials, main_model_material):
    for brick_id, brick_reference in layer_handler.used_bricks.items():
        used_brick_indices = np.argwhere(layer_handler.used_bricks_grid == brick_id)

        # check how many components the brick represents
        components = set()

        for x, y, z in used_brick_indices:
            components.add(layer_handler.components_grid[x, y, z])

        # if the brick stretches over multiple components don't change it's material
        if len(components) > 1:
            continue

        # what component the brick represents
        current_component = Components(components.pop())

        # what material is currently applied to the brick
        current_material = brick_reference.material.name

        # check if the correct material is applied to the brick depending on it's component type
        if current_component in [Components.light_front_left, Components.light_front_right]:
            if current_material != "matte_yellow":
                materials["matte_yellow"].apply_to_brick_by_id(brick_id)
        elif current_component in [Components.light_rear_left, Components.light_rear_right]:
            if current_material != "matte_red":
                materials["matte_red"].apply_to_brick_by_id(brick_id)
        else:
            if current_material != main_model_material:
                main_model_material.apply_to_brick_by_id(brick_id)

# deletes the default objects that appear when unity is first opened
def delete_default_objects():
    # remove the 3 default Blender objects
    default_names = {"Cube", "Light", "Camera"}

    for obj_name in default_names:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

# moves the 3D model to the origin point of the scene
def move_main_object_to_starting_point(voxel_grid):
    # get the main (currently the only) object in the scene (the car model)
    obj = bpy.context.scene.objects[0]

    # find all the objects (including children of the main object) in the scene 
    objects_to_check = [obj] + list(obj.children_recursive)

    # find the min x, y and z values of the voxel_grid
    voxel_grid_indices = np.argwhere(voxel_grid == 1)

    min_x_voxel, min_y_voxel, min_z_voxel = voxel_grid_indices.min(axis=0)
    max_x_voxel, max_y_voxel, max_z_voxel = voxel_grid_indices.max(axis=0)

    # initialize the min x, y and z values of the car model
    min_x_model, min_y_model, min_z_model = float('inf'), float('inf'), float('inf')
    max_x_model, max_y_model, max_z_model = float('-inf'), float('-inf'), float('-inf')

    # find the min and max x, y and z values in the car model
    for object in objects_to_check:
        if object.type == 'MESH':
            vertices_world = [object.matrix_world @ v.co for v in object.data.vertices]
            min_x_model = min(min_x_model, *(v.x for v in vertices_world))
            min_y_model = min(min_y_model, *(v.y for v in vertices_world))
            min_z_model = min(min_z_model, *(v.z for v in vertices_world))

            max_x_model = max(max_x_model, *(v.x for v in vertices_world))
            max_y_model = max(max_y_model, *(v.y for v in vertices_world))
            max_z_model = max(max_z_model, *(v.z for v in vertices_world))
    
    # move the main object to align with the min (so the bottom left back part of the model is at (0, 0, 0))
    bpy.context.view_layer.objects.active = obj
    offset = Vector((min_x_model, min_y_model, min_z_model))
    obj.location -= offset

    # set the origin of the main object to the (0, 0, 0) point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')

    # scale the object to (mostly) allign with the voxel grid
    ### SCALE DEPENDING ON THE CAR ###
    # R8: 5.885
    # ferrari: 5.65
    # c_class: 5.4
    # g_class: 5.35
    # RS4: 5.6
    obj.scale = (5.885, 5.885, 5.885) 

    # apply the scale
    bpy.ops.object.transform_apply()

    # find the min and max x, y and z values in the scaled car model
    for object in objects_to_check:
        if object.type == 'MESH':
            vertices_world = [object.matrix_world @ v.co for v in object.data.vertices]
            min_x_model = min(min_x_model, *(v.x for v in vertices_world))
            min_y_model = min(min_y_model, *(v.y for v in vertices_world))
            min_z_model = min(min_z_model, *(v.z for v in vertices_world))

            max_x_model = max(max_x_model, *(v.x for v in vertices_world))
            max_y_model = max(max_y_model, *(v.y for v in vertices_world))
            max_z_model = max(max_z_model, *(v.z for v in vertices_world))

    # adjust the car model position so it alligns with it's voxel_grid counterpart
    voxel_grid_center_x = (min_x_voxel + max_x_voxel) / 2
    voxel_grid_center_y = (min_y_voxel + max_y_voxel) / 2     

    model_center_x = (min_x_model + max_x_model) / 2
    model_center_y = (min_y_model + max_y_model) / 2     

    offset_x = voxel_grid_center_x - model_center_x
    offset_y = voxel_grid_center_y - model_center_y

    obj.location.x += offset_x
    obj.location.y += offset_y
    obj.location.y -= 0.5

# loads the 3D model of a car into the scene and adjusts its hiearchy
def load_model():
    ### NAMES ### 
    # r8_components.glb
    # ferrari_components.glb
    # c_class_components.glb
    # g_class_components.glb
    # rs4_components.glb

    # import the model
    bpy.ops.import_scene.gltf(filepath="C:\\FRI\\DIPLOMA\\Binvox\\r8_components.glb")
    imported_object = bpy.context.selected_objects[0]
    
    # link the model and its children to the correct collection
    bpy.context.scene.collection.objects.unlink(imported_object)
    invisible_collection = bpy.data.collections.get("Car")
    invisible_collection.objects.link(imported_object)

    for child in imported_object.children_recursive:
        bpy.context.scene.collection.objects.unlink(child)
        invisible_collection = bpy.data.collections.get("Car")
        invisible_collection.objects.link(child)

# returns the voxelized 3D model as an NPArray
def voxelize_model():
    ### NAMES ###
    # r8_rescaled.binvox
    # ferrari_rescaled.binvox
    # c_class_rescaled.binvox
    # g_class_rescaled.binvox
    # rs4_rescaled.binvox

    # load the .binvox file
    with open("C:/FRI/DIPLOMA/Binvox/r8_rescaled.binvox", "rb") as f:
        model = binvox_rw.read_as_3d_array(f)

    # access the voxel data
    return model.data

# returns potential spawn positions for the brick
def apply_correlation(voxel_grid, brick):
    # create a kernel based on the brick dimensions
    kernel = brick.brick_kernel

    # correlate
    correlation_grid = scipy.ndimage.correlate(voxel_grid, kernel, mode='constant', cval=0, origin=brick.kernel_origin)

    # identify the available positions for the brick
    kernel_sum = kernel.sum()
    fitting_positions = np.argwhere(correlation_grid == kernel_sum)

    return fitting_positions

# returns potential spawn positions for the irregular brick
def apply_convolution(voxel_grid, brick):
    # create a kernel based on the brick dimensions
    kernel = brick.brick_kernel

    # convolve
    convolved_grid = scipy.ndimage.convolve(voxel_grid, kernel, mode='constant', cval=0, origin=brick.kernel_origin)

    # identify the available positions for the brick
    kernel_sum = kernel.sum()
    fitting_positions = np.argwhere(convolved_grid == kernel_sum)

    return fitting_positions

# clears all invisible (spawned bricks that are only used to make copies) bricks in the scene
def clear_invisible_bricks():
    collection_name = "Invisible"

    # get collection of invisible bricks
    collection = bpy.data.collections.get(collection_name)

    if collection:
        # unlink all objects and delete them
        for obj in list(collection.objects):
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.objects.remove(obj)

        # unlink the invisible collection from all parent collections
        for parent in bpy.data.collections:
            if collection.name in parent.children:
                parent.children.unlink(parent.children[collection.name])

        # remove the collection itself

        bpy.data.collections.remove(collection)
