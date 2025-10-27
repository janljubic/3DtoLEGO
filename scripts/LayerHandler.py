import numpy as np

class LayerSlicer:
    def __init__(self, voxel_grid, components_grid, layer_size):
        self.voxel_grid = voxel_grid
        self.components_grid = components_grid 
        self.used_bricks = {} # all the used bricks (key: id, value: brick)
        self.used_bricks_grid = np.zeros(voxel_grid.shape, dtype=np.int32)
        self.layer_size = layer_size
        self.z_size = voxel_grid.shape[2]
        self.current_layer_start = 0
        self.current_layer = 0
    
    # adds a new brick with a custom material to global used_bricks grid
    def add_used_brick(self, brick, material):
        self.used_bricks[brick.id] = brick
        brick.material = material
    
    # updates the global voxel_grid with filled voxels (used for adding new bricks to the model) 
    def update_voxel_grid(self, used_brick, x_pos, y_pos, z_pos): 
        # indices in the global voxel_grid
        self.voxel_grid[x_pos:x_pos + used_brick.length, y_pos:y_pos + used_brick.width, z_pos:z_pos + used_brick.height] = 0

    # updates a whole layer of bricks and changes the global voxel_grid accordingly
    def update_voxel_grid_layer(self, voxel_grid_layer):
        # define the region in the global grid to be updated
        z_start = self.current_layer_start
        z_end = self.current_layer_start + voxel_grid_layer.shape[2]

        # Ensure we are within bounds
        if z_end > self.voxel_grid.shape[2]:
            raise ValueError("Layer exceeds the bounds of the global voxel grid.")

        # Update the specific layer in the global voxel grid
        self.voxel_grid[:, :, z_start:z_end] = voxel_grid_layer

    # updates a specific voxel in the global voxel_grid (used when expanding the size of the cabin)
    def update_voxel_grid_index(self, x_index, y_index, z_index, filled):
        self.voxel_grid[x_index, y_index, z_index] = 0 if filled else 1

    # updates the global voxel_grid with filled voxels (used exclusively for adding new sloped bricks to the model)
    def update_voxel_grid_sloped(self, sloped_brick, x_pos, y_pos, z_pos):
        # get all indices that are marked as empty
        dxs, dys, dzs = np.nonzero(sloped_brick.brick_kernel)

        # calculate the global positions of said indices
        xs = x_pos + dxs
        ys = y_pos + dys
        zs = z_pos + dzs

        # mark the indices as filled
        self.voxel_grid[xs, ys, zs] = 0

    # updates the global used_bricks_grid with with the added bricks ID
    def update_used_bricks_grid(self, used_brick, x_pos, y_pos, z_pos=None):
        if z_pos is None:
            z_pos = self.current_layer_start

        self.used_bricks_grid[x_pos:x_pos + used_brick.length, y_pos:y_pos + used_brick.width, z_pos:z_pos + used_brick.height] = used_brick.id

    # updates the global used_bricks_grid with with the added brick IDs (used exclusively for sloped bricks)
    def update_used_bricks_grid_sloped(self, sloped_brick, x_pos, y_pos, z_pos):
        # get all indices that are marked as empty
        dxs, dys, dzs = np.nonzero(sloped_brick.brick_kernel)

        # calculate the global positions of said indices
        xs = x_pos + dxs
        ys = y_pos + dys
        zs = z_pos + dzs

        # mark the indices with the bricks ID
        self.used_bricks_grid[xs, ys, zs] = sloped_brick.id

    # marks voxels in the global component_grid as empty/filed (used when expanding the size of the cabin)
    def update_components_grid_index(self, x_index, y_index, z_index, value):
        self.components_grid[x_index, y_index, z_index] = value

    # returns the next layer of the global voxel_grid (depending on the layer size)
    def next_layer(self):
        # check if there are no more layers
        if self.current_layer >= self.z_size:
            return None 

        # calculate the indices of the layer
        z_start = self.current_layer
        z_end = min(self.current_layer + self.layer_size, self.z_size)

        # slice the layer out of the model
        current_layers = self.voxel_grid[:, :, z_start:z_end]

        # update the current layer
        self.current_layer = z_end

        # update the starting index in the global array
        self.current_layer_start = z_start

        return current_layers

    # adjusts the size of the layer (thin bricks = 1, thick bricks = 3)
    def change_layer_size(self, layer_size):
        self.layer_size = layer_size

    # resets the current layer back to the lowest one (used after completing a pass of adding new bricks across all layers)
    def reset_layers(self, layer_size):
        self.layer_size = layer_size
        self.current_layer_start = 0
        self.current_layer = 0