import os
from vispy import scene
from canvas.canvas_items import SceneObjects, SceneProperties, SceneCameras, CameraPerspective


class Canvas(scene.SceneCanvas):
    def __init__(self, key_controller=None, host_press_event=None, host_release_event=None, scene_properties=None, render_parameters=None):
        scene.SceneCanvas.__init__(self, keys=None, vsync=False)
        self.unfreeze()
        self._key_controller = key_controller
        self._host_press_event = host_press_event
        self._host_release_event = host_release_event
        self._cameras = SceneCameras()
        self.view = self.central_widget.add_view()
        self._objects = SceneObjects(parent_view=self.view,
                                     render_settings=render_parameters,
                                     orientation=self._get_param_value(scene_properties, "up_axis")[0],
                                     scale=self._get_param_value(scene_properties, "scale"),
                                     is_centering=self._get_param_value(scene_properties, "center"))
        self._scene_properties = SceneProperties(canvas=self, view=self.view, scene=self.view.scene)
        self.freeze()

        # self._clear_scene()  # <-------- turn on!!!

        # create perspective camera
        self._cameras.add_camera(CameraPerspective(key_controller=key_controller,
                                                   name="Perspective camera",
                                                   on_changed=self.on_camera_changed,
                                                   parent_scene=self.view.scene,
                                                   fov=self._get_param_value(scene_properties, "camera_fov")))
        # connect camera to the view
        self.view.camera = self._cameras.current_camera
        self._objects.update_camera_callback(self._cameras.current_camera.get_center(), self._cameras.current_camera.get_position())

        # set canvas parameters. Visual, colors and so on
        self._scene_properties.apply(scene_properties)

        # next set canvas commands
        self._key_controller.set_camera_event(self._cameras.current_camera.key_event)
        self._key_controller.add_function("Fix area", self.command_fix_area)

    # --------------Scene process---------------------------
    def set_camera(self, index):
        old_index = self._cameras.current_camera_index
        is_change = self._cameras.set_camera(index)
        if is_change:
            self._cameras.get_camera(old_index).make_unactive()
            self.view.camera = self._cameras.current_camera
            self._cameras.current_camera.make_active()
            self._scene_properties.update_visuals(self.size, self._cameras.current_camera)

    def add_mesh_from_file(self, file_path):
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1]
            if ext == ".obj" or ext == ".OBJ":
                self._objects.add_mesh_from_obj_file(file_path)
            else:
                print("Only *.obj file can be opened")
        else:
            print("There is not file " + file_path)

    # --------------Technical functions---------------------
    def _clear_scene(self):
        count = len(self.view.scene.children)
        i = count - 1
        while i >= 0:
            self.view.scene._remove_child(self.view.scene.children[i])
            i = i - 1

    def _get_param_value(self, params, key):
        for p in params:
            if p[0] == key:
                return p[1]
        return None

    # -------------Events----------------------------------
    def on_camera_changed(self):  # this method called by camera instance when it change position
        self._scene_properties.update_visuals(self.size, self._cameras.current_camera)
        self._objects.update_camera_callback(self._cameras.current_camera.get_center(), self._cameras.current_camera.get_position())

    def on_mouse_press(self, event):
        pass

    def on_mouse_release(self, event):
        pass

    def on_mouse_double_click(self, event):
        pass

    def on_mouse_move(self, event):
        pass

    def on_mouse_wheel(self, event):
        pass

    def on_key_press(self, event):  # key pressed catched by the host is not transfered to the canvas
        k = event.key
        if k is not None:
            self._key_controller.pressed_keys.add(k.name)
            is_catch = self._key_controller.check_event()
            if is_catch is False:
                self._host_press_event(event, pressed_keys=self._key_controller.pressed_keys, from_canvas=True)

    def on_key_release(self, event):
        k = event.key
        if k is not None:
            if k.name in self._key_controller.pressed_keys:
                self._key_controller.pressed_keys.remove(k.name)
            is_catch = self._key_controller.check_event()
            if is_catch is False:
                self._host_release_event(event, pressed_keys=self._key_controller.pressed_keys, from_canvas=True)

    def on_resize(self, event):
        scene.SceneCanvas.on_resize(self, event)
        self._scene_properties.update_visuals(self.size, self._cameras.current_camera)

    # ---------Host application callbacks------------------
    def properties_change(self, params=None, changed_name=None, old_value=None, new_value=None, type=None):  # the host should call this method when user change any of properties parameters
        self._scene_properties.apply(params)
        # also orientation set for objects
        if changed_name == "up_axis":
            self._objects.set_orientation(new_value[0])
        elif changed_name == "scale":
            self._objects.set_scale(new_value)
        elif changed_name == "center":
            self._objects.set_centering(new_value)
        elif changed_name == "camera_fov":
            self._cameras.current_camera.set_fov(new_value)

    def render_settings_change(self, params=None, changed_name=None, old_value=None, new_value=None, type=None):
        # print("render settings changed")
        self._objects.apply_render_settings(params, changed_name)

    # ---------Canvas commands-----------------------------
    def clear_keys(self):
        self._key_controller.clear()

    def command_fix_area(self):
        b = self._objects.get_all_bounds()
        if self._objects.is_clear() or (b[0] == (0, 0) and b[1] == (0, 0) and b[2] == (0, 0)):
            self._cameras.current_camera.reset()
            self._cameras.current_camera._distance = 2.5
            self._cameras.current_camera.view_changed()
            self._scene_properties.update_visuals(self.size, self._cameras.current_camera)
        else:
            self._cameras.current_camera.set_range(x=b[0], y=b[1], z=b[2])
            self._cameras.current_camera._distance = self._cameras.current_camera.scale_factor
            self._cameras.current_camera.view_changed()

    def command_clear_scene(self):
        self._objects.clear_scene()
