import numpy as np
import math

from vispy.visuals.visual import CompoundVisual
from vispy.visuals.line import LineVisual
from vispy.color import Color
from vispy import scene
from vispy.visuals.transforms import MatrixTransform


class GridVisual(LineVisual):
    def __init__(self, step=1.0, count=10, subdivs=5, draw_center=True, grid_color=[0.7, 0.7, 0.7, 0.5], subgrid_color=[0.7, 0.7, 0.7, 0.25], center_color=[0.9, 0.9, 0.9, 0.75], method="gl", **kwargs):
        vert_array = []
        color_array = []
        min_coord = -1 * (count / 2) * step
        subdiv_size = step / subdivs
        for i in range(count + 1):
            # form x=const lines
            shift = min_coord + step * i
            if (draw_center is False) or (draw_center is True and abs(shift) > subdiv_size / 2):
                vert_array.append([shift, min_coord, 0])
                vert_array.append([shift, -1*min_coord, 0])
                color_array.append(grid_color)
                color_array.append(grid_color)
                # y=const line
                vert_array.append([min_coord, shift, 0])
                vert_array.append([-1 * min_coord, shift, 0])
                color_array.append(grid_color)
                color_array.append(grid_color)
            # subdivided lines
            if i < count:
                for j in range(subdivs - 1):
                    vert_array.append([shift + (j + 1) * subdiv_size, min_coord, 0])
                    vert_array.append([shift + (j + 1) * subdiv_size, -1*min_coord, 0])
                    color_array.append(subgrid_color)
                    color_array.append(subgrid_color)
                    vert_array.append([min_coord, shift + (j + 1) * subdiv_size, 0])
                    vert_array.append([-1*min_coord, shift + (j + 1) * subdiv_size, 0])
                    color_array.append(subgrid_color)
                    color_array.append(subgrid_color)
        if draw_center:
            vert_array.append([0, -1*min_coord, 0])
            vert_array.append([0, min_coord, 0])
            vert_array.append([-1*min_coord, 0, 0])
            vert_array.append([min_coord, 0, 0])
            color_array.append(center_color)
            color_array.append(center_color)
            color_array.append(center_color)
            color_array.append(center_color)

        verts = np.array(vert_array)
        color = np.array(color_array)
        LineVisual.__init__(self, pos=verts, color=color, connect='segments', method=method, **kwargs)


class AxisArrowVisual(CompoundVisual):
    def __init__(self, parent=None, width=6.0, arrow_size=5.0, color_red=Color((1.0, 0.0, 0.0, 1.0)), color_green=Color((0.0, 1.0, 0.0, 1.0)), color_blue=Color((0.0, 0.0, 1.0, 1.0)), **kwargs):
        start = [0, 0, 0]
        end_x = [-1, 0, 0]
        end_y = [0, -1, 0]
        end_z = [0, 0, -1]
        positions_x = np.array([start, end_x])
        positions_y = np.array([start, end_y])
        positions_z = np.array([start, end_z])

        arrow_x = np.array([start + end_x])
        arrow_y = np.array([start + end_y])
        arrow_z = np.array([start + end_z])
        self._arrow_x = scene.visuals.Arrow(parent=parent, color=color_red, arrow_color=color_red, width=width, pos=positions_x, arrows=arrow_x, arrow_type="stealth", arrow_size=arrow_size)
        self._arrow_y = scene.visuals.Arrow(parent=parent, color=color_green, arrow_color=color_green, width=width, pos=positions_y, arrows=arrow_y, arrow_type="stealth", arrow_size=arrow_size)
        self._arrow_z = scene.visuals.Arrow(parent=parent, color=color_blue, arrow_color=color_blue, width=width, pos=positions_z, arrows=arrow_z, arrow_type="stealth", arrow_size=arrow_size)
        CompoundVisual.__init__(self, [self._arrow_x, self._arrow_y, self._arrow_z], **kwargs)


class NullVisual(LineVisual):
    def __init__(self, parent=None, size=0.1, color=Color((1.0, 0.0, 0.0, 1.0)), **kwargs):
        vert_array = [[-1*size, 0, 0], [size, 0, 0], [0, -1*size, 0], [0, size, 0], [0, 0, -1*size], [0, 0, size]]
        verts = np.array(vert_array)
        LineVisual.__init__(self, pos=verts, color=color, connect='segments', method="gl", **kwargs)


NullNode = scene.visuals.create_visual_node(NullVisual)
AxisArrowNode = scene.visuals.create_visual_node(AxisArrowVisual)
GridNode = scene.visuals.create_visual_node(GridVisual)


class SceneVisuals(object):  # collection of visuals on the scene which are not correspond to objects
    def __init__(self, scene=None):
        self._scene = scene
        self._is_update_visuals = True
        self._view_axis = None
        self._view_axis_exist = False
        self._grid = None
        self._grid_geo_parameters = {}  # here we store parameters of the current frid. If new parameters are distinct from these, we should remove and recreate the grid
        self._is_grid_exist = False
        self._axis_size = None
        self._axis_shift = None
        self._orientation_mode = 2  # 2 - default, z is upper, 1 - y is upper, 0 - x is upper

    def set_orientation(self, mode):
        self._orientation_mode = mode

    def _extract_rotation(self, matrix):
        # get rotation axis
        u = (matrix[2][1] - matrix[1][2], matrix[0][2] - matrix[2][0], matrix[1][0] - matrix[0][1])
        trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
        # and angle
        angle = np.arccos((trace - 1) / 2) * 180 / math.pi
        return (u, angle)

    def _vector_square_length(self, vector):
        to_return = 0.0
        for i in range(len(vector)):
            to_return = to_return + vector[i]**2
        return to_return

    @property
    def is_update_visuals(self):
        return self._is_update_visuals

    @is_update_visuals.setter
    def is_update_visuals(self, value):
        self._is_update_visuals = value

    def add_view_axis(self, parent, axis_size=50, width=2.0, axis_arrow_size=5.0, axis_corner=1, axis_shift_x=50, axis_shift_y=50, axis_x_color=Color("red"), axis_y_color=Color("green"), axis_z_color=Color("blue")):
        self._axis_size = axis_size
        self._axis_corner = axis_corner
        self._axis_shift_x = axis_shift_x
        self._axis_shift_y = axis_shift_y
        self._view_axis = AxisArrowNode(parent=parent, width=width, arrow_size=axis_arrow_size, color_red=axis_x_color, color_green=axis_y_color, color_blue=axis_z_color)
        self._view_axis.transform = MatrixTransform()
        self._view_axis_exist = True

    def remove_axis(self):
        if self._view_axis_exist:
            self._view_axis.parent = None
            self._view_axis_exist = False

    def set_axis_data(self, axis_size=50, width=2.0, axis_arrow_size=5.0, axis_corner=1, axis_shift_x=50, axis_shift_y=50, axis_x_color=Color("red"), axis_y_color=Color("green"), axis_z_color=Color("blue")):
        self._axis_corner = axis_corner
        self._axis_shift_x = axis_shift_x
        self._axis_shift_y = axis_shift_y
        self._axis_size = axis_size
        if self._view_axis_exist:  # set the color and width
            self._view_axis._arrow_x.set_data(color=axis_x_color, width=width)
            self._view_axis._arrow_x.arrow_size = axis_arrow_size
            self._view_axis._arrow_x.arrow_color = axis_x_color
            self._view_axis._arrow_y.set_data(color=axis_y_color, width=width)
            self._view_axis._arrow_y.arrow_size = axis_arrow_size
            self._view_axis._arrow_y.arrow_color = axis_y_color
            self._view_axis._arrow_z.set_data(color=axis_z_color, width=width)
            self._view_axis._arrow_z.arrow_size = axis_arrow_size
            self._view_axis._arrow_z.arrow_color = axis_z_color

    def add_grid(self, parent, grid_count=10, grid_step_size=1.0, grid_subdivs=5, grid_center=True, grid_color=[0.7, 0.7, 0.7, 0.5], subgrid_color=[0.7, 0.7, 0.7, 0.25], center_color=[0.9, 0.9, 0.9, 0.75]):
        # save geometry data
        self._grid_geo_parameters.clear()
        self._grid_geo_parameters["grid_count"] = grid_count
        self._grid_geo_parameters["grid_subdivs"] = grid_subdivs
        self._grid_geo_parameters["grid_center"] = grid_center
        self._grid = GridNode(parent=parent, step=grid_step_size, subdivs=grid_subdivs, draw_center=grid_center, count=grid_count, grid_color=grid_color, subgrid_color=subgrid_color, center_color=center_color)
        self._is_grid_exist = True

    def remove_grid(self):
        if self._is_grid_exist:
            self._grid.parent = None
            self._is_grid_exist = False

    def set_grid_data(self, grid_count=10, grid_step_size=1.0, grid_subdivs=5, grid_center=True, grid_color=[0.7, 0.7, 0.7, 0.5], subgrid_color=[0.7, 0.7, 0.7, 0.25], center_color=[0.9, 0.9, 0.9, 0.75]):
        # check is grid shold stay old or we should recreate it
        is_recreate = False
        if "grid_count" in self._grid_geo_parameters.keys() and "grid_subdivs" in self._grid_geo_parameters.keys() and "grid_center" in self._grid_geo_parameters.keys():
            if self._grid_geo_parameters["grid_count"] == grid_count and self._grid_geo_parameters["grid_subdivs"] == grid_subdivs and self._grid_geo_parameters["grid_center"] == grid_center:
                is_recreate = False
            else:
                is_recreate = True
        else:
            is_recreate = True
        if is_recreate:
            self.remove_grid()
            self.add_grid(self._scene, grid_count=grid_count, grid_step_size=grid_step_size, grid_subdivs=grid_subdivs, grid_center=grid_center, grid_color=grid_color, subgrid_color=subgrid_color, center_color=center_color)
        else:
            # the grid geo is the same. Simply change it parameters
            color_array = []
            vert_array = []
            count = self._grid_geo_parameters["grid_count"]
            step = grid_step_size
            subdivs = self._grid_geo_parameters["grid_subdivs"]
            draw_center = self._grid_geo_parameters["grid_center"]
            min_coord = -1 * (count / 2) * step
            subdiv_size = step / subdivs
            for i in range(count + 1):
                # form x=const lines
                shift = min_coord + step * i
                if (draw_center is False) or (draw_center is True and abs(shift) > subdiv_size / 2):
                    vert_array.append([shift, min_coord, 0])
                    vert_array.append([shift, -1*min_coord, 0])
                    color_array.append(grid_color)
                    color_array.append(grid_color)
                    # y=const line
                    vert_array.append([min_coord, shift, 0])
                    vert_array.append([-1 * min_coord, shift, 0])
                    color_array.append(grid_color)
                    color_array.append(grid_color)
                # subdivided lines
                if i < count:
                    for j in range(subdivs - 1):
                        vert_array.append([shift + (j + 1) * subdiv_size, min_coord, 0])
                        vert_array.append([shift + (j + 1) * subdiv_size, -1*min_coord, 0])
                        color_array.append(subgrid_color)
                        color_array.append(subgrid_color)
                        vert_array.append([min_coord, shift + (j + 1) * subdiv_size, 0])
                        vert_array.append([-1*min_coord, shift + (j + 1) * subdiv_size, 0])
                        color_array.append(subgrid_color)
                        color_array.append(subgrid_color)
            if draw_center:
                vert_array.append([0, -1*min_coord, 0])
                vert_array.append([0, min_coord, 0])
                vert_array.append([-1*min_coord, 0, 0])
                vert_array.append([min_coord, 0, 0])
                color_array.append(center_color)
                color_array.append(center_color)
                color_array.append(center_color)
                color_array.append(center_color)
            verts = np.array(vert_array)
            color = np.array(color_array)
            self._grid.set_data(color=color, pos=verts)

    def update(self, canvas_size, camera):
        if self._view_axis_exist:
            self._view_axis.transform.reset()
            cam_matrix = [[0.0 if j == 3 else camera.transform.inv_matrix[i][j] for j in range(4)] for i in range(3)]
            cam_matrix.append([0.0, 0.0, 0.0, 1.0])
            # next apply transform corresponding to orientation mode
            if self._orientation_mode == 0:
                tr = [[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
                self._view_axis.transform.matrix = np.dot(self._view_axis.transform.matrix, tr)
            elif self._orientation_mode == 1:
                tr = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
                self._view_axis.transform.matrix = np.dot(self._view_axis.transform.matrix, tr)
            self._view_axis.transform.matrix = np.dot(self._view_axis.transform.matrix, cam_matrix)
            self._view_axis.transform.scale((-1*self._axis_size, self._axis_size, 0.0001))
            if self._axis_corner == 0:
                self._view_axis.transform.translate((self._axis_shift_x, self._axis_shift_y))
            elif self._axis_corner == 1:
                self._view_axis.transform.translate((self._axis_shift_x, canvas_size[1] - self._axis_shift_y))
            elif self._axis_corner == 2:
                self._view_axis.transform.translate((canvas_size[0] - self._axis_shift_x, canvas_size[1] - self._axis_shift_y))
            else:
                self._view_axis.transform.translate((canvas_size[0] - self._axis_shift_x, self._axis_shift_y))
            self._view_axis.update()
