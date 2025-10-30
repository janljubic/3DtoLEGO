import sys
# change path to your scripts folder
sys.path.append("./scripts")
import time
import numpy as np
import random
from Brick import Brick, Wheel, Color, BrickType, Smooth, Material, Windscreen
from Brick import Orientation, SlopedOrientation
import HelperFunctions
from HelperFunctions import Components
from LayerHandler import LayerSlicer

# remove the default objects in Blender
HelperFunctions.delete_default_objects()

connecting_brick = Brick(4, 2, 3, "4x2x3_connecting.glb", Orientation, True)
connecting_brick.change_orientation(Orientation.NORTH_SOUTH)

# region BRICK DICTIONARIES
thin_bricks = {
    "1x1x1": Brick(1, 1, 1, "1x1x1.glb"),
    "2x1x1": Brick(2, 1, 1, "2x1x1.glb"),
    "3x1x1": Brick(3, 1, 1, "3x1x1.glb"),
    "4x1x1": Brick(4, 1, 1, "4x1x1.glb"),
    "5x1x1": Brick(5, 1, 1, "5x1x1.glb"),
    "6x1x1": Brick(6, 1, 1, "6x1x1.glb"),
    "8x1x1": Brick(8, 1, 1, "8x1x1.glb"),
    "10x1x1": Brick(10, 1, 1, "10x1x1.glb"),
    "12x1x1": Brick(12, 1, 1, "12x1x1.glb"),
    "2x2x1": Brick(2, 2, 1, "2x2x1.glb"),
    "3x2x1": Brick(3, 2, 1, "3x2x1.glb"),
    "4x2x1": Brick(4, 2, 1, "4x2x1.glb"),
    "6x2x1": Brick(6, 2, 1, "6x2x1.glb"),
    "8x2x1": Brick(8, 2, 1, "8x2x1.glb"),
    "10x2x1": Brick(10, 2, 1, "10x2x1.glb"),
    "12x2x1": Brick(12, 2, 1, "12x2x1.glb"),
    "14x2x1": Brick(14, 2, 1, "14x2x1.glb"),
    "16x2x1": Brick(16, 2, 1, "16x2x1.glb"),
    "3x3x1": Brick(3, 3, 1, "3x3x1.glb"),
    "4x4x1": Brick(4, 4, 1, "4x4x1.glb"),
    "6x4x1": Brick(6, 4, 1, "6x4x1.glb"),
    "8x4x1": Brick(8, 4, 1, "8x4x1.glb"),
    "10x4x1": Brick(10, 4, 1, "10x4x1.glb"),
    "12x4x1": Brick(12, 4, 1, "12x4x1.glb"),
    "6x6x1": Brick(6, 6, 1, "6x6x1.glb"),
    "8x6x1": Brick(8, 6, 1, "8x6x1.glb"),
    "10x6x1": Brick(10, 6, 1, "10x6x1.glb"),
    "12x6x1": Brick(12, 6, 1, "12x6x1.glb"),
    "14x6x1": Brick(14, 6, 1, "14x6x1.glb"),
    "16x6x1": Brick(16, 6, 1, "16x6x1.glb"),
    "24x6x1": Brick(24, 6, 1, "24x6x1.glb"),
    "8x8x1": Brick(8, 8, 1, "8x8x1.glb"),
    "11x8x1": Brick(11, 8, 1, "11x8x1.glb"),
    "16x8x1": Brick(16, 8, 1, "16x8x1.glb"),
    "16x16x1": Brick(16, 16, 1, "16x16x1.glb"),
}

thick_bricks = {
    "1x1x3": Brick(1, 1, 3, "1x1x3.glb"),
    "2x1x3": Brick(2, 1, 3, "2x1x3.glb"),
    "4x1x3": Brick(4, 1, 3, "4x1x3.glb"),
    "6x1x3": Brick(6, 1, 3, "6x1x3.glb"),
    "8x1x3": Brick(8, 1, 3, "8x1x3.glb"),
    "10x1x3": Brick(10, 1, 3, "10x1x3.glb"),
    "12x1x3": Brick(12, 1, 3, "12x1x3.glb"),
    "16x1x3": Brick(16, 1, 3, "16x1x3.glb"),
    "2x2x3": Brick(2, 2, 3, "2x2x3.glb"),
    "3x2x3": Brick(3, 2, 3, "3x2x3.glb"),
    "4x2x3": Brick(4, 2, 3, "4x2x3.glb"),
    "6x2x3": Brick(6, 2, 3, "6x2x3.glb"),
    "8x2x3": Brick(8, 2, 3, "8x2x3.glb"),
    "10x2x3": Brick(10, 2, 3, "10x2x3.glb"),
}

smooth_bricks = {
    "1x1x1": Brick(1, 1, 1, "1x1x1_smooth.glb"),
    "2x1x1": Brick(2, 1, 1, "2x1x1_smooth.glb"),
    "3x1x1": Brick(3, 1, 1, "3x1x1_smooth.glb"),
    "4x1x1": Brick(4, 1, 1, "4x1x1_smooth.glb"),
    "6x1x1": Brick(6, 1, 1, "6x1x1_smooth.glb"),
    "8x1x1": Brick(8, 1, 1, "1x1x1_smooth.glb"),
    "2x2x1": Brick(2, 2, 1, "2x2x1_smooth.glb"),
    "3x2x1": Brick(3, 2, 1, "3x2x1_smooth.glb"),
    "4x2x1": Brick(4, 2, 1, "4x2x1_smooth.glb"),
    "6x2x1": Brick(6, 2, 1, "6x2x1_smooth.glb"),
    "6x6x1": Brick(6, 6, 1, "6x6x1_smooth.glb"),
}

# custom_kernel_origins sequence: NORTH, SOUTH, WEST, EAST
sloped_bricks = {
    "2x1x2": Brick(2, 1, 2, "2x1x2_sloped_smooth.glb", SlopedOrientation, Smooth.SLOPED, 
                    [(0, 0, 0), (1, 0, 1)], 
                    [(-1, 0, -1), (-1, 0, -1), (0, -1, -1), (0, -1, -1)]),
    "3x1x3": Brick(3, 1, 3, "3x1x3_sloped_smooth.glb", SlopedOrientation, Smooth.SLOPED, 
                     [(0, 0, 0), (1, 0, 0), (1, 0, 1), (2, 0, 1), (2, 0, 2)],
                     [(-1, 0, -1), (-1, 0, -1), (0, -1, -1), (0, -1, -1)]),
    "3x3x3_corner": Brick(3, 3, 3, "3x3x3_sloped_smooth_corner.glb", SlopedOrientation, Smooth.SLOPED, 
                     [(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 2, 0), 
                      (1, 2, 1), (2, 0, 0), (2, 1, 0), (2, 1, 1), (2, 2, 1), (2, 2, 2)],
                     [(-1, -1, -1), (-1, -1, -1), (-1, -1, -1), (-1, -1, -1)])
}

wheel_bricks = {
    "wheel_30x14": Wheel(30, 14, "wheel_tire(30x14).glb"),
    "wheel_43x14": Wheel(43, 14, "wheel_tire(43x14).glb"),
    "wheel_37x22": Wheel(37, 22, "wheel_tire(37x22).glb"),
    "wheel_43x22": Wheel(43, 22, "wheel_tire(43x22).glb"),
    "wheel_49x28": Wheel(49, 28, "wheel_tire(49x28).glb"),
    "wheel_56x28": Wheel(56, 28, "wheel_tire(56x28).glb"),
}
# endregion

materials = {
    "matte_red": Material("matte_red", Color.RED),
    "matte_green": Material("matte_green", Color.GREEN),
    "matte_blue": Material("matte_blue", Color.BLUE),
    "matte_yellow": Material("matte_yellow", Color.YELLOW),
    "matte_cyan": Material("matte_cyan", Color.CYAN),
    "matte_magenta": Material("matte_magenta", Color.MAGENTA),
    "matte_orange": Material("matte_orange", Color.ORANGE),
    "matte_purple": Material("matte_purple", Color.PURPLE),
    "matte_pink": Material("matte_pink", Color.PINK),
    "matte_brown": Material("matte_brown", Color.BROWN),
    "matte_black": Material("matte_black", Color.BLACK),
    "matte_lime": Material("matte_lime", Color.LIME),
    "matte_teal": Material("matte_teal", Color.TEAL),
    "matte_violet": Material("matte_violet", Color.VIOLET),
    "matte_gold": Material("matte_gold", Color.GOLD),
    "matte_turquoise": Material("matte_turquoise", Color.TURQUOISE),
    "matte_crimson": Material("matte_crimson", Color.CRIMSON),
    "matte_indigo": Material("matte_indigo", Color.INDIGO),
    "matte_navy": Material("matte_navy", Color.NAVY),
    "matte_chartreuse": Material("matte_chartreuse", Color.CHARTREUSE),
}

# body color of the car
main_model_material = materials["matte_blue"]

# start the timer (for time analysis of methods)
start = time.time()

# voxelize the input model
voxel_grid = HelperFunctions.voxelize_model()
voxel_grid = np.transpose(voxel_grid, (2, 1, 0))
voxel_grid = voxel_grid.astype(np.int32)

# create a copy of the original voxel_grid
voxel_grid_copy = voxel_grid.copy()

# 2nd timer for time analysis
start_temp = time.time()

# grid to divide the model into components
components_grid = np.copy(voxel_grid)

# create all collections for objects, load the 3D model and adjust it to overlap the voxelization file
HelperFunctions.create_collections()
HelperFunctions.load_model()
HelperFunctions.move_main_object_to_starting_point(voxel_grid)

# get the main (currently the only) object in the scene
voxel_grid, components_grid = HelperFunctions.check_each_voxel(voxel_grid, components_grid)
layer_handler = LayerSlicer(voxel_grid, components_grid, 1)
mapping_time = time.time() - start_temp

# spawn the wheels
start_temp = time.time()
HelperFunctions.spawn_wheels(connecting_brick, layer_handler, wheel_bricks, main_model_material)
wheels_time = time.time() - start_temp

# different types of windscreens (uncomment the desired cabin and change the height in the spawn_windscreen function accordingly)
windscreen = Windscreen(8, 5, 6, "8x5x6_windscreen.glb")
#windscreen = Windscreen(8, 5, 9, "8x5x9_windscreen.glb")

# spawn the windscreen
start_temp = time.time()
HelperFunctions.spawn_windscreen(windscreen, layer_handler, main_model_material, 0, 6 if windscreen.height == 6 else 0)

# adjust the original (empty) voxel_grid for testing the sloped bricks placement 
original_voxel_grid = HelperFunctions.adjust_original_voxel_grid(layer_handler, voxel_grid_copy)
cabin_time = time.time() - start_temp

# fills the voxel_grid with bricks of different dimensions
def fill_model_with_bricks(brick_type, material=main_model_material, exchange_orientations=False):
    orientation_counter = 0

    # reset the layer_handler to the appropriate height for the new bricks#
    if brick_type == BrickType.THIN:
        layer_height = 1
    elif brick_type == BrickType.THICK:
        layer_height = 3

    layer_handler.reset_layers(layer_height)

    while True:
        current_layer = layer_handler.next_layer()

        # break if no more layers left
        if current_layer is None:
            orientation_counter = 0
            print("No more layers left. Reseting layers and proceeding to next brick.")
            break
        
        if exchange_orientations:
            default_orientation = Orientation.EAST_WEST if orientation_counter % 2 == 0 else Orientation.NORTH_SOUTH
        else:
            default_orientation = Orientation.EAST_WEST

        fill_with_bricks(current_layer, material, default_orientation)
        orientation_counter += 1

# fills the voxel_grid with sloped bricks of different dimensions
def fill_with_bricks_sloped(selected_bricks, material=main_model_material, default_orientation=SlopedOrientation.NORTH):
    bricks = selected_bricks.copy()

    while bricks:
        # find the brick with the largest surface
        brick = max(
            bricks.values(),
            key=lambda obj: (
                min(obj.length, obj.width),  # prioritize smaller of length/width
                max(obj.length, obj.width)  # then prioritize larger of length/width
            )
        )

        tested_orientations = {brick.orientation}

        while True:
            # find the fitting positions for the brick
            fitting_positions = HelperFunctions.apply_correlation(layer_handler.voxel_grid, brick)
            filtered_positions = find_allowed_spawns(fitting_positions, brick)
            
            # no fitting positions found
            if len(filtered_positions) == 0:
                if len(tested_orientations) == len(SlopedOrientation):
                    # reset the orientation to the default one after trying all the orientations
                    brick.change_sloped_orientation(default_orientation)

                    # delete the brick from the copied array
                    del bricks[next(key for key, value in bricks.items() if value == brick)]
                    break
                else:
                    untested_orientation = SlopedOrientation.get_untested_orientation(tested_orientations)

                    if untested_orientation:
                        # try the other orientation of the brick (if it has one) and add it the list of tried orientations
                        brick.change_sloped_orientation(untested_orientation)
                        tested_orientations.add(untested_orientation)
            else:
                # check if any of the fitting positions contains a mirrored position
                bricks_to_add = check_for_symmetry(filtered_positions, layer_handler.voxel_grid, brick)

                # pick a random position to place the brick if a mirrored pair was not found
                if not bricks_to_add:
                    random_position = random.choice(filtered_positions)
                    bricks_to_add.append(tuple(map(lambda pos: pos.item(), random_position)))

                # add the brick to the position
                for x, y, z in bricks_to_add:
                    spawned_brick = brick.spawn_brick(x, y, z, material)
                    
                    spawned_brick.smooth_brick = Smooth.SLOPED
                    layer_handler.add_used_brick(spawned_brick, material)

                    # check for connected bricks
                    layer_handler.update_used_bricks_grid_sloped(spawned_brick, x, y, z)
                    HelperFunctions.determine_connected_bricks(layer_handler, spawned_brick)

                    # update the voxel grid
                    layer_handler.update_voxel_grid_sloped(brick, x, y, z)

# fills the voxel_grid with smooth bricks of different dimensions
def fill_model_with_bricks_smooth(selected_bricks, material=main_model_material, default_orientation=Orientation.EAST_WEST):
    bricks = selected_bricks.copy()

    while bricks:
        # find the brick with the largest surface
        brick = max(
            bricks.values(),
            key=lambda obj: (
                min(obj.length, obj.width),  # prioritize smaller of length/width
                max(obj.length, obj.width)  # then prioritize larger of length/width
            )
        )

        tested_orientations = {brick.orientation}

        while True:
            # find the fitting positions for the brick
            fitting_positions = HelperFunctions.apply_convolution(layer_handler.voxel_grid, brick)
            filtered_positions = find_allowed_spawns(fitting_positions, brick)
            
            # no fitting positions found
            if len(filtered_positions) == 0:
                if brick.orientation == Orientation.NONE:
                    # delete the brick from the copied array
                    del bricks[next(key for key, value in bricks.items() if value == brick)]
                    break

                if len(tested_orientations) == len(Orientation) - 1:
                    # reset the orientation to the default one after trying all the orientations
                    brick.change_orientation(default_orientation)

                    # delete the brick from the copied array
                    del bricks[next(key for key, value in bricks.items() if value == brick)]
                    break
                else:
                    untested_orientation = Orientation.get_untested_orientation(tested_orientations)

                    if untested_orientation:
                        # try the other orientation of the brick (if it has one) and add it the list of tried orientations
                        brick.change_orientation(untested_orientation)
                        tested_orientations.add(untested_orientation)
            else:
                # check if any of the fitting positions contains a mirrored position
                bricks_to_add = check_for_symmetry(filtered_positions, layer_handler.voxel_grid, brick)

                # pick a random position to place the brick if a mirrored pair was not found
                if not bricks_to_add:
                    random_position = random.choice(filtered_positions)
                    bricks_to_add.append(tuple(map(lambda pos: pos.item(), random_position)))

                # spawn the bricks into selected positions
                for x, y, z in bricks_to_add:
                    spawned_brick = brick.spawn_brick(x, y, z, material)
                    spawned_brick.smooth_brick = Smooth.NORMAL
                    layer_handler.add_used_brick(spawned_brick, material)

                    # check for connected bricks
                    layer_handler.update_used_bricks_grid(spawned_brick, x, y, z)
                    HelperFunctions.determine_connected_bricks(layer_handler, spawned_brick)

                    # update the voxel grid
                    layer_handler.update_voxel_grid(brick, x, y, z)

# spawns in the bricks that represent the front and rear lights of the car
def spawn_lights(components_grid):
    voxel_grid_copy = np.copy(layer_handler.voxel_grid)

    # retrieve all light components from the model
    all_lights = [component for component in Components if "light" in component.name]
    front_lights = [light.value for light in all_lights if "front" in light.name]
    rear_lights = [light.value for light in all_lights if "rear" in light.name]

    # make space for the front lights in the voxel_grid
    voxel_grid_copy[np.isin(components_grid, front_lights)] = 1
    layer_handler.voxel_grid = voxel_grid_copy

    # fill the space of the front lights
    fill_model_with_bricks(BrickType.THICK, materials["matte_yellow"])
    fill_model_with_bricks(BrickType.THIN, materials["matte_yellow"])

    # make space for the rear lights in the voxel_grid
    voxel_grid_copy[np.isin(components_grid, rear_lights)] = 1
    layer_handler.voxel_grid = voxel_grid_copy

    # fill the space of the front lights
    fill_model_with_bricks(BrickType.THICK, materials["matte_red"])
    fill_model_with_bricks(BrickType.THIN, materials["matte_red"])

# checks if a placed brick has a symmetrical position (on the Y-axis) and spawns a brick there if it does
def check_for_symmetry(fitting_positions, voxel_grid_layer, brick):
    def calculate_mirrored_position(x_pos, y_pos, custom=False):
        mirrored_x = voxel_grid_layer.shape[0] - x_pos - brick.length
        return mirrored_x, y_pos

    bricks_to_add = []
    
    # bricks longer than half of the model cannot be mirrored
    if brick.length > voxel_grid_layer.shape[0] / 2:
        return []

    # if there is only one fitting position return it
    if len(fitting_positions) == 1:# and not isinstance(brick.orientation, SlopedOrientation):
        bricks_to_add.append((pos.item() for pos in fitting_positions[0]))
        return bricks_to_add

    symmetry_line_x = voxel_grid_layer.shape[0] / 2
    sorted_fitting_positions = sorted(fitting_positions, key=lambda pos: pos[2].item(), reverse=False)

    # check all positions to find the ones that can be mirrored
    for position in sorted_fitting_positions:
        x_pos, y_pos, z_pos = (pos.item() for pos in position)
        mirrored_x, mirrored_y = calculate_mirrored_position(x_pos, y_pos)
        
        if isinstance(brick.orientation, SlopedOrientation):
            original_orientation = brick.orientation

            # get mirrored orientation
            if original_orientation == SlopedOrientation.NORTH:
                mirrored_orientation = SlopedOrientation.SOUTH
            elif original_orientation == SlopedOrientation.SOUTH:
                mirrored_orientation = SlopedOrientation.NORTH
            elif original_orientation == SlopedOrientation.EAST:
                mirrored_orientation = SlopedOrientation.WEST
            elif original_orientation == SlopedOrientation.WEST:
                mirrored_orientation = SlopedOrientation.EAST

            # calculate mirrored brick position from the original
            original_brick_to_add = (x_pos, y_pos, z_pos)
            custom_x, custom_y = calculate_mirrored_position(x_pos, y_pos, True)
            
            brick.change_sloped_orientation(mirrored_orientation)
            
            fitting_positions_test = HelperFunctions.apply_correlation(layer_handler.voxel_grid, brick)
            filtered_positions_test = find_allowed_spawns(fitting_positions_test, brick)

            # if mirrored position exists spawn a brick there
            if (custom_x, custom_y, z_pos) in filtered_positions_test:
                spawned_brick = brick.spawn_brick(custom_x, custom_y, z_pos, main_model_material)
                spawned_brick.smooth_brick = Smooth.SLOPED
                layer_handler.add_used_brick(spawned_brick, main_model_material)

                # check for connected bricks
                layer_handler.update_used_bricks_grid_sloped(spawned_brick, custom_x, custom_y, z_pos)
                HelperFunctions.determine_connected_bricks(layer_handler, spawned_brick)

                # update the voxel grid
                layer_handler.update_voxel_grid_sloped(brick, custom_x, custom_y, z_pos)

            brick.change_sloped_orientation(original_orientation)

            bricks_to_add.append(original_brick_to_add)
            return bricks_to_add
        else:
            # find matching mirrored position
            mirrored_position = [
                pos for pos in sorted_fitting_positions
                if pos[0].item() == mirrored_x 
                and pos[1].item() == mirrored_y
            ]

            if mirrored_position:
                x_mirrored, y_mirrored, z_mirrored = (pos.item() for pos in mirrored_position[0])

                # only return the original if the voxels of it stretch over the middle of the model
                x_voxels_original = list(range(x_pos, x_pos + brick.length))
    
                if int(symmetry_line_x) in x_voxels_original:
                    bricks_to_add.append((x_pos, y_pos, z_pos))
                    return list(set(bricks_to_add))
                
                bricks_to_add.append((x_pos, y_pos, z_pos))
                bricks_to_add.append((x_mirrored, y_mirrored, z_mirrored))
                # set and then list to clear duplicates
                return list(set(bricks_to_add))
            
            if isinstance(brick.orientation, SlopedOrientation):
                if not mirrored_position:
                    continue

    return bricks_to_add

# fills a layer with bricks
def fill_with_bricks(voxel_grid_layer, material, default_orientation=Orientation.EAST_WEST):
    # copy the appropriate bricks dictionary depending on the brick's height
    bricks = thin_bricks.copy() if voxel_grid_layer.shape[2] == 1 else thick_bricks.copy()

    while bricks:
        # find the brick with the largest surface
        brick = max(
            bricks.values(),
            key=lambda obj: (
                min(obj.length, obj.width),  # prioritize smaller of length/width
                max(obj.length, obj.width)  # then prioritize larger of length/width
            )
        )

        tried_rotation = False

        while True:
            # find the fitting positions for the brick
            fitting_positions = HelperFunctions.apply_convolution(voxel_grid_layer, brick)
            random.shuffle(fitting_positions)

            # no fitting positions found
            if len(fitting_positions) == 0:
                if (tried_rotation or brick.orientation == Orientation.NONE):
                    # reset the orientation to the default one after trying all the orientations
                    if (brick.orientation != Orientation.NONE):
                        brick.change_orientation(default_orientation)

                    # delete the brick from the copied array
                    del bricks[next(key for key, value in bricks.items() if value == brick)]
                    break
                else:
                    # try the other orientation of the brick (if it has one)
                    brick.change_orientation(Orientation.NORTH_SOUTH if default_orientation == Orientation.EAST_WEST else Orientation.EAST_WEST)
                    tried_rotation = True
            else:
                # check if any of the fitting positions contains a mirrored position
                bricks_to_add = check_for_symmetry(fitting_positions, voxel_grid_layer, brick)

                # pick a random position to place the brick if a mirrored pair was not found
                if not bricks_to_add:
                    random_position = random.choice(fitting_positions)
                    bricks_to_add.append(tuple(map(lambda pos: pos.item(), random_position)))

                # spawn brick, update voxel_grid, check for connections, neighbours...
                for x_brick, y_brick, z_brick in bricks_to_add:
                    # place the brick in a random position
                    spawned_brick = brick.spawn_brick(x_brick, y_brick, z_brick + layer_handler.current_layer_start, material)
                    layer_handler.add_used_brick(spawned_brick, material)

                    # check for connected bricks
                    layer_handler.update_used_bricks_grid(spawned_brick, x_brick, y_brick)
                    #layer_handler.update_used_bricks_grid(spawned_brick, x_brick, y_brick)
                    HelperFunctions.determine_connected_bricks(layer_handler, spawned_brick)

                    # update the voxel grid of the layer
                    for x in range(brick.length):
                        for y in range(brick.width):
                            for z in range(brick.height):
                                voxel_grid_layer[x_brick + x][y_brick + y][z_brick + z] = 0

    # try the next brick
    layer_handler.update_voxel_grid_layer(voxel_grid_layer)

# connects two smaller subgraphs into a larger one using a "bridge" brick
def connect_subgraphs(neighboring_bricks_subgrid, empty_subgrid, mapping_subgrid):
    connection_bricks = thick_bricks.copy() if empty_subgrid.shape[2] == 3 else thin_bricks.copy()

    def check_positions(fitting_positions, brick):
        elegible_fitting_positions = []

        # get the two brick ids that the voxel subgrid is based on
        brick_ids = {brick_id for brick_id, _ in neighboring_bricks_subgrid}

        for position in fitting_positions:
            # get the brick position indices in the empty_subgrid
            x_pos, y_pos, z_pos = map(lambda pos: pos.item(), position)

            if len(brick_ids) == 2:
                first_brick_id, second_brick_id = brick_ids
            else:
                print("Error: The list doesn't contain exactly two brick IDs.")
                continue

            first_brick_count = 0
            second_brick_count = 0

            for x in range(brick.length):
                for y in range(brick.width):
                    for z in range(brick.height):
                        temp_tuple = mapping_subgrid[x + x_pos, y + y_pos, z + z_pos]
                        matching_voxel = [id for id, global_indices in neighboring_bricks_subgrid 
                                          if global_indices == temp_tuple]
                        
                        if matching_voxel == first_brick_id:
                            first_brick_count += 1
                        elif matching_voxel == second_brick_id:
                            second_brick_count += 1

            # add all the positions that connect the two bricks to a list
            if first_brick_count > 0 and second_brick_count > 0:
                elegible_fitting_positions.append(
                    (position, (first_brick_count, second_brick_count)))

        if not elegible_fitting_positions:
            return None

        # find and return the optimal fitting position (with the most connecting voxels)
        best_position = max(elegible_fitting_positions, key=lambda x: (x[1][0], x[1][1]))
        x_pos, y_pos, z_pos = best_position[0]

        # update and return the empty_subgrid for the next iteration of convolution
        for x in range(brick.length):
            for y in range(brick.width):
                for z in range(brick.height):
                    empty_subgrid[x + x_pos][y + y_pos][z + z_pos] = 0

        return [mapping_subgrid[x_pos, y_pos, z_pos], empty_subgrid]

    while connection_bricks:
        # find the brick with the largest surface
        brick = max(connection_bricks.values(), key=lambda obj: obj.length * obj.width)

        tried_rotation = False

        while (True):
            # find the fitting positions for the brick in the subgrid
            fitting_positions = HelperFunctions.apply_convolution(empty_subgrid, brick)

            returned_items = check_positions(fitting_positions, brick)
                
            # no fitting positions found
            if returned_items is None:
                if tried_rotation or brick.orientation == Orientation.NONE:
                    # reset the orientation to the default one after trying all the orientations
                    if (brick.orientation != Orientation.NONE):
                        brick.change_orientation(Orientation.EAST_WEST)

                    # delete the brick from the copied array
                    del connection_bricks[next(key for key, value in connection_bricks.items() if value == brick)]
                    break
                else:
                    # try the other orientation of the brick (if it has one)
                    brick.change_orientation(Orientation.NORTH_SOUTH)
                    tried_rotation = True
            else:
                elegible_fitting_positions, empty_subgrid = returned_items
                x_pos, y_pos, z_pos = elegible_fitting_positions
                # find the optimal fitting position and spawn the brick
                spawned_brick = brick.spawn_brick(x_pos, y_pos, z_pos, main_model_material)
                layer_handler.add_used_brick(spawned_brick, main_model_material)

                # update the global_grid, used_bricks grid and the empty_subgrid
                layer_handler.update_voxel_grid(spawned_brick, x_pos, y_pos, z_pos)
                layer_handler.update_used_bricks_grid(spawned_brick, x_pos, y_pos, z_pos)

                # check for connected bricks
                HelperFunctions.determine_connected_bricks(layer_handler, spawned_brick)

# connects all unconnected bricks with the model
def fix_model_connectivity():
    connection_counter = 0
    same_bricks_counter = 0
    previous_subgraphs_counter = 0
    previous_subgraphs = list()

    while (True):
        # find and divide all the subgraphs to the main (largest) one and the smaller disconnected ones (smaller ones)
        connection_subgraphs = HelperFunctions.find_brick_connection_subgraphs(layer_handler.used_bricks)

        # increment counter if the no subgraphs were connected in the previous run
        if len(previous_subgraphs) == len(connection_subgraphs) and len(connection_subgraphs) == 2:
            connection_counter += 1
        
        previous_subgraphs = connection_subgraphs
        
        connection_counter += 1

        # return if the subgraph number hasn't changed in some time (it is removing and replacing the same bricks)
        if connection_counter > 500:
            smaller_subgraph = min(connection_subgraphs)
            print(f"Error! A brick {smaller_subgraph} couldn't be connected somewhere.")
            return

        # end if all bricks are connected
        if len(connection_subgraphs) == 1:
            print("All bricks are now connected.")
            return

        largest_subgraph = max(connection_subgraphs, key=len)
        disconnected_subgraphs = [subgraph for subgraph in connection_subgraphs if subgraph != largest_subgraph]

        if len(disconnected_subgraphs) == previous_subgraphs_counter or previous_subgraphs_counter == 0:
            same_bricks_counter += 1

        disconnected_brick_id = None

        while disconnected_subgraphs:
            non_static_subgraphs = []

            # check if all disconnected subgraphs are full of static bricks
            for disconnected_subgraph in disconnected_subgraphs:
                  if all(layer_handler.used_bricks[disconnected_brick_id].smooth_brick != Smooth.NONE for disconnected_brick_id in list(disconnected_subgraph)):
                    continue
                  else:
                    non_static_subgraphs.append(disconnected_subgraph)
          
            # all subgraphs contain only static bricks -> select one of them randomly
            if non_static_subgraphs:
                random_subgraph = random.choice(non_static_subgraphs)
                disconnected_brick_id = random.choice(list(random_subgraph))
            else:
                random_subgraph = random.choice(disconnected_subgraphs)
                disconnected_brick_id = random.choice(list(random_subgraph))

            # break if found a brick with at least one neighbour
            if layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks:
                break
            # remove subgraph if no valid bricks with neighbors exist
            else:
                disconnected_subgraphs.remove(random_subgraph)
                disconnected_brick_id = None
        
        # if no brick with neighbors is found, exit the loop
        if disconnected_brick_id == None :
            print("No remaining disconnected bricks with neighbors.")
            break
 
        # create a list of all neighbours and their lowest z values
        neighbour_z_list = list()
        
        # if all neighbouring bricks are static, pick one randomly
        if all(layer_handler.used_bricks[neighboring_brick].smooth_brick != Smooth.NONE for neighboring_brick in layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks):
            neighboring_smooth_bricks = list(neighboring_brick for neighboring_brick
                                            in layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks 
                                            if layer_handler.used_bricks[neighboring_brick].smooth_brick == Smooth.NORMAL)
            
            if neighboring_smooth_bricks:
                random_neighbouring_brick = random.choice(neighboring_smooth_bricks)
            else:
                random_neighbouring_brick = random.choice(list(layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks))

            random_neighboring_brick_indices = np.argwhere(layer_handler.used_bricks_grid == random_neighbouring_brick)
            lowest_z = min(z[2] for z in random_neighboring_brick_indices)
            neighbour_z_list.append((random_neighbouring_brick, lowest_z))
        else:
            for neighboring_brick in layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks:
                # ignore the static bricks (for components)
                if layer_handler.used_bricks[neighboring_brick].smooth_brick != Smooth.NONE and same_bricks_counter < 100:
                    continue

                neighboring_brick_indices = np.argwhere(layer_handler.used_bricks_grid == neighboring_brick)

                if neighboring_brick_indices.size == 0:
                    print("Problematic neighbouring brick ID:" + str(neighboring_brick))
                    print("Problematic neighbouring brick indices:" + str(neighboring_brick_indices))
                    break

                lowest_z = min(z[2] for z in neighboring_brick_indices)

                neighbour_z_list.append((neighboring_brick, lowest_z))
         
        if len(neighbour_z_list) == 0:
            print(f"Brick {brick.id} doesn't contain any non-static neighbouring bricks.")
            return
        
        # find a random neighbour with the lowest z
        lowest_z = min(neighbour_z_list, key=lambda x: x[1])[1]
        lowest_neighboring_brick_id = random.choice([brick_id for brick_id, z in neighbour_z_list if z == lowest_z])

        # check what type of a component the brick represents
        disconnected_brick_indices = np.argwhere(layer_handler.used_bricks_grid == disconnected_brick_id)
        neighboring_brick_indices = np.argwhere(layer_handler.used_bricks_grid == lowest_neighboring_brick_id)

        # check what component the disconnected bricks represent
        component1 = Components(layer_handler.components_grid[disconnected_brick_indices[0][0],
                                                disconnected_brick_indices[0][1],
                                                disconnected_brick_indices[0][2]])
        
        component2 = Components(layer_handler.components_grid[neighboring_brick_indices[0][0],
                                                neighboring_brick_indices[0][1],
                                                neighboring_brick_indices[0][2]])
        
        # determine the material of the newly spawned bricks depending on the component type
        if component1 in [Components.light_front_left, Components.light_front_right] or component2 in [Components.light_front_left, Components.light_front_right]:
            material = materials["matte_yellow"]
        elif component1 in [Components.light_rear_left, Components.light_rear_right] or component2 in [Components.light_rear_left, Components.light_rear_right]:
            material = materials["matte_red"]
        else:
            material = main_model_material

        layer_handler.used_bricks[disconnected_brick_id].neighbouring_bricks.discard(lowest_neighboring_brick_id)

        # get the subgrid of all the voxels of the two bricks that meet the criteria for connecting the two subgraphs
        neighbouring_bricks_subgrid, empty_subgrid, mapping_subgrid = HelperFunctions.find_connection_points(disconnected_brick_id, lowest_neighboring_brick_id, layer_handler.used_bricks_grid)

        # mark the voxels for the voxel_grid and the indices for the used_bricks_grid empty
        disconnected_brick_indices = np.where(layer_handler.used_bricks_grid == disconnected_brick_id)

        for layer in range(len(disconnected_brick_indices[0])):
            x = disconnected_brick_indices[0][layer]
            y = disconnected_brick_indices[1][layer]
            z = disconnected_brick_indices[2][layer]

            layer_handler.voxel_grid[x, y, z] = 1
            layer_handler.used_bricks_grid[x, y, z] = 0
        
        used_bricks_grid = layer_handler.used_bricks_grid
        neighbouring_brick_indices = np.where(used_bricks_grid == lowest_neighboring_brick_id)

        for layer in range(len(neighbouring_brick_indices[0])):
            x = neighbouring_brick_indices[0][layer]
            y = neighbouring_brick_indices[1][layer]
            z = neighbouring_brick_indices[2][layer]

            layer_handler.voxel_grid[x, y, z] = 1
            layer_handler.used_bricks_grid[x, y, z] = 0

        # remove all connection/neighbouring references of the removed bricks in the used_bricks dictionary
        for brick in layer_handler.used_bricks.values():
            brick.connected_bricks.discard(disconnected_brick_id)
            brick.connected_bricks.discard(lowest_neighboring_brick_id)
            brick.neighbouring_bricks.discard(disconnected_brick_id)
            brick.neighbouring_bricks.discard(lowest_neighboring_brick_id)

        # remove the selected bricks from the scene
        layer_handler.used_bricks[disconnected_brick_id].remove_brick()
        layer_handler.used_bricks[lowest_neighboring_brick_id].remove_brick()
        
        # remove the selected bricks from the used_bricks dictionary
        del layer_handler.used_bricks[disconnected_brick_id] 
        del layer_handler.used_bricks[lowest_neighboring_brick_id]
    	
        # place a brick to connect the two subgraphs
        connect_subgraphs(neighbouring_bricks_subgrid, empty_subgrid, mapping_subgrid)

        fill_model_with_bricks(BrickType.THICK, material)
        fill_model_with_bricks(BrickType.THIN, material)

# returns a list of available spawns for each brick
def find_allowed_spawns(fitting_positions, brick):
    def check_above_voxels(x_pos, y_pos, z_pos):
        kernel = brick.brick_kernel
        
        for x in range(kernel.shape[0]):
            for y in range(kernel.shape[1]):
                highest_z = None

                # find the highest voxel for a specific XY in the kernel (start from highest and go to lowest)
                for z in range(kernel.shape[2] - 1, -1, -1):
                    if kernel[x, y, z] == 1:
                        highest_z = z
                        break
                        
                # if a voxel exists, check if the voxel above it is empty space (out of the model -
                #  that means the looked at voxel is the highest voxel in the actual model for that (x, y))
                if highest_z is not None:
                    global_x = x_pos + x
                    global_y = y_pos + y
                    global_z = z_pos + highest_z

                    if (0 <= global_x < original_voxel_grid.shape[0] and
                    0 <= global_y < original_voxel_grid.shape[1] and
                    0 <= global_z + 1 < original_voxel_grid.shape[2]):
                        # check if there are empty brick voxels anywhere above the highest Z for each XY - (sloped) brick cannot be placed there
                        for above_z in range(global_z + 1, original_voxel_grid.shape[2]):
                            if original_voxel_grid[global_x, global_y, above_z] == 1:
                                return False
       
        return True
    
    potential_spawns = set()

    for position in fitting_positions:
        x, y, z = (pos.item() for pos in position)
        
        # add the position to the list of potential positions if the voxel above is empty
        if check_above_voxels(x, y, z):
            potential_spawns.add(tuple(position))

    return list(potential_spawns)


# fill the model with bricks and print the times of each stage
start_temp = time.time()
fill_with_bricks_sloped(sloped_bricks)
sloped_time = time.time() - start_temp

start_temp = time.time()
fill_model_with_bricks_smooth(smooth_bricks)
smooth_time = time.time() - start_temp

start_temp = time.time()
fill_model_with_bricks(BrickType.THICK)
thick_time = time.time() - start_temp

start_temp = time.time()
fill_model_with_bricks(BrickType.THIN)
thin_time = time.time() - start_temp

start_temp = time.time()
spawn_lights(layer_handler.components_grid)
lights_time = time.time() - start_temp

start_temp = time.time()
fix_model_connectivity()
HelperFunctions.check_materials(layer_handler, materials, main_model_material)
connectivity_time = time.time() - start_temp

# end timer and calculate the final time taken
full_time = time.time() - start

print(f"Component mapping time: {mapping_time:.3f} seconds")
print(f"Wheels generation: {wheels_time:.3f} seconds")
print(f"Cabin generation: {cabin_time:.3f} seconds")
print(f"Sloped bricks generation: {sloped_time:.3f} seconds")
print(f"Smooth bricks generation: {smooth_time:.3f} seconds")
print(f"Thick bricks generation: {thick_time:.3f} seconds.")
print(f"Thin bricks generation: {thin_time:.3f} seconds.")
print(f"Lights generation: {lights_time:.3f} seconds.")
print(f"Fixing connectivity: {connectivity_time:.3f} seconds.")
print(f"Full generation: {full_time:.3f} seconds.")

# reset the brick ID and clear all invisible (temporary) bricks from the scene
Brick.id = 0

HelperFunctions.clear_invisible_bricks()

