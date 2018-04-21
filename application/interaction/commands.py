import xml.etree.cElementTree as ET


class CommandClass(object):
    def __init__(self, command_name="", command_label="", key=None):
        self._command_name = command_name
        self._command_label = command_name if len(command_label) == 0 else command_label
        self._command_key = key
        self._function = None  # set here function for command

    def get_name(self):
        return self._command_name

    def get_label(self):
        return self._command_label

    def get_key(self):
        return self._command_key

    def set_function(self, function):
        self._function = function

    def apply(self):
        if self._function is not None:
            self._function()
        else:
            print("Functon for the command " + self._command_name + " is not defined")

    def add_to_xml(self, root):
        ET.SubElement(root, "command", {"name": self._command_name,
                                        "label": self._command_label,
                                        "key": self._command_key.get_key_string()})
