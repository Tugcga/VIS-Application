import os
from PyQt4 import QtGui, QtCore

from helpers.read_data import read_render_settings_from_file, read_scene_properties_from_file, read_style_settings_from_file, get_data_path
from canvas.canvas_main import Canvas
from interaction.keys import KeyController
from helpers.gui_classes import LayoutData

from data.stylesheets.style_aqua.aqua.qsshelper import QSSHelper
from data.stylesheets.style_dark import load_stylesheet_pyqt


class MainWindow(QtGui.QMainWindow):
    def _create_float_window(self, area_widget, window_type=""):  # used for scene_properties, render_settings and so on
        content = QtGui.QWidget()
        area_widget.horizontalScrollBar().setEnabled(False)
        area_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        content.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        area_widget.installEventFilter(self)
        params = None
        ext_return = False  # turn on if we wuld like to return not only parameters, but also some external data
        ext_data = None
        if window_type == "scene_properties":
            params = read_scene_properties_from_file(get_data_path("scene_properties.xml"), content)
        elif window_type == "render_settings":
            params = read_render_settings_from_file(get_data_path("render_settings.xml"), content)
        elif window_type == "style_settings":
            (params, ext_data) = read_style_settings_from_file(get_data_path("style_settings.xml"), content)
            ext_return = True
        area_widget.setWidget(content)
        if ext_return:
            return (params, ext_data)
        else:
            return params

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.DOC_START_WIDTH = 300
        self.DOC_START_HEIGHT = 480
        self.MAIN_WINDOW_WIDTH = 800
        self.MAIN_WINDOW_HEIGHT = 600
        self._last_open_dir = ""
        self._key_controller = KeyController()
        self._key_controller.init_keys(get_data_path("shortcuts.xml"))
        self._dockable_list = []  # store dockable widgets in the form [[doc, area, state, width, height], ...] where state=0 - floating window, 1 - docked window
        self._doc_to_index = {}  # map from window name to it index in the list

        # get scene properties from file or form standart
        self._layout_data = LayoutData(get_data_path("layout.xml"))
        self.scene_prop_area = QtGui.QScrollArea()
        self.scene_prop_params = self._create_float_window(self.scene_prop_area, "scene_properties")
        # render settings
        self.render_settings_area = QtGui.QScrollArea()
        self.render_settings_params = self._create_float_window(self.render_settings_area, "render_settings")
        # style change window
        self.style_settings_area = QtGui.QScrollArea()
        s_d = self._create_float_window(self.style_settings_area, "style_settings")
        self.style_settings_params = s_d[0]
        self.style_data = s_d[1]

        self.setWindowTitle("VIS Application")

        self.canvas = Canvas(key_controller=self._key_controller,
                             host_press_event=self.keyPressEvent,
                             host_release_event=self.keyReleaseEvent,
                             scene_properties=self.scene_prop_params.get_parameters(),
                             render_parameters=self.render_settings_params.get_parameters())
        self.canvas.measure_fps(0.1, self.show_fps)
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        self.scene_prop_params.set_change_callback(self.canvas.properties_change)
        self.render_settings_params.set_change_callback(self.canvas.render_settings_change)
        self.style_settings_params.set_change_callback(self.change_style_callback)
        self.change_style_callback(params=self.style_settings_params.get_parameters())

        # FPS message in statusbar:
        self.status = self.statusBar()
        self.status.showMessage("...")

        # add file menus
        file_menu = self.menuBar().addMenu("File")
        open_key = self._key_controller.get_command_key("open")
        if open_key is not None:
            open_action = file_menu.addAction(self._key_controller.get_command_label("open"))
            open_action.setShortcut(open_key.get_key_string())
            open_action.setStatusTip("Open and import file to the scene")
            open_action.triggered.connect(self.open_command)
        exit_key = self._key_controller.get_command_key("quit")
        if exit_key is not None:
            exit_action = file_menu.addAction(self._key_controller.get_command_label("quit"))
            exit_action.setShortcut(exit_key.get_key_string())
            exit_action.setStatusTip("Close the application")
            exit_action.triggered.connect(self.close_command)

        # add view menu
        view_menu = self.menuBar().addMenu("View")
        # open properties window
        props_key = self._key_controller.get_command_key("show_poroperties")
        if props_key is not None:
            properties_action = view_menu.addAction(self._key_controller.get_command_label("show_poroperties"))
            properties_action.setShortcut(props_key.get_key_string())
            properties_action.setStatusTip("Open properties window")
            properties_action.triggered.connect(self.properties_command)
        # open render settings
        render_key = self._key_controller.get_command_key("show_render_settings")
        if render_key is not None:
            render_settings_action = view_menu.addAction(self._key_controller.get_command_label("show_render_settings"))
            render_settings_action.setShortcut(render_key.get_key_string())
            render_settings_action.setStatusTip("Open render settings window")
            render_settings_action.triggered.connect(self.render_settings_command)
        # open style settings
        style_key = self._key_controller.get_command_key("show_style_settings")
        if style_key is not None:
            style_settings_action = view_menu.addAction(self._key_controller.get_command_label("show_style_settings"))
            style_settings_action.setShortcut(style_key.get_key_string())
            style_settings_action.setStatusTip("Open style settings window")
            style_settings_action.triggered.connect(self.style_settings_command)
        # alow edit layout
        self._edit_layout = False
        layout_key = self._key_controller.get_command_key("edit_layout")
        self._edit_layout_text = self._key_controller.get_command_label("edit_layout")
        if layout_key is not None:
            self._edit_layout_action = view_menu.addAction(self._form_edit_layout_text())
            self._edit_layout_action.setShortcut(layout_key.get_key_string())
            self._edit_layout_action.setStatusTip("Enable/Disable layout editing")
            self._edit_layout_action.triggered.connect(self.edit_layout_command)

        # add commands menu
        commands_menu = self.menuBar().addMenu("Commands")
        clear_command_key = self._key_controller.get_command_key("clear_scene")
        if clear_command_key is not None:
            clear_command_action = commands_menu.addAction(self._key_controller.get_command_label("clear_scene"))
            clear_command_action.setShortcut(clear_command_key.get_key_string())
            clear_command_action.setStatusTip("Clear scene")
            # clear_command_action.triggered.connect(self.canvas.command_clear_scene)
            clear_command_action.triggered.connect(self.clear_command)
        fit_camera_command_key = self._key_controller.get_command_key("fit_camera")
        if fit_camera_command_key is not None:
            fit_camera_command_action = commands_menu.addAction(self._key_controller.get_command_label("fit_camera"))
            fit_camera_command_action.setShortcut(fit_camera_command_key.get_key_string())
            fit_camera_command_action.setStatusTip("Frame camera view")
            fit_camera_command_action.triggered.connect(self.canvas.command_fix_area)

        # set widgets
        self.setCentralWidget(self.canvas.native)
        self._create_scene_properties()
        self._create_render_settings()
        self._create_style_settings()

        # set the size of the main window
        main_data = self._layout_data.get_data("main_window")
        is_maximized = False
        if main_data is not None and "is_maximized" in main_data.keys():
            is_maximized = True if main_data["is_maximized"] == "True" else False
        if is_maximized:
            self.showMaximized()
        else:
            main_width = (main_data["width"] if "width" in main_data.keys() else self.MAIN_WINDOW_WIDTH) if main_data is not None else self.MAIN_WINDOW_WIDTH
            main_height = (main_data["height"] if "height" in main_data.keys() else self.MAIN_WINDOW_HEIGHT) if main_data is not None else self.MAIN_WINDOW_HEIGHT
            self.resize(main_width, main_height)  # each time the height is grow to 20 pixels. It's wrong behaviour. It's because is doced widgets
            if main_data is not None and "position_x" in main_data.keys() and "position_x" in main_data.keys():
                self.move(main_data["position_x"], main_data["position_y"])

    def _form_edit_layout_text(self):
        if self._edit_layout:
            return self._edit_layout_text[7:]  # remove first word from Enable/Disable Layout Edit
        else:
            return self._edit_layout_text[:6] + self._edit_layout_text[14:]

    def show_fps(self, fps):
        self.status.showMessage("FPS: %.2f" % (fps, ))

    def keyPressEvent(self, event, pressed_keys=None, from_canvas=False):
        # print("Host event: " + str(pressed_keys) + " from canvas: " + str(from_canvas))
        pass

    def keyReleaseEvent(self, event, pressed_keys=None, from_canvas=False):
        pass

    def _get_data_from_stylesheet(self, file_path):
        to_return = ""
        with open(file_path, "r") as file:
            to_return = file.read()
        return to_return

    def change_style_callback(self, params=None, changed_name=None, old_value=None, new_value=None, type=None):
        # get current style name
        style_name = None
        use_colors = None
        for p in params:
            if p[0] == "style_names":
                style_name = p[1][1][p[1][0]]
            elif p[0] == "use_colors":
                use_colors = p[1]
        # apply styles
        if style_name is not None:
            if self.style_data.is_factory(style_name):  # set the factory style
                self.setStyleSheet("")
                QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(style_name))
            else:  # use css
                if self.style_data.is_qss(style_name):
                    qss_path = self.style_data.get_qss_path(style_name)
                    if qss_path is not None:
                        use_colors = None
                        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("WindowsVista"))
                        # for special styles use special methods
                        if style_name == "aqua":
                            qss = QSSHelper.open_qss(qss_path)
                            self.setStyleSheet(qss)
                        elif style_name == "dark_style":
                            dark_stylesheet = load_stylesheet_pyqt()
                            self.setStyleSheet(dark_stylesheet)
                        else:
                            self.setStyleSheet(self._get_data_from_stylesheet(qss_path))
        # and colors
        if use_colors is not None:
            if use_colors:
                QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())
            else:
                QtGui.QApplication.setPalette(self.style_data.get_original_palette())

    def _init_doc_widget(self, doc_widget, doc_area, saved_data=None, doc_name=""):
        widget_state = ((0 if saved_data["is_floating"] else 1) if "is_floating" in saved_data.keys() else 0) if saved_data is not None else 0  # state = 0 - floating, 1 - doced
        doc_widget.topLevelChanged.connect(lambda value: self.doc_topLevelChanged_signal(value, doc_name))
        doc_widget.visibilityChanged.connect(lambda value: self.doc_visibilityChanged_signal(value, doc_name))
        doc_widget.setFloating(widget_state == 0)
        r_area = QtCore.Qt.RightDockWidgetArea
        l_area = QtCore.Qt.LeftDockWidgetArea
        area_to_doc = ((l_area if saved_data["area_index"] == 1 else r_area) if "area_index" in saved_data.keys() else r_area) if saved_data is not None else r_area
        doc_width = (saved_data["width"] if "width" in saved_data.keys() else self.DOC_START_WIDTH) if saved_data is not None else self.DOC_START_WIDTH
        doc_height = (saved_data["height"] if "height" in saved_data.keys() else self.DOC_START_HEIGHT) if saved_data is not None else self.DOC_START_HEIGHT
        # try to tabbify this dic widget
        tab_target = None
        if saved_data is not None and "tabify" in saved_data.keys():
            tabbed_list = saved_data["tabify"]
            if len(tabbed_list) > 0:
                # try to find emited widgets
                for t in tabbed_list:
                    if t in self._doc_to_index.keys():
                        tab_target = self._dockable_list[self._doc_to_index[t]][0]
        if tab_target is None:
            self.addDockWidget(area_to_doc, doc_widget)
        else:
            self.tabifyDockWidget(tab_target, doc_widget)
        # set properties to widget
        doc_widget.setWidget(doc_area)
        doc_area.width = doc_width
        doc_area.height = doc_height
        self._dockable_list.append([doc_widget, doc_area, widget_state, doc_width, doc_height])  # 3, 4 params are fixed widht and height
        self._doc_to_index[doc_name] = len(self._dockable_list) - 1
        if saved_data is not None and "position_x" in saved_data.keys() and "position_y" in saved_data.keys():
            doc_widget.move(saved_data["position_x"], saved_data["position_y"])
        self._check_doc_layout(self._dockable_list[len(self._dockable_list) - 1])

    def _create_scene_properties(self):
        saved_data = self._layout_data.get_data("scene_properties")
        self._scene_properties_doc = QtGui.QDockWidget("Scene Properties", self)
        self._init_doc_widget(self._scene_properties_doc, self.scene_prop_area, saved_data=saved_data, doc_name="scene_properties")
        is_visible = (saved_data["is_visible"] if "is_visible" in saved_data.keys() else False) if saved_data is not None else False
        pos = self._get_pos_from_doc_data(saved_data)
        if is_visible:
            self._show_doc(self._scene_properties_doc, pos_x=pos[0], pos_y=pos[1])
        else:
            self._scene_properties_doc.hide()

    def _create_render_settings(self):
        saved_data = self._layout_data.get_data("render_settings")
        self._render_settings_doc = QtGui.QDockWidget("Render Settings", self)
        self._init_doc_widget(self._render_settings_doc, self.render_settings_area, saved_data=saved_data, doc_name="render_settings")
        is_visible = (saved_data["is_visible"] if "is_visible" in saved_data.keys() else False) if saved_data is not None else False
        pos = self._get_pos_from_doc_data(saved_data)
        if is_visible:
            self._show_doc(self._render_settings_doc, pos_x=pos[0], pos_y=pos[1])
        else:
            self._render_settings_doc.hide()

    def _create_style_settings(self):
        saved_data = self._layout_data.get_data("style_settings")
        self._style_settings_doc = QtGui.QDockWidget("Style Settings", self)
        self._init_doc_widget(self._style_settings_doc, self.style_settings_area, saved_data=saved_data, doc_name="style_settings")
        is_visible = (saved_data["is_visible"] if "is_visible" in saved_data.keys() else False) if saved_data is not None else False
        pos = self._get_pos_from_doc_data(saved_data)
        if is_visible:
            self._show_doc(self._style_settings_doc, pos_x=pos[0], pos_y=pos[1])
        else:
            self._style_settings_doc.hide()

    def _get_pos_from_doc_data(self, doc_data):
        if doc_data is not None and "position_x" in doc_data.keys() and "position_y" in doc_data.keys():
            return (doc_data["position_x"], doc_data["position_y"])
        else:
            return (None, None)

    def _show_doc(self, doc, pos_x=None, pos_y=None):
        doc.show()
        if pos_x is not None and pos_y is not None:
            doc.move(pos_x, pos_y)

    def properties_command(self):
        if self._scene_properties_doc is not None and self._scene_properties_doc.isVisible() is False:
            self._show_doc(self._scene_properties_doc)

    def render_settings_command(self):
        if self._render_settings_doc is not None and self._render_settings_doc.isVisible() is False:
            self._show_doc(self._render_settings_doc)

    def style_settings_command(self):
        if self._style_settings_doc is not None and self._style_settings_doc.isVisible() is False:
            self._show_doc(self._style_settings_doc)

    def eventFilter(self, source, event):
        if event.type() == 14:  # resize event
            # iterate throw dockable list and find event are widget
            for doc_widget_data in self._dockable_list:
                if doc_widget_data[1] == source:  # area is the second element in the data
                    width = source.size().width() - min(source.verticalScrollBar().width(), 17)  # MAGIC 17 - when window appear the scroll size is 100. Usual is 17
                    doc_widget_data[3] = source.size().width()
                    doc_widget_data[4] = source.size().height()
                    # and also for all tabbed
                    for t in self.tabifiedDockWidgets(doc_widget_data[0]):
                        for t_doc_data in self._dockable_list:
                            if t_doc_data[0] == t:
                                t_doc_data[3] = doc_widget_data[3]
                                t_doc_data[4] = doc_widget_data[4]
                    source.widget().resize(width, source.widget().size().height())
        return super(MainWindow, self).eventFilter(source, event)

    def closeEvent(self, event):
        self._layout_data.save_xml(get_data_path("layout.xml"), self._dockable_list, self._doc_to_index, self)
        self.scene_prop_params.save_xml(get_data_path("scene_properties.xml"))
        self.render_settings_params.save_xml(get_data_path("render_settings.xml"))
        self.style_settings_params.save_xml(get_data_path("style_settings.xml"))

    def open_command(self):
        self.canvas.clear_keys()
        file_path = QtGui.QFileDialog.getOpenFileName(self, "Open file...", self._last_open_dir, "Obj file (*.obj)")
        if len(file_path) > 0:
            self._last_open_dir = os.path.split(file_path)[0]
            if os.path.isfile(file_path):
                self.canvas.add_mesh_from_file(file_path)

    def close_command(self):
        # with message box
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Do you really want to close the application?")
        msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        retval = msg.exec_()
        self.canvas.clear_keys()
        if retval == 16384:
            # disconnect signals
            for doc in self._dockable_list:
                doc[0].topLevelChanged.disconnect()
                doc[0].visibilityChanged.disconnect()
            QtGui.qApp.quit()

    def clear_command(self):
        # create message box
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)

        msg.setText("Do you really wont to clear all meshes from the scene?")
        msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        retval = msg.exec_()
        self.canvas.clear_keys()
        if retval == 16384:
            self.canvas.command_clear_scene()

    def _set_enable_layout(self, doc_data):  # doc_data = [doc, area, state, width]
        if doc_data[1] is not None:
            doc_data[1].setMinimumWidth(0)
            doc_data[1].setMaximumWidth(16777215)
            doc_data[1].setMinimumHeight(0)
            doc_data[1].setMaximumHeight(16777215)
        doc_data[0].setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetClosable)
        doc_data[0].setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

    # def _set_disable_layout(self, doc, area, state):
    def _set_disable_layout(self, doc_data):  # doc_data = [doc, area, state, width]
        if doc_data[2] == 0:  # doc is floating
            doc_data[0].setFloating(True)
            doc_data[0].setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetFloatable)
        else:  # doc is not floating
            doc_data[0].setFloating(False)
            doc_data[0].setFeatures(QtGui.QDockWidget.DockWidgetClosable)
            if doc_data[1] is not None:
                doc_data[1].setFixedWidth(doc_data[3])
                # doc_data[1].setFixedHeight(doc_data[4] - 22)  # this 22 is MAGIC
                doc_data[1].setFixedHeight(doc_data[4])
                # and also for docs in the same tabb
                for d in self.tabifiedDockWidgets(doc_data[0]):
                    d.widget().setFixedWidth(doc_data[3])
                    # d.widget().setFixedHeight(doc_data[4] - 22)
                    d.widget().setFixedHeight(doc_data[4])
        doc_data[0].setAllowedAreas(QtCore.Qt.NoDockWidgetArea)

    def _check_doc_layout(self, doc_data):
        if self._edit_layout:
            self._set_enable_layout(doc_data)
        else:
            self._set_disable_layout(doc_data)

    def doc_topLevelChanged_signal(self, value, key):
        if key in self._doc_to_index.keys():
            index = self._doc_to_index[key]
            self._dockable_list[index][2] = 0 if value is True else 1
            self._check_doc_layout(self._dockable_list[index])

    def doc_visibilityChanged_signal(self, value, key):
        if key in self._doc_to_index.keys():
            index = self._doc_to_index[key]
            doc_area = self._dockable_list[index][1]
            if self._dockable_list[index][0].isFloating():
                if value is True:  # doc start visible
                    doc_area.setMinimumWidth(0)
                    doc_area.setMinimumHeight(0)
                    # also for docs in the same tab
                    for d in self.tabifiedDockWidgets(self._dockable_list[index][0]):
                        d.widget().setMinimumWidth(0)
                        d.widget().setMinimumHeight(0)
                else:  # doc start hidden.
                    # Fix minimum size only if it is not tabbed
                    if len(self.tabifiedDockWidgets(self._dockable_list[index][0])) == 0:
                        m_height = self._dockable_list[index][4]
                        doc_area.setMinimumWidth(self._dockable_list[index][3])
                        doc_area.setMinimumHeight(m_height)

    def edit_layout_command(self):
        if self._edit_layout is False:
            self._edit_layout = True
            self._edit_layout_action.setText(self._form_edit_layout_text())
            for w in self._dockable_list:
                self._set_enable_layout(w)
        else:
            self._edit_layout = False
            self._edit_layout_action.setText(self._form_edit_layout_text())
            for w in self._dockable_list:
                self._set_disable_layout(w)
