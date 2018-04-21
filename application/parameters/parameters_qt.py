import sys
import re
import xml.etree.cElementTree as ET
from PyQt4 import QtGui, QtCore


class ParameterCombobox(QtGui.QWidget):
    def __init__(self, parent=None, value=0, items=[], name="", label_text="", label_width=64, height=22, change_callback=None):
        QtGui.QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self.name = name
        self.label_text = label_text
        self.value = value
        self._items = [item for item in items]
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QtGui.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)

        self.value_combobox = QtGui.QComboBox()
        self.value_combobox.addItems(items)
        self.value_combobox.setCurrentIndex(self.value)
        self.value_combobox.currentIndexChanged.connect(self.selection_changed)
        self.value_combobox.setFixedHeight(height)
        self.value_combobox.setMinimumWidth(24)

        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_combobox)
        self.setLayout(self.layout)

    def selection_changed(self, index):
        self.value = index
        self.value_change()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "value": str(self.value),
                       "items": str(self._items),
                       "label": self.label_text}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=(self.value, self._items))


class ParameterColor(QtGui.QWidget):
    def __init__(self, parent=None, value=QtGui.QColor(128, 128, 128, 255), name="", label_text="", label_width=64, height=22, change_callback=None):
        QtGui.QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self.name = name
        self.label_text = label_text
        self.value = value
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None
        # self._color_width = 32
        self._color_height = 16
        self._label_to_color_gap = 10
        self._right_margin = 10
        self._color_width = None

        # calculate color rectangle zone
        self._color_rect_min_x = label_width + self._label_to_color_gap
        self._color_rect_min_y = None

        self.label = QtGui.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)

        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        size = self.size()  # the size of allowed are for the widget
        self._color_rect_min_y = (size.height() - self._color_height) // 2
        self._color_width = size.width() - self._color_rect_min_x - self._right_margin
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.value)

        painter.drawRect(self._color_rect_min_x, self._color_rect_min_y, self._color_width, self._color_height)
        painter.end()

    def mousePressEvent(self, event):
        pos = event.pos()
        # check is we click to the color area
        x = pos.x()
        y = pos.y()
        if self._color_rect_min_y is not None and self._color_width is not None:
            if x > self._color_rect_min_x and x < self._color_rect_min_x + self._color_width and y > self._color_rect_min_y and y < self._color_rect_min_y + self._color_height:
                new_color_id, new_color_correct = QtGui.QColorDialog.getRgba(self.value.rgba())
                if new_color_correct:
                    self.value = QtGui.QColor()
                    self.value.setRgba(new_color_id)
                    self.value_change()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "value": str((self.value.red(), self.value.green(), self.value.blue(), self.value.alpha())),
                       "label": self.label_text}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)


class ParameterBool(QtGui.QWidget):
    def __init__(self, parent=None, value=False, name="", label_text="", label_width=64, height=22, change_callback=None):
        QtGui.QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self.name = name
        self.label_text = label_text
        self.value = value
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QtGui.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)
        self.value_checkbox = QtGui.QCheckBox()
        self.value_checkbox.setChecked(self.value)
        self.value_checkbox.setFixedHeight(height)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        layout.addWidget(self.label)
        layout.addWidget(self.value_checkbox, QtCore.Qt.AlignRight)
        self.setLayout(layout)

        self.value_checkbox.stateChanged.connect(self.stateChanged)

    def stateChanged(self, value):
        if value == 0:
            self.value = False
        else:
            self.value = True
        self.value_change()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "value": str(self.value),
                       "label": self.label_text}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)


class ParameterString(QtGui.QWidget):
    def __init__(self, parent=None, value="", name="", label_text="", label_width=64, height=22, change_callback=None):
        QtGui.QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self.name = name
        self.label_text = label_text
        self.value = value
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QtGui.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)
        self.value_textbox = QtGui.QLineEdit()
        self.value_textbox.setFixedHeight(height)
        self._update_value_label()
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        layout.addWidget(self.label)
        layout.addWidget(self.value_textbox)
        self.setLayout(layout)

        self.value_textbox.returnPressed.connect(self.textbox_enter)
        self.value_textbox.editingFinished.connect(self.textbox_enter)

    def _update_value_label(self):
        self.value_textbox.setText(self.value)

    def textbox_enter(self):
        text = self.value_textbox.text()
        self.value = text
        self._update_value_label()
        self.value_textbox.clearFocus()
        self.value_change()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "value": str(self.value),
                       "label": self.label_text}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)


class ParameterInteger(QtGui.QWidget):
    def check_int(self, s):
        if s[0] in ("-", "+"):
            return s[1:].isdigit()
        return s.isdigit()

    def clamp(self, value, min_value, max_value):
        if value < min_value:
            return min_value
        elif value > max_value:
            return max_value
        else:
            return value

    def __init__(self, parent=None, value=0, name="", label_text="", min_value=None, max_value=None, label_width=64, height=22, min_visible=0, max_visible=10, change_callback=None):
        QtGui.QWidget.__init__(self, parent)

        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self.name = name
        self.label_text = label_text
        self.min_value_raw = min_value
        self.max_value_raw = max_value
        self.min_value = min_value if min_value is not None else -sys.maxsize
        self.max_value = max_value if max_value is not None else sys.maxsize
        self.value = self.clamp(value, self.min_value, self.max_value)
        self.min_visible = max(self.min_value, min(min_visible, self.value))
        self.max_visible = min(self.max_value, max(max_visible, self.value))
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QtGui.QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)
        self.value_textbox = QtGui.QLineEdit()
        self.value_textbox.setFixedWidth(52)
        self.value_textbox.setFixedHeight(height)
        self._update_value_label()
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setFixedHeight(height)
        self._update_visible_interval()
        self.slider.setValue(value)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        layout.addWidget(self.label)
        layout.addWidget(self.value_textbox)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.slider_valueChanged)
        self.value_textbox.returnPressed.connect(self.textbox_enter)
        self.value_textbox.editingFinished.connect(self.textbox_enter)
        self.slider.sliderReleased.connect(self.slider_sliderReleased)

    def _update_visible_interval(self):
        self.slider.setRange(self.min_visible, self.max_visible)

    def _update_value_label(self):
        self.value_textbox.setText(str(self.value))

    def slider_valueChanged(self, value):
        self.value = value
        self._update_value_label()
        self.value_change()

    def slider_sliderReleased(self):
        self.try_change_visible(self.value)
        self.slider.setValue(self.value)

    def try_change_visible(self, new_value):
        delta = self.max_visible - self.min_visible
        # increase visible interval if new value out of the current
        if new_value <= self.min_visible:
            self.min_visible = max(self.min_value, new_value - delta)
        if new_value >= self.max_visible:
            self.max_visible = min(self.max_value, new_value + delta)
        self._update_visible_interval()

    def textbox_enter(self):
        text = self.value_textbox.text()
        # check is this text is integer
        if self.check_int(text):
            new_value = int(text)
            # clamp value
            if new_value < self.min_value:
                new_value = self.min_value
            if new_value > self.max_value:
                new_value = self.max_value
            self.try_change_visible(new_value)
            self.slider.setValue(new_value)
            self._update_value_label()
            self.value_change()
        else:
            self._update_value_label()
        self.value_textbox.clearFocus()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "min_value": str(self.min_value_raw),
                       "max_value": str(self.max_value_raw),
                       "value": str(self.value),
                       "label": self.label_text,
                       "min_visible": str(self.min_visible),
                       "max_visible": str(self.max_visible)}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)


class ParameterFloat(QtGui.QWidget):
    def is_float(self, str):
        return True if self._float_regexp(str) else False

    def clamp(self, value, min_value, max_value):
        if value < min_value:
            return min_value
        elif value > max_value:
            return max_value
        else:
            return value

    def __init__(self, parent=None, value=0.0, name="", label_text="", min_value=None, max_value=None, label_width=64, height=22, min_visible=0.0, max_visible=10.0, change_callback=None):
        QtGui.QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 2
        self.HORIZONTAL_MARGIN = 6

        self._slider_steps = 1024
        self._float_regexp = re.compile(r"^[-+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?$").match
        self._int_vis_min = None
        self._int_vis_max = None
        self._remember_to_fix = False

        self.name = name
        self.min_value_raw = min_value
        self.max_value_raw = max_value
        self.label_text = label_text
        self.min_value = min_value if min_value is not None else -float("inf")
        self.max_value = max_value if max_value is not None else float("inf")
        self.value = self.clamp(value, self.min_value, self.max_value)
        self.min_visible = max(self.min_value, min(min_visible, self.value))
        self.max_visible = min(self.max_value, max(max_visible, self.value))
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QtGui.QLabel(self.label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)
        self.value_textbox = QtGui.QLineEdit()
        self.value_textbox.setFixedWidth(52)
        self.value_textbox.setFixedHeight(height)
        self._update_value_label()
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setFixedHeight(height)
        self._update_visible_interval()
        self._set_slider_value()
        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.value_textbox)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.slider_valueChanged)
        self.value_textbox.returnPressed.connect(self.textbox_enter)
        self.value_textbox.editingFinished.connect(self.textbox_enter)
        self.slider.sliderReleased.connect(self.slider_sliderReleased)

    def _update_visible_interval(self):
        step = (self.max_visible - self.min_visible) / self._slider_steps
        self._int_vis_min = int(self.min_visible / step)
        self._int_vis_max = int(self.max_visible / step)
        self._remember_to_fix = True
        self.slider.setRange(self._int_vis_min, self._int_vis_max)

    def _update_value_label(self):
        self.value_textbox.setText(str(round(self.value, 4)))

    def _set_slider_value(self):
        self._remember_to_fix = True
        step = (self.max_visible - self.min_visible) / self._slider_steps
        self.slider.setValue(self.value / step)

    def slider_valueChanged(self, value):
        step = (self.max_visible - self.min_visible) / self._slider_steps
        shift = value - self._int_vis_min
        if self._remember_to_fix is False:
            self.value = self.min_visible + shift * step
        self._update_value_label()
        self.value_change()
        self._remember_to_fix = False

    def slider_sliderReleased(self):
        self.try_change_visible(self.value)
        self._set_slider_value()

    def try_change_visible(self, new_value):
        delta = self.max_visible - self.min_visible
        # increase visible interval if new value out of the current
        if new_value <= self.min_visible:
            self.min_visible = max(self.min_value, new_value - delta)
        if new_value >= self.max_visible:
            self.max_visible = min(self.max_value, new_value + delta)
        self._update_visible_interval()

    def textbox_enter(self):
        text = self.value_textbox.text()
        # check is this text is integer
        if self.is_float(text):
            new_value = float(text)
            # clamp value
            if new_value < self.min_value:
                new_value = self.min_value
            if new_value > self.max_value:
                new_value = self.max_value
            self.try_change_visible(new_value)
            self.value = new_value
            self._set_slider_value()
            self._update_value_label()
            self.value_change()
        else:
            self._update_value_label()
        self.value_textbox.clearFocus()

    def add_to_xml(self, root):
        params_dict = {"name": self.name,
                       "min_value": str(self.min_value_raw),
                       "max_value": str(self.max_value_raw),
                       "value": str(self.value),
                       "label": self.label_text,
                       "min_visible": str(self.min_visible),
                       "max_visible": str(self.max_visible)}
        ET.SubElement(root, "parameter", params_dict)

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)
