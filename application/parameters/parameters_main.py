import xml.etree.cElementTree as ET
from PyQt4 import QtGui, QtCore

from parameters.parameters_qt import ParameterCombobox, ParameterColor, ParameterBool, ParameterString, ParameterInteger, ParameterFloat


class ParametersSet(object):
    '''Contains set of parameters. host is a QWidget for drawing parameters widget.
    This class contains data management for parameters.'''
    def __init__(self, name="", host=None, label_width=64, change_callback=None):
        self._name = name
        self._parameters = []  # each parameter is a tripple: (name, value, type_str)
        self._widgets = []  # in the same order as in _parameters
        self._name_to_index = {}  # this dictionary used for finding parameter by it name. Key is a name, value is a pair (p_index, w_index)
        self._group_layouts = []
        self._group_name_to_index = {}
        self._widget_index_to_group = {}  # map from widget index to it group name in the form w_index: group_name. None if not group
        self._label_width = label_width
        self._change_callback = change_callback

        # set basic ui
        self.layout = QtGui.QVBoxLayout()
        # self.layout.setMargin(0)  # this should be done by css
        self.layout.setSpacing(10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        host.setLayout(self.layout)

    def set_change_callback(self, change_callback):
        self._change_callback = change_callback

    def add_group(self, group_name="", group_label=""):
        if group_name not in self._group_name_to_index.keys():
            new_group = QtGui.QGroupBox(group_label)
            new_layout = QtGui.QVBoxLayout()
            new_group.setLayout(new_layout)
            self._group_layouts.append(new_layout)
            self._group_name_to_index[group_name] = len(self._group_layouts) - 1
            self.layout.addWidget(new_group)

    def add_parameter(self, group=None, name=None, visual_name="", value=None, type=None, min_limit=None, max_limit=None, min_visible=None, max_visible=None):
        '''type=integer, float, string, boolean, color, combobox. visual_name is not a name of the parameter, but it label'''
        new_widget = None
        if name is not None and name not in self._name_to_index.keys():
            if type == "integer":
                new_widget = ParameterInteger(name=name,
                                              label_width=self._label_width,
                                              label_text=visual_name,
                                              value=value if value is not None else 0,
                                              min_visible=min_visible if min_visible is not None else 0,
                                              max_visible=max_visible if max_visible is not None else 10,
                                              min_value=min_limit,
                                              max_value=max_limit,
                                              change_callback=self._parameter_change)
                new_parameter = (name, value, type)
            elif type == "float":
                new_widget = ParameterFloat(name=name,
                                            label_width=self._label_width,
                                            label_text=visual_name,
                                            value=value if value is not None else 0.0,
                                            min_visible=min_visible if min_visible is not None else 0.0,
                                            max_visible=max_visible if max_visible is not None else 1.0,
                                            min_value=min_limit,
                                            max_value=max_limit,
                                            change_callback=self._parameter_change)
                new_parameter = (name, value, type)
            elif type == "string":
                new_widget = ParameterString(name=name,
                                             label_width=self._label_width,
                                             label_text=visual_name,
                                             value=value if value is not None else "",
                                             change_callback=self._parameter_change)
                new_parameter = (name, value, type)
            elif type == "boolean":
                new_widget = ParameterBool(name=name,
                                           label_width=self._label_width,
                                           label_text=visual_name,
                                           value=value if value is not None else False,
                                           change_callback=self._parameter_change)
                new_parameter = (name, value, type)
            elif type == "color":
                color = QtGui.QColor(128, 128, 128, 255)
                if value is not None and len(value) >= 3:
                    color = QtGui.QColor(value[0], value[1], value[2], 255) if len(value) == 3 else QtGui.QColor(value[0], value[1], value[2], value[3])
                new_widget = ParameterColor(name=name,
                                            label_width=self._label_width,
                                            label_text=visual_name,
                                            value=color,
                                            change_callback=self._parameter_change)
                new_parameter = (name, value, type)
            elif type == "combobox":
                new_widget = ParameterCombobox(name=name,
                                               label_width=self._label_width,
                                               label_text=visual_name,
                                               value=value[0] if value is not None else 0,
                                               items=value[1] if value is not None else [],
                                               change_callback=self._parameter_change)
                new_parameter = (name, value, type)
        if new_widget is not None:
            self._parameters.append(new_parameter)
            self._widgets.append(new_widget)
            self._name_to_index[name] = (len(self._parameters) - 1, len(self._widgets) - 1)
            # add widget
            if group is not None and group in self._group_name_to_index.keys():
                self._group_layouts[self._group_name_to_index[group]].addWidget(new_widget)
                self._widget_index_to_group[len(self._widgets) - 1] = group
            else:
                self._widget_index_to_group[len(self._widgets) - 1] = None
                self.layout.addWidget(new_widget)

    def get_value(self, param_name):
        if param_name in self._name_to_index.keys():
            return self._parameters[self._name_to_index[param_name]][1]
        else:
            return None

    def get_type(self, param_name):
        if param_name in self._name_to_index.keys():
            return self._parameters[self._name_to_index[param_name]][2]
        else:
            return None

    def _parameter_change(self, param_name, param_value):
        p_index = self._name_to_index[param_name][0]
        p_type = self._parameters[p_index][2]
        p_value = param_value
        p_old = self._parameters[p_index][1]
        if p_type == "color":
            p_value = (param_value.red(), param_value.green(), param_value.blue(), param_value.alpha())
        # set value
        self._parameters[p_index] = (param_name, p_value, p_type)
        if self._change_callback is not None:
            self._change_callback(params=self._parameters, type=p_type, changed_name=param_name, new_value=p_value, old_value=p_old)

    def get_parameters(self):
        return self._parameters

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

    def save_xml(self, file_path):
        root = ET.Element("parameters_set", {"name": self._name, "label_width": str(self._label_width)})
        # iterate throw groups
        saved_params = []
        for group_name in self._group_name_to_index.keys():
            group = ET.SubElement(root, "group", {"name": group_name})
            # next throw all parameters, and check is it on this group
            for param in self._parameters:
                p_name = param[0]
                (p_index, w_index) = self._name_to_index[p_name]
                if self._widget_index_to_group[w_index] is not None and self._widget_index_to_group[w_index] == group_name and p_index not in saved_params:
                    saved_params.append(p_index)
                    widget = self._widgets[w_index]
                    widget.add_to_xml(group)
        # finally find params without group
        for param in self._parameters:
            p_name = param[0]
            (p_index, w_index) = self._name_to_index[p_name]
            if p_index not in saved_params:
                saved_params.append(p_index)
                widget = self._widgets[w_index]
                widget.add_to_xml(root)
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_path)
