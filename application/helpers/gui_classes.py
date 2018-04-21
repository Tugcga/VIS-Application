import os
import xml.etree.cElementTree as ET
from PyQt4 import QtGui


class LayoutData(object):
    def __init__(self, file_path=None):
        self._data = {}  # store data as dictionary {"doc_name": {data for this doc}}
        if os.path.isfile(file_path):
            # read data from xml
            tree = ET.parse(file_path)
            root = tree.getroot()
            for child in root:
                doc_name = child.tag
                # get subsection of the doc settings
                doc_params = {}
                for d_child in child:
                    param_name = d_child.tag
                    param_value_text = d_child.attrib["value"] if "value" in d_child.attrib.keys() else None
                    if param_value_text is not None:
                        doc_params[param_name] = eval(param_value_text)
                        # doc_params[param_name] = True if param_value_text == "True" else (False if param_value_text == "False" else (eval(param_value_text)))
                self._data[doc_name] = doc_params

    def get_data(self, name=""):
        if name in self._data.keys():
            return self._data[name]
        else:
            return None

    def _form_data_for_doc(self, doc, app, width=None, height=None, tabbed_list=None):
        to_return = {}
        to_return["is_visible"] = doc.isVisible()
        to_return["is_floating"] = doc.isFloating()
        to_return["area_index"] = app.dockWidgetArea(doc) if doc.isFloating() is False else 0  # 0 for floating window
        # save names of tabbed docs in the same place
        if tabbed_list is not None and len(tabbed_list) > 0:
            to_return["tabify"] = tabbed_list
        to_return["width"] = width  # doc.size().width()
        to_return["height"] = height  # doc.size().height() - 22  # MAGIC for fix incerasing of the window size after relaunch of the application
        position = doc.pos()
        to_return["position_x"] = position.x()
        to_return["position_y"] = position.y()
        return to_return

    def _form_data_for_main_window(self, app):
        main_size = app.size()
        to_return = {}
        to_return["width"] = main_size.width()
        to_return["height"] = main_size.height()
        to_return["is_maximized"] = app.isMaximized()
        main_pos = app.pos()
        to_return["position_x"] = main_pos.x()
        to_return["position_y"] = main_pos.y()
        return to_return

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

    def _get_name(self, doc_list, doc_to_index, widget):
        for doc_name in doc_to_index.keys():
            index = doc_to_index[doc_name]
            if doc_list[index][0] == widget:
                return doc_name
        return None

    def save_xml(self, file_path, doc_list, doc_to_index, app):
        # at first set data to the self._data
        for doc_name in doc_to_index.keys():
            doc = doc_list[doc_to_index[doc_name]][0]
            doc_width = doc_list[doc_to_index[doc_name]][3]
            doc_height = doc_list[doc_to_index[doc_name]][4]
            if doc_name != "main_window":
                tabbed_widgets = app.tabifiedDockWidgets(doc)
                tabbed_list = []
                for w in tabbed_widgets:
                    w_name = self._get_name(doc_list, doc_to_index, w)
                    if w_name is not None:
                        tabbed_list.append(w_name)
                self._data[doc_name] = self._form_data_for_doc(doc, app, width=doc_width, height=doc_height, tabbed_list=tabbed_list)
        self._data["main_window"] = self._form_data_for_main_window(app)
        # next save to xml
        root = ET.Element("layout")
        for d_key in self._data.keys():
            data = self._data[d_key]
            doc_section = ET.SubElement(root, d_key)
            for k in data.keys():
                ET.SubElement(doc_section, k, {"value": str(data[k])})
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(file_path)


class StylesClass(object):
    def __init__(self):
        self._factory_names = QtGui.QStyleFactory.keys()
        self._original_palette = QtGui.QApplication.palette()
        self._qss_names = []
        self._qss_paths = []
        qss_extensions = [".qss"]
        # find *.qss files
        root_path = os.path.split(os.path.abspath(__file__))[0] + "..\\..\\..\\"
        for item in os.walk(root_path):
            folder = item[0]
            files = item[2]
            if len(files) > 0:
                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext in qss_extensions:
                        file_path = folder + "\\" + file
                        self._qss_names.append(os.path.splitext(file)[0])
                        self._qss_paths.append(file_path)
        self._all_names = [v for v in self._factory_names] + [v for v in self._qss_names]

    def get_names(self):
        return self._all_names

    def get_original_palette(self):
        return self._original_palette

    def get_current_style_name(self):
        return QtGui.QApplication.style().objectName()

    def get_current_style_index(self):
        cur_name = self.get_current_style_name()
        for i in range(len(self._factory_names)):
            if cur_name == self._factory_names[i].lower():
                return i
        return -1

    def is_qss(self, name):
        if name in self._qss_names:
            return True
        else:
            return False

    def get_qss_path(self, name):
        for i in range(len(self._qss_names)):
            if self._qss_names[i] == name:
                return self._qss_paths[i]
        return None

    def is_factory(self, name):
        if name in self._factory_names:
            return True
        else:
            return False
