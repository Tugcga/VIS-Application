import numpy as np
import math

from vispy.color import Color
from vispy import scene
from vispy import geometry

from helpers.obj_loader import OBJLoader
from canvas.canvas_visuals import SceneVisuals
from interaction.keys import KeyClass


class SceneObjects(object):
    def __init__(self, parent_view=None, render_settings=None, orientation=2, scale=1.0, is_centering=True):
        self._meshes = []
        self._view = parent_view
        self._scene = parent_view.scene
        # the set of render settings
        # set it default values
        self._settings_color = Color((0.8, 0.8, 0.8, 1.0))
        self._settings_edge_color = Color((1.0, 0.824, 0.0, 1.0))
        self._settings_point_color = Color((0.0, 0.0, 1.0, 1.0))
        self._settings_point_size = 5.0
        self._settings_show_faces = True
        self._settings_show_wire = False
        self._settings_line_width = 1
        self._settinge_show_points = False
        self._settings_ambient_color = Color((0.1, 0.1, 0.1, 1.0))
        self._settings_light_color = Color((1.0, 1.0, 1.0, 1.0))
        self._settings_light_intensity = 1.0
        self._settings_shiness = 1.0 / 200.0
        self._light_direction = (-1, -1, -1)
        self._light_shift_x = 0.0
        self._light_shift_y = 0.0
        self._orientation = orientation
        self._scale = scale
        self._center_align = is_centering
        if render_settings is not None:  # set render settings by values from host application
            self._save_render_settings(render_settings)

        # readed data
        self._raw_mesh_data = None
        self._mesh_data = None  # here we store mesh-data objects fro createing and modyfying meshes
        self._calc_positions = None
        self._calc_normals = None
        self._edges_data = None
        # points data stored in the _raw_mesh_data[0]

        # visualse on the scene
        self._mesh = None
        self._edges = None
        self._points = None

    def set_orientation(self, mode):
        is_new = False
        if mode != self._orientation:
            is_new = True
        self._orientation = mode
        if is_new:
            if len(self._meshes) > 0:
                self._create_mesh_datas(only_positions=False)
                self._update_polygons(force_positions=True)
                self._update_edges(force_positions=True)
                self._update_points(force_positions=True)

    def set_scale(self, scale):
        self._scale = scale
        if len(self._meshes) > 0:
            self._create_mesh_datas(only_positions=True)
            self._update_polygons(force_positions=True)
            self._update_edges(force_positions=True)
            self._update_points(force_positions=True)

    def set_centering(self, is_centering):
        self._center_align = is_centering
        if len(self._meshes) > 0:
            self._create_mesh_datas(only_positions=True)
            self._update_polygons(force_positions=True)
            self._update_edges(force_positions=True)
            self._update_points(force_positions=True)


    def _read_obj(self, file_path):  # return (positions, poly_faces, edge_faces, normals) as np.array-s
        obj_loader = OBJLoader(file_path)
        normals_map = obj_loader.normals
        normals_exist = True if len(normals_map) > 0 else False
        vertices_map = obj_loader.vertices
        start_face = 0
        faces_list = []
        edges_list = []
        from_to_edges = {}  # key is original pair (i1, i2), value is the edge
        vertices_list = []
        normals_list = []
        for face in obj_loader.faces:
            face_vertices = face[0]
            face_normals = face[1]
            face_length = len(face_vertices)
            # create vertices
            for fv in face_vertices:
                vertices_list.append(vertices_map[fv - 1])
            if normals_exist:
                for fn in face_normals:
                    normals_list.append(normals_map[fn - 1])
            # generate esges and faces ordering data
            e_origin = [face_vertices[0], face_vertices[1]]
            e_origin.sort()
            e_origin = tuple(e_origin)
            e = [start_face, start_face + 1]
            e.sort()
            e = tuple(e)
            # if not e in edges_list:
            if not e_origin in from_to_edges:
                edges_list.append(e)
                from_to_edges[e_origin] = e
            e_origin = [face_vertices[0], face_vertices[face_length - 1]]
            e_origin.sort()
            e_origin = tuple(e_origin)
            e = [start_face, start_face + face_length - 1]
            e.sort()
            e = tuple(e)
            # if not e in edges_list:
            if not e_origin in from_to_edges:
                edges_list.append(e)
                from_to_edges[e_origin] = e
            for i in range(face_length - 2):
                faces_list.append([start_face, start_face + i + 1, start_face + i + 2])
                e_origin = [face_vertices[i + 1], face_vertices[i + 2]]
                e_origin.sort()
                e_origin = tuple(e_origin)
                e = [start_face + i + 1, start_face + i + 2]
                e.sort()
                e = tuple(e)
                if not e_origin in from_to_edges:
                # if not e in edges_list:
                    edges_list.append(e)
                    from_to_edges[e_origin] = e
            start_face += face_length
        return (np.array(vertices_list), np.array(faces_list), np.array(edges_list), np.array(normals_list) if len(normals_list) > 0 else None)

    def clear_scene(self):
        if len(self._meshes) > 0:
            for i in range(len(self._meshes)):
                if self._meshes[i] is not None:
                    self._meshes[i].parent = None
        self._meshes = []
        self._point = None
        self._edges = None
        self._mesh = None

    def is_clear(self):
        return len(self._meshes) == 0

    def get_all_bounds(self):
        mesh_bounds = [(0, 0) for axis in range(3)]
        edges_bounds = [(0, 0) for axis in range(3)]
        points_bounds = [(0, 0) for axis in range(3)]
        if self._mesh is not None:
            mesh_bounds = [self._mesh.bounds(i) for i in range(3)]
        if self._edges is not None:
            if len(self._edges._bounds) >= 3:
                edges_bounds = [self._edges.bounds(i) for i in range(3)]
            else:
                edges_bounds = [self._edges.bounds(0), (0.0, 0.0), self._edges.bounds(1)]
        if self._points is not None:
            points_bounds = [self._points.bounds(i) for i in range(3)]
        return [(min(min(mesh_bounds[i][0], edges_bounds[i][0]), points_bounds[i][0]), max(max(mesh_bounds[i][1], edges_bounds[i][1]), points_bounds[i][1])) for i in range(3)]

    def _add_polygons(self):
        if self._settings_show_faces:
            self._mesh = scene.visuals.Mesh(meshdata=self._mesh_data,
                                            color=self._settings_color,
                                            parent=self._scene,
                                            shading="smooth")
            self._mesh.ambient_light_color = self._settings_ambient_color
            self._mesh.shininess = self._settings_shiness
            self._meshes.append(self._mesh)
        else:
            self._mesh = None

    def _update_polygons(self, force_positions=False):
        if self._mesh is not None and self._settings_show_faces is False:  # remove the polygons visual
            self._meshes.remove(self._mesh)
            self._mesh.parent = None
            self._mesh = None
        elif self._mesh is not None and self._settings_show_faces is True:  # update visual
            self._mesh.color = self._settings_color
            self._mesh.shininess = self._settings_shiness
            self._mesh.ambient_light_color = self._settings_ambient_color
            if force_positions:
                self._mesh.set_data(meshdata=self._mesh_data)
        elif self._mesh is None and self._settings_show_faces is True:  # add polygons
            self._add_polygons()
        self._set_light()

    def _add_edges(self):
        if self._settings_show_wire:
            self._edges = scene.visuals.Mesh(meshdata=self._edges_data,
                                             color=self._settings_edge_color,
                                             mode="lines",
                                             parent=self._scene)
            self._edges.set_gl_state(depth_func="lequal", line_width=self._settings_line_width, polygon_offset=(1.0, 1.0), polygon_offset_fill=True)
            self._meshes.append(self._edges)
        else:
            self._edges = None

    def _update_edges(self, force_positions=False):
        if self._edges is not None and self._settings_show_wire is False:  # remove edges visual
            self._meshes.remove(self._edges)
            self._edges.parent = None
            self._edges = None
        elif self._edges is not None and self._settings_show_wire is True:  # update visual
            self._edges.color = self._settings_edge_color
            if force_positions:
                self._edges.set_data(meshdata=self._edges_data)
            self._edges.set_gl_state(depth_func="lequal", line_width=self._settings_line_width, polygon_offset=(1.0, 1.0), polygon_offset_fill=True)
        elif self._edges is None and self._settings_show_wire is True:  # add edges visual
            self._add_edges()
        self._set_light()

    def _add_points(self):
        if self._settinge_show_points:
            self._points = scene.visuals.Markers(pos=self._calc_positions,
                                                 # pos=self._raw_mesh_data[0],
                                                 edge_width=0.0,
                                                 size=self._settings_point_size,
                                                 face_color=self._settings_point_color,
                                                 parent=self._scene)
            self._points.antialias = 0
            self._meshes.append(self._points)
        else:
            self._points = None

    def _update_points(self, force_positions=False):
        if self._points is not None and self._settinge_show_points is False:  # remove edges visual
            if self._points in self._meshes:
                self._meshes.remove(self._points)
            self._points.parent = None
            self._points = None
        elif self._points is not None and self._settinge_show_points is True:  # update visual
            self._points.set_data(pos=self._calc_positions,
                                  # pos=self._raw_mesh_data[0],
                                  size=self._settings_point_size, edge_width=0.0,
                                  edge_width_rel=None, face_color=self._settings_point_color)
        elif self._points is None and self._settinge_show_points is True:  # add edges visual
            self._add_points()
        self._set_light()

    def _set_light(self):
        if self._mesh is not None:
            self._mesh.light_dir = self._light_direction

    def _apply_transform(self, a, tr, shift):
        v = a - shift
        return tr @ v

    def _apply_orientation_to_values(self, array, use_scale=False):
        shift = [0.0, 0.0, 0.0]
        scale = self._scale if use_scale else 1.0
        if use_scale and self._center_align:
            shift = np.average(array, axis=0)
        if self._orientation == 0:
            # tr = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
            tr = np.array([[0, scale, 0], [0, 0, scale], [scale, 0, 0]])
            return np.apply_along_axis(self._apply_transform, 1, array, tr, shift)
        elif self._orientation == 1:
            # tr = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
            tr = np.array([[0, 0, scale], [scale, 0, 0], [0, scale, 0]])
            return np.apply_along_axis(self._apply_transform, 1, array, tr, shift)
        else:
            tr = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, scale]])
            return np.apply_along_axis(self._apply_transform, 1, array, tr, shift)

    def _create_mesh_datas(self, only_positions=False):
        self._calc_positions = self._apply_orientation_to_values(self._raw_mesh_data[0], use_scale=True)
        set_noramals = False
        if only_positions is False:
            if self._raw_mesh_data[3] is not None:
                self._calc_normals = self._apply_orientation_to_values(self._raw_mesh_data[3], use_scale=False)
                set_noramals = True
        self._mesh_data = geometry.MeshData(vertices=self._calc_positions, faces=self._raw_mesh_data[1])
        if set_noramals:
            self._mesh_data._vertex_normals = self._calc_normals
        self._edges_data = geometry.MeshData(vertices=self._calc_positions, faces=self._raw_mesh_data[2])

    def add_mesh_from_obj_file(self, file_path):
        self.clear_scene()
        # read the data
        self._raw_mesh_data = self._read_obj(file_path)  # (np.array(vertices_list), np.array(faces_list), np.array(edges_list), np.array(normals_list))
        # next create mesh-data objects
        self._create_mesh_datas()
        
        # next add meshes to the scene
        self._add_polygons()
        self._add_edges()
        self._add_points()
        self._set_light()

    def _get_value(self, params, key):
        for p in params:
            if p[0] == key:
                return p[1]
        return None

    def _color_to_float(self, color):
        return [color[i] / 255.0 for i in range(len(color))]

    def _save_render_settings(self, params):
        line_width = self._get_value(params, "line_width")
        if line_width is not None:
            self._settings_line_width = line_width
        show_faces = self._get_value(params, "show_faces")
        if show_faces is not None:
            self._settings_show_faces = show_faces
        show_edges = self._get_value(params, "show_edges")
        if show_edges is not None:
            self._settings_show_wire = show_edges
        show_points = self._get_value(params, "show_points")
        if show_points is not None:
            self._settinge_show_points = show_points
        poly_color = self._get_value(params, "poly_color")
        if poly_color is not None:
            self._settings_color = self._color_to_float(poly_color)
        edge_color = self._get_value(params, "edge_color")
        if edge_color is not None:
            self._settings_edge_color = self._color_to_float(edge_color)
        point_color = self._get_value(params, "point_color")
        if point_color is not None:
            self._settings_point_color = self._color_to_float(point_color)
        shiness = self._get_value(params, "shiness")
        if point_color is not None:
            self._settings_shiness = shiness
        point_size = self._get_value(params, "point_size")
        if point_size is not None:
            self._settings_point_size = point_size
        ambient_color = self._get_value(params, "ambient_color")
        if ambient_color is not None:
            self._settings_ambient_color = self._color_to_float(ambient_color)
        light_color = self._get_value(params, "light_color")
        if light_color is not None:
            self._settings_light_color = self._color_to_float(light_color)
        light_intensity = self._get_value(params, "light_intensity")
        if light_intensity is not None:
            self._settings_light_intensity = light_intensity
        light_shift_x = self._get_value(params, "light_shift_x")
        light_shift_y = self._get_value(params, "light_shift_y")
        if light_shift_x is not None:
            self._light_shift_x = light_shift_x
        if light_shift_y is not None:
            self._light_shift_y = light_shift_y

    def apply_render_settings(self, params=None, changed_param=""):
        self._save_render_settings(params)
        if changed_param in ["show_faces", "ambient_color", "shiness", "poly_color"]:
            self._update_polygons()
        elif changed_param in ["show_edges", "edge_color", "line_width"]:
            self._update_edges()
        elif changed_param in ["show_points", "point_size", "point_color"]:
            self._update_points()
        elif changed_param in ["light_shift_x", "light_shift_y", "light_shift_z"]:
            self.update_camera_callback(self._view.camera.center, self._view.camera.get_position())
        else:  # light_color and light_intensity are not implemented in MeshVisual
            pass

    def _cross(self, a, b):
        return (a[1]*b[2] - a[2]*b[1], -a[0]*b[2] + a[2]*b[0], a[0]*b[1] - a[1]*b[0])

    def _normalize(self, a):
        length = math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2])
        return (a[0] / length, a[1] / length, a[2] / length)

    def _scale_vector(self, s, a):  # a is a vector, s is a scalar
        return (s*a[0], s*a[1], s*a[2])

    def _add_vectors(self, a, b):
        return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

    def _mult_matrix_to_vector(self, m, v):
        to_return = []
        for i in range(3):
            val = 0.0
            for s in range(3):
                val += m[i][s] * v[s]
            to_return.append(val)
        return to_return

    def update_camera_callback(self, center, camera):
        # set light direction
        to_vector = ([center[i] - camera[i] for i in range(3)])
        up_vector = (0.0, 0.0, 1.0)
        x_side = self._normalize(self._cross(to_vector, up_vector))
        y_side = self._normalize(self._cross(x_side, to_vector))
        light_shift = self._add_vectors(self._scale_vector(self._light_shift_x, x_side), self._scale_vector(self._light_shift_y, y_side))
        self._light_direction = ([camera[i] + light_shift[i] - center[i] for i in range(3)])
        self._set_light()


class SceneProperties(object):
    def __init__(self, canvas=None, view=None, scene=None):
        self._canvas = canvas
        self._view = view
        self._scene = scene
        self._visuals = SceneVisuals(scene=scene)  # here we store grid, axis and so on
        self._grid_exist = False
        self._axis_exist = False

    def _get_value(self, params, key):
        for p in params:
            if p[0] == key:
                return p[1]
        return None

    def _color_to_float(self, color):
        return [color[i] / 255.0 for i in range(len(color))]

    def add_visual_view_axis(self, axis_size=50, axis_arrow_size=5.0, width=2.0, axis_corner=1, axis_shift_x=50, axis_shift_y=50, axis_x_color=Color("red"), axis_y_color=Color("green"), axis_z_color=Color("blue")):
        self._visuals.add_view_axis(self._view, axis_size=axis_size, axis_arrow_size=axis_arrow_size, width=width, axis_corner=axis_corner, axis_shift_x=axis_shift_x, axis_shift_y=axis_shift_y, axis_x_color=axis_x_color, axis_y_color=axis_y_color, axis_z_color=axis_z_color)
        self._axis_exist = True

    def add_visual_grid(self, grid_step_size=1.0, grid_count=10, grid_subdivs=5, grid_center=True, grid_color=[0.7, 0.7, 0.7, 0.5], subgrid_color=[0.7, 0.7, 0.7, 0.25], center_color=[0.9, 0.9, 0.9, 0.75]):
        self._visuals.add_grid(self._scene, grid_count=grid_count, grid_step_size=grid_step_size, grid_subdivs=grid_subdivs, grid_center=grid_center, grid_color=grid_color, subgrid_color=subgrid_color, center_color=center_color)
        self._grid_exist = True

    def update_visuals(self, canvas_size, camera):
        self._visuals.update(canvas_size, camera)

    def apply(self, params=None):
        if params is not None:
            # upper axis
            up_axis = self._get_value(params, "up_axis")
            if up_axis is not None:
                self._visuals.set_orientation(up_axis[0])
            # background color
            bg_color = self._get_value(params, "bg_color")
            if bg_color is not None:
                self._canvas.bgcolor = self._color_to_float(bg_color)
            # axis section
            show_axis = self._get_value(params, "show_axis")
            if show_axis is not None:
                if show_axis:
                    # read axis params
                    axis_corner = self._get_value(params, "axis_corner")[0]
                    axis_shift_x = self._get_value(params, "axis_shift_x")
                    axis_shift_y = self._get_value(params, "axis_shift_y")
                    axis_x_color = self._get_value(params, "axis_x_color")
                    axis_y_color = self._get_value(params, "axis_y_color")
                    axis_z_color = self._get_value(params, "axis_z_color")
                    axis_size = self._get_value(params, "axis_size")
                    axis_width = self._get_value(params, "axis_width")
                    axis_arrow_size = self._get_value(params, "axis_arrow_size")
                    if self._axis_exist is False:
                        self.add_visual_view_axis(axis_corner=axis_corner,
                                                  axis_size=axis_size,
                                                  width=axis_width,
                                                  axis_arrow_size=axis_arrow_size,
                                                  axis_shift_x=axis_shift_x,
                                                  axis_shift_y=axis_shift_y,
                                                  axis_x_color=self._color_to_float(axis_x_color),
                                                  axis_y_color=self._color_to_float(axis_y_color),
                                                  axis_z_color=self._color_to_float(axis_z_color))
                    else:
                        # arrow exist. Set it data
                        self._visuals.set_axis_data(axis_size=axis_size, width=axis_width, axis_arrow_size=axis_arrow_size, axis_corner=axis_corner, axis_shift_x=axis_shift_x, axis_shift_y=axis_shift_y, axis_x_color=self._color_to_float(axis_x_color), axis_y_color=self._color_to_float(axis_y_color), axis_z_color=self._color_to_float(axis_z_color))
                else:
                    self._visuals.remove_axis()
                    self._axis_exist = False
            # grid section
            show_grid = self._get_value(params, "show_grid")
            if show_grid is not None:
                if show_grid:
                    # read grid parameters
                    grid_step_size = self._get_value(params, "grid_step_size")
                    grid_subdivs = self._get_value(params, "grid_subdivs")
                    grid_count = self._get_value(params, "grid_count")
                    grid_center = self._get_value(params, "grid_center")
                    grid_color = self._get_value(params, "grid_color")
                    grid_subgrid_color = self._get_value(params, "grid_subgrid_color")
                    grid_center_color = self._get_value(params, "grid_center_color")
                    if self._grid_exist:
                        self._visuals.set_grid_data(grid_step_size=grid_step_size,
                                                    grid_subdivs=grid_subdivs,
                                                    grid_center=grid_center,
                                                    grid_count=grid_count,
                                                    grid_color=self._color_to_float(grid_color),
                                                    subgrid_color=self._color_to_float(grid_subgrid_color),
                                                    center_color=self._color_to_float(grid_center_color))
                    else:
                        self.add_visual_grid(grid_step_size=grid_step_size,
                                             grid_subdivs=grid_subdivs,
                                             grid_center=grid_center,
                                             grid_count=grid_count,
                                             grid_color=self._color_to_float(grid_color),
                                             subgrid_color=self._color_to_float(grid_subgrid_color),
                                             center_color=self._color_to_float(grid_center_color))
                else:
                    self._visuals.remove_grid()
                    self._grid_exist = False
        self.update_visuals(self._canvas.size, self._canvas._cameras.current_camera)


class SceneCameras(object):
    def __init__(self):
        self._cameras_list = []
        self._cameras_count = 0
        self._current_camera = None
        self._current_camera_index = -1

    def add_camera(self, camera, set_current=True):
        self._cameras_list.append(camera)
        self._cameras_count = len(self._cameras_list)
        if set_current:
            self._current_camera_index = self._cameras_count - 1
            self._current_camera = camera

    @property
    def current_camera(self):
        if self._current_camera_index > -1 and self._current_camera_index < self._cameras_count:
            return self._current_camera
        else:
            return None

    def get_camera(self, index):
        if index >= 0 and index < self._cameras_count:
            return self._cameras_list[index]
        else:
            if index < 0:
                return self._cameras_list[0]
            if index >= self._cameras_count:
                return self._cameras_list[self._cameras_count - 1]

    @property
    def current_camera_index(self):
        return self._current_camera_index

    def set_camera(self, index):
        if index >= 0 and index < self._cameras_count and index != self._current_camera_index:
            self._current_camera_index = index
            self._current_camera = self._cameras_list[index]
            return True
        else:
            return False


class CameraPerspective(scene.cameras.TurntableCamera):
    def __init__(self, key_controller=None, on_changed=None, fov=60.0, elevation=30.0, azimuth=90.0, distance=2.5, parent_scene=None, **kwargs):
        super(CameraPerspective, self).__init__(fov=fov, elevation=elevation, azimuth=azimuth, distance=distance, **kwargs)
        # self._active = True
        self._scene = parent_scene
        self._on_changed = on_changed
        self._current_symbols = []
        self._current_keys = KeyClass()  # store last pressed keys
        if key_controller is not None:
            self._camera_keys = key_controller.get_camera_keys()
        else:
            self._camera_keys = None
        if self._camera_keys is not None:
            self._camera_keys_init = True
        else:
            self._camera_keys_init = False

        self.center = (0.0, 0.0, 0.0)

    def _get_position_from_transform(self, matrix):
        return [matrix[3][i] for i in range(3)]

    def get_position(self):
        return tuple(self._get_position_from_transform(self.transform.matrix))

    def get_center(self):
        return self.center

    def key_event(self, key):  # key is KeyClass with all pressed symbols
        self._current_keys = key

    def set_fov(self, new_fov):
        self.fov = new_fov

    def viewbox_mouse_event(self, event):
        should_update = False
        if event.handled:
            return
        if event.type == "mouse_release":
            self._event_value = None
        elif event.type == "mouse_press":
            event.handled = True
        elif event.type == "mouse_move":
            if event.press_event is None:
                return

            modifiers = event.mouse_event.modifiers
            p1 = event.mouse_event.press_event.pos
            p2 = event.mouse_event.pos
            d = p2 - p1
            # form KeyClass from curent state
            key = KeyClass(self._current_keys.get_symbols(), modifiers, [b for b in event.buttons])
            cam_mode = self._camera_keys.get_mode(key)
            if cam_mode == 1:  # rotate
                self._update_rotation(event)
                should_update = True
            elif cam_mode == 2:  # pan
                # Translate
                norm = np.mean(self._viewbox.size)
                if self._event_value is None or len(self._event_value) == 2:
                    self._event_value = self.center
                dist = (p1 - p2) / norm * self._scale_factor
                dist[1] *= -1
                dx, dy, dz = self._dist_to_trans(dist)
                ff = self._flip_factors
                up, forward, right = self._get_dim_vectors()
                dx, dy, dz = right * dx + forward * dy + up * dz
                dx, dy, dz = ff[0] * dx, ff[1] * dy, dz * ff[2]
                c = self._event_value
                self.center = c[0] + dx, c[1] + dy, c[2] + dz
                should_update = True
            elif cam_mode == 3:  # zoom
                if self._event_value is None:
                    self._event_value = (self._scale_factor, self._distance)
                zoomy = (1 - self.zoom_factor) ** d[1]
                self.scale_factor = self._event_value[0] * zoomy
                # Modify distance if its given
                if self._distance is not None:
                    self._distance = self._event_value[1] * zoomy
                self.view_changed()
                should_update = True
        if should_update:
            self._on_changed()