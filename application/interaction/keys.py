import xml.etree.cElementTree as ET
import copy
import os

import vispy.util.keys as keys

from interaction.commands import CommandClass


class KeyClass(object):
    # store data as pair (symbol_array, modifier_array). To identify complex keys. Modifiers should be only alt, ctrl or shift. Symbols are not these keys
    # mouse_array contains array of 1, 2, 3 for mouse buttons in the key
    def is_modifier(self, k):
        if k == keys.SHIFT or k == keys.ALT or k == keys.CONTROL:
            return True
        return False

    def __init__(self, symbol_array=[], mod_array=[], mouse_array=[]):
        self._is_correct = False
        self._symbols = []
        self._modifiers = []
        self._mouse = []
        if len(symbol_array) > 0 or len(mod_array) > 0 or len(mouse_array) > 0:
            for s in symbol_array:
                if self.is_modifier(s) is False:
                    self._is_correct = True
                    self._symbols.append(s)
            for m in mod_array:
                if self.is_modifier(m):
                    self._is_correct = True
                    self._modifiers.append(m)
            b_array = [1, 2, 3]
            for b in mouse_array:
                if b in b_array:
                    self._is_correct = True
                    self._mouse.append(b)

    def get_symbols(self):
        return self._symbols

    def get_modifiers(self):
        return self._modifiers

    def get_mouse_buttons(self):
        return self._mouse

    def get_is_correct(self):
        return self._is_correct

    def is_equal(self, key):
        if self._is_correct is False or key.get_is_correct() is False:
            return False
        k_symbols = key.get_symbols()
        k_modifiers = key.get_modifiers()
        k_buttons = key.get_mouse_buttons()
        if len(self._symbols) == len(k_symbols) and len(self._modifiers) == len(k_modifiers) and len(self._mouse) == len(k_buttons):
            def is_in_array(v, array):
                for w in array:
                    if v == w:
                        return True
                return False

            for s in self._symbols:
                if is_in_array(s, k_symbols) is False:
                    return False
            for m in self._modifiers:
                if is_in_array(m, k_modifiers) is False:
                    return False
            for b in self._mouse:
                if is_in_array(b, k_buttons) is False:
                    return False
            return True
        else:
            return False

    def get_modifs_string(self):
        to_return = []
        for m in self._modifiers:
            if self.is_modifier(m):
                to_return.append("Shift" if m == keys.SHIFT else ("Ctrl" if m == keys.CONTROL else ("Alt" if m == keys.ALT else "")))
        return "+".join(to_return)

    def get_symbols_string(self):
        to_return = []
        for k in self._symbols:
            to_return.append(str(k.name).capitalize())
        return "+".join(to_return)

    def get_key_string(self):
        mods = self.get_modifs_string()
        symbols = self.get_symbols_string()
        if len(mods) == 0:
            return symbols
        else:
            return mods + "+" + symbols

    def get_mouse_buttons_string(self):
        to_return = []
        if 1 in self._mouse:
            to_return.append("Left")
        if 2 in self._mouse:
            to_return.append("Right")
        if 3 in self._mouse:
            to_return.append("Middle")
        return "+".join(to_return)

    def to_string(self):
        if self._is_correct:
            mod_array = []
            sym_array = []
            button_array = []
            for m in self._modifiers:
                mod_array.append(str(m.name))
            for s in self._symbols:
                sym_array.append(str(s.name))
            for b in self._mouse:
                button_array.append("left" if b == 1 else ("right" if b == 2 else "middle"))
            return "+".join(mod_array) + " - " + "+".join(sym_array) + " - " + "+".join(button_array)
        else:
            return "Empty"

    def __repr__(self):
        return self.to_string()


class CameraKeysClass(object):
    # store keys for camera interactions
    def __init__(self):
        self._orbit_key = None
        self._zoom_key = None
        self._pan_key = None

    def _get_union(self, k1, k2):
        def is_in_array(v, array):
            for w in array:
                if v == w:
                    return True
            return False

        symbols = []
        for k in k1.get_symbols():
            if not is_in_array(k, symbols):
                symbols.append(k)
        for k in k2.get_symbols():
            if not is_in_array(k, symbols):
                symbols.append(k)
        modifiers = []
        for k in k1.get_modifiers():
            if not is_in_array(k, modifiers):
                modifiers.append(k)
        for k in k2.get_modifiers():
            if not is_in_array(k, modifiers):
                modifiers.append(k)
        buttons = []
        for k in k1.get_mouse_buttons():
            if not is_in_array(k, buttons):
                buttons.append(k)
        for k in k2.get_mouse_buttons():
            if not is_in_array(k, buttons):
                buttons.append(k)
        return KeyClass(symbols, modifiers, buttons)

    def set_orbit_key(self, key):
        if key.get_is_correct():
            self._orbit_key = key

    def set_pan_key(self, key):
        if key.get_is_correct():
            self._pan_key = key

    def set_zoom_key(self, key):
        if key.get_is_correct():
            self._zoom_key = key

    def get_mode(self, key):  # 0 - does not math, 1 - orbit match, 2 - pan match, 3 - zoom match
        if self._orbit_key is not None and self._orbit_key.is_equal(key):
            return 1
        elif self._pan_key is not None and self._pan_key.is_equal(key):
            return 2
        elif self._zoom_key is not None and self._zoom_key.is_equal(key):
            return 3
        else:
            return 0

    def add_to_xml(self, root):
        ET.SubElement(root, "orbit", {"key": self._orbit_key.get_key_string(), "mouse": self._orbit_key.get_mouse_buttons_string()})
        ET.SubElement(root, "pan", {"key": self._pan_key.get_key_string(), "mouse": self._pan_key.get_mouse_buttons_string()})
        ET.SubElement(root, "zoom", {"key": self._zoom_key.get_key_string(), "mouse": self._zoom_key.get_mouse_buttons_string()})


class KeyController(object):  # controll behaivour of key pressing
    def __init__(self):
        # keys.SHIFT, keys.ALT, keys.CONTROL
        self._pressed_keys = set()  # the set of pressed keys. Store symbols.
        # self._pressed_buttons = set()  # mouse buttons. Store integers
        self._camera_keys = None
        self._camera_keys_init = False
        self._camera_event = None
        self._commands = []

    def _set_camera_keys(self, camera_data):
        self._camera_keys = CameraKeysClass()
        self._camera_keys.set_orbit_key(camera_data["orbit"])
        self._camera_keys.set_pan_key(camera_data["pan"])
        self._camera_keys.set_zoom_key(camera_data["zoom"])
        self._camera_keys_init = True

    def _form_key_from_xml(self, section):
        # read key and mouse strings
        key_str = ""
        if "key" in section.attrib.keys():
            key_str = section.attrib["key"]
        m_str = ""
        if "mouse" in section.attrib.keys():
            m_str = section.attrib["mouse"]
        (k, k_symbols, k_modifs) = self._form_key_from_key(key_str)
        m_buttons = []
        parts = m_str.split("+")
        if len(parts) > 0:
            for p in parts:
                if p == "Left":
                    m_buttons.append(1)
                elif p == "Right":
                    m_buttons.append(2)
                elif p == "Middle":
                    m_buttons.append(3)
        return KeyClass(k_symbols, k_modifs, m_buttons)

    def _form_key_from_key(self, key_str):
        # split by +
        parts = key_str.split("+")
        if len(parts) > 0:
            modifs = []
            symbols = []
            for p in parts:
                if p == "Shift":
                    modifs.append(keys.SHIFT)
                elif p == "Ctrl":
                    modifs.append(keys.CONTROL)
                elif p == "Alt":
                    modifs.append(keys.ALT)
                else:
                    if len(p) > 0:
                        symbols.append(keys.Key(p.lower()))
            return (KeyClass(symbols, modifs, []), symbols, modifs)
        else:
            return (KeyClass([], [], []), [], [])

    def _get_data_from_tree(self, root, cam_keys):
        _camera_keys = copy.deepcopy(cam_keys)
        _commands = {}
        cam_section = root.find("camera")
        if cam_section is not None:
            orbit = cam_section.find("orbit")
            pan = cam_section.find("pan")
            zoom = cam_section.find("zoom")
            if orbit is not None:
                _camera_keys["orbit"] = self._form_key_from_xml(orbit)
            if pan is not None:
                _camera_keys["pan"] = self._form_key_from_xml(pan)
            if zoom is not None:
                _camera_keys["zoom"] = self._form_key_from_xml(zoom)
        # next commands
        commands = root.findall("command")
        for c in commands:
            c_keys = c.attrib.keys()
            if "key" in c_keys and "label" in c_keys and "name" in c_keys:
                command_data = {"name": c.attrib["name"], "key": self._form_key_from_key(c.attrib["key"])[0], "label": c.attrib["label"]}
                _commands[c.attrib["name"]] = command_data
        return (_camera_keys, _commands)

    def init_keys(self, file_path=None):  # called from host application in __init__ section
        # if file_path is valid we should read the data from xml and use it
        file_exist = False
        camera_data = {}  # set default camera keys
        camera_data["orbit"] = KeyClass([], [], [2])
        camera_data["pan"] = KeyClass([], [], [1])
        camera_data["zoom"] = KeyClass([], [], [3])
        commands_data = {}
        if os.path.isfile(file_path):
            file_exist = True
            tree = ET.parse(file_path)
            (camera_data, commands_data) = self._get_data_from_tree(tree.getroot(), camera_data)
        self._set_camera_keys(camera_data)  # set camera keys
        # next for build-in commands
        fit_camera = commands_data["fit_camera"] if "fit_camera" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="fit_camera", command_label=fit_camera["label"] if fit_camera is not None else "Fit Camera View", key=fit_camera["key"] if fit_camera is not None else KeyClass([keys.Key("a")], [], [])))
        clear_scene = commands_data["clear_scene"] if "clear_scene" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="clear_scene", command_label=clear_scene["label"] if clear_scene is not None else "Clear Scene", key=clear_scene["key"] if clear_scene is not None else KeyClass([keys.Key("c")], [keys.CONTROL], [])))
        open = commands_data["open"] if "open" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="open", command_label=open["label"] if open is not None else "Open...", key=open["key"] if open is not None else KeyClass([keys.Key("o")], [keys.CONTROL], [])))
        quit = commands_data["quit"] if "quit" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="quit", command_label=quit["label"] if quit is not None else "Quit", key=quit["key"] if quit is not None else KeyClass([keys.Key("q")], [keys.CONTROL], [])))
        edit_layout = commands_data["edit_layout"] if "edit_layout" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="edit_layout", command_label=edit_layout["label"] if edit_layout is not None else "Enable/Disable Layout Edit", key=edit_layout["key"] if edit_layout is not None else KeyClass([keys.Key("e")], [keys.CONTROL], [])))
        show_poroperties = commands_data["show_poroperties"] if "show_poroperties" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="show_poroperties", command_label=show_poroperties["label"] if show_poroperties is not None else "Properties...", key=show_poroperties["key"] if show_poroperties is not None else KeyClass([keys.Key("p")], [], [])))
        show_render_settings = commands_data["show_render_settings"] if "show_render_settings" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="show_render_settings", command_label=show_render_settings["label"] if show_render_settings is not None else "Render Settings...", key=show_render_settings["key"] if show_render_settings is not None else KeyClass([keys.Key("r")], [], [])))
        show_style_settings = commands_data["show_style_settings"] if "show_style_settings" in commands_data.keys() else None
        self._commands.append(CommandClass(command_name="show_style_settings", command_label=show_style_settings["label"] if show_style_settings is not None else "Style Settings...", key=show_style_settings["key"] if show_style_settings is not None else KeyClass([keys.Key("v")], [], [])))
        if file_exist is False:  # save xml with data
            self._save_to_xml(file_path)

    def indent(self, elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _save_to_xml(self, file_path):
        root = ET.Element("shortcuts")
        for c in self._commands:
            c.add_to_xml(root)
        # next camera section
        cam_section = ET.SubElement(root, "camera")
        self._camera_keys.add_to_xml(cam_section)
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_path)

    def add_command(self, command_name, command_label, command_key, command_function):
        is_exist = False
        for c in self._commands:
            if c.get_name() == command_name:
                is_exist = True
        if is_exist is False:
            new_command = CommandClass(command_name=command_name, command_label=command_label, key=command_key)
            new_command.set_function(command_function)
            self._commands.append(new_command)

    def get_command_key(self, command_name):
        # iterate throw commands and try to find it
        for c in self._commands:
            if c.get_name() == command_name:
                return c.get_key()
        return None

    def get_command_label(self, command_name):
        for c in self._commands:
            if c.get_name() == command_name:
                return c.get_label()
        return None

    def get_camera_keys(self):
        if self._camera_keys_init:
            return self._camera_keys
        else:
            return None

    def add_function(self, command, function):
        '''command should be inner name of the command, not it label'''
        for c in self._commands:
            if c.get_name() == command:
                c.set_function(function)

    def set_camera_event(self, camera_event):
        self._camera_event = camera_event

    def check_event(self):  # return True if something happens, False if there is no valid command
        key_event = self._get_key_from_event()
        # is_camera_on = self._camera_event(key_event)
        self._camera_event(key_event)  # transfer to camera data about pressed keys
        for c in self._commands:
            if c.get_key().is_equal(key_event):
                # apply command
                c.apply()
                return True
        return False
        '''if is_camera_on is False:
            # check commands
            for c in self._commands:
                if c.get_key().is_equal(key_event):
                    # apply command
                    c.apply()
                    return True
            return False
        else:
            return True'''

    @property
    def pressed_keys(self):
        return self._pressed_keys

    def clear(self):
        self._pressed_keys.clear()
        self._pressed_keys = set()

    def _get_key_from_event(self):  # form KeyClass from event data
        keys_list = []
        modifs_list = []
        for k in list(self._pressed_keys):
            if k == "Shift" or k == "Control" or k == "Alt":
                modifs_list.append(keys.Key(k))
            else:
                keys_list.append(keys.Key(k))
        return KeyClass(keys_list, modifs_list, [])
