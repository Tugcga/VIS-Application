import os
import xml.etree.cElementTree as ET
from parameters.parameters_main import ParametersSet
from helpers.gui_classes import StylesClass


def get_data_path(data_filename=None):
    if data_filename is not None:
        return os.path.split(__file__)[0] + "\\..\\data\\" + data_filename
    else:
        return None


def get_image_path(data_filename=None):
    if data_filename is not None:
        return os.path.split(__file__)[0] + "\\..\\data\\images\\" + data_filename
    else:
        return None


def from_tree_to_data(tree):
    '''Returns the data from xml-file as a pair (groups, parameters). Here groups are all groups on the parameters set.'''
    groups = []
    parameters = []  # each parameter in the form (group, dict). group may be None
    tree_groups = tree.findall("group")
    for g in tree_groups:
        if "name" in g.attrib.keys():
            g_name = g.attrib["name"]
            groups.append(g_name)
            # add parameters
            group_params = g.findall("parameter")
            for p in group_params:
                parameters.append((g_name, p.attrib))
    tree_params = tree.findall("parameter")  # params without group
    for p in tree_params:
        parameters.append((None, p.attrib))
    return (groups, parameters)


def get_value_from_data(data, param_name, keys, alternatives):
    to_return = [str(alternatives[i]) for i in range(len(alternatives))]
    for p in data:
        p_dict = p[1]
        if "name" in p_dict.keys() and p_dict["name"] == param_name:
            k_index = 0
            for k in keys:
                if k in p_dict.keys():
                    to_return[k_index] = p_dict[k]
                k_index += 1
            return to_return
    return to_return


def read_render_settings_from_file(file_path, host_widget):
    set_name = "Render Settings"
    label_width = 92
    file_exist = False
    parameters = []
    if os.path.isfile(file_path):
        file_exist = True
        tree = ET.parse(file_path)
        (groups, parameters) = from_tree_to_data(tree)
        root = tree.getroot()
        set_name = root.attrib["name"] if "name" in root.attrib.keys() else "Render Settings"
        label_width = int(root.attrib["label_width"]) if "label_width" in root.attrib.keys() else 92
    params = ParametersSet(host=host_widget, name=set_name, label_width=label_width)
    params.add_group("show_items", "Show Items")
    params.add_group("polygons_settings", "Polygons Settings")
    params.add_group("edges_settings", "Edges Settings")
    params.add_group("points_settings", "Points Settings")
    params.add_group("light", "Light")
    # read parameters
    show_faces = get_value_from_data(parameters, "show_faces", ["value"], [True])
    show_edges = get_value_from_data(parameters, "show_edges", ["value"], [False])
    show_points = get_value_from_data(parameters, "show_points", ["value"], [False])

    poly_color = get_value_from_data(parameters, "poly_color", ["value"], [(200, 200, 200, 255)])
    edge_color = get_value_from_data(parameters, "edge_color", ["value"], [(255, 210, 0, 255)])
    point_color = get_value_from_data(parameters, "point_color", ["value"], [(0, 0, 255, 255)])

    # light_intensity = get_value_from_data(parameters, "light_intensity", ["value", "min_limit", "max_visible"], [1.0, 0.0, 2.0])
    # light_color = get_value_from_data(parameters, "light_color", ["value"], [(255, 255, 255, 255)])
    ambient_color = get_value_from_data(parameters, "ambient_color", ["value"], [(25, 25, 25, 255)])
    light_shift_x = get_value_from_data(parameters, "light_shift_x", ["value", "min_visible", "max_visible"], [0.0, -10.0, 10.0])
    light_shift_y = get_value_from_data(parameters, "light_shift_y", ["value", "min_visible", "max_visible"], [0.0, -10.0, 10.0])

    point_size = get_value_from_data(parameters, "point_size", ["value", "min_limit", "max_visible"], [5.0, 0.0, 10.0])
    line_width = get_value_from_data(parameters, "line_width", ["value", "min_limit", "max_visible"], [1, 1, 4])
    shiness = get_value_from_data(parameters, "shiness", ["value", "min_limit", "max_visible"], [0.005, 0.0, 0.1])

    # set parameters to widgets
    params.add_parameter(group="show_items", name="show_faces", visual_name="Show Polygons", value=eval(show_faces[0]), type="boolean")
    params.add_parameter(group="show_items", name="show_edges", visual_name="Show Edges", value=eval(show_edges[0]), type="boolean")
    params.add_parameter(group="show_items", name="show_points", visual_name="Show Points", value=eval(show_points[0]), type="boolean")

    params.add_parameter(group="polygons_settings", name="poly_color", visual_name="Color", value=eval(poly_color[0]), type="color")
    params.add_parameter(group="polygons_settings", name="shiness", visual_name="Shiness", value=eval(shiness[0]), type="float", min_limit=eval(shiness[1]), max_visible=eval(shiness[2]))

    params.add_parameter(group="edges_settings", name="edge_color", visual_name="Color", value=eval(edge_color[0]), type="color")
    params.add_parameter(group="edges_settings", name="line_width", visual_name="Width", value=eval(line_width[0]), type="integer", min_limit=eval(line_width[1]), max_visible=eval(line_width[2]))
    params.add_parameter(group="points_settings", name="point_color", visual_name="Color", value=eval(point_color[0]), type="color")
    params.add_parameter(group="points_settings", name="point_size", visual_name="Point Size", value=eval(point_size[0]), type="float", min_limit=eval(point_size[1]), max_visible=eval(point_size[2]))

    # params.add_parameter(group="light", name="light_color", visual_name="Light Color", value=eval(light_color[0]), type="color")
    # params.add_parameter(group="light", name="light_intensity", visual_name="Light Intensity", value=eval(light_intensity[0]), type="float", min_limit=eval(light_intensity[1]), max_visible=eval(light_intensity[2]))
    params.add_parameter(group="light", name="ambient_color", visual_name="Ambient Color", value=eval(ambient_color[0]), type="color")
    params.add_parameter(group="light", name="light_shift_x", visual_name="Horizontal Shift", value=eval(light_shift_x[0]), type="float", min_visible=eval(light_shift_x[1]), max_visible=eval(light_shift_x[2]))
    params.add_parameter(group="light", name="light_shift_y", visual_name="Vertical Shift", value=eval(light_shift_y[0]), type="float", min_visible=eval(light_shift_y[1]), max_visible=eval(light_shift_y[2]))

    if file_exist is False:
        params.save_xml(file_path)
    return params


def read_scene_properties_from_file(file_path, host_widget):
    set_name = "Scene Properties"
    label_width = 92
    file_exist = False
    parameters = []
    if os.path.isfile(file_path):
        file_exist = True
        tree = ET.parse(file_path)
        (groups, parameters) = from_tree_to_data(tree)
        root = tree.getroot()
        set_name = root.attrib["name"] if "name" in root.attrib.keys() else "Scene Properties"
        label_width = int(root.attrib["label_width"]) if "label_width" in root.attrib.keys() else 92
    prop_params = ParametersSet(host=host_widget, name=set_name, label_width=label_width)
    prop_params.add_group("scene", "Scene")
    up_axis = get_value_from_data(parameters, "up_axis", ["value", "items", "min_limit", "max_limit"], [2, ["X", "Y", "Z"], 0, 2])
    prop_params.add_parameter(group="scene", name="up_axis", visual_name="Up Axis", value=(eval(up_axis[0]), eval(up_axis[1])), type="combobox", min_limit=eval(up_axis[2]), max_limit=eval(up_axis[3]))
    scale = get_value_from_data(parameters, "scale", ["value", "min_limit", "min_visible", "max_visible"], [1.0, 0.0, 0.5, 2.0])
    prop_params.add_parameter(group="scene", name="scale", visual_name="Scale", value=eval(scale[0]), type="float", min_limit=eval(scale[1]), min_visible=eval(scale[2]), max_visible=eval(scale[3]))
    center = get_value_from_data(parameters, "center", ["value"], [True])
    prop_params.add_parameter(group="scene", name="center", visual_name="Centering", value=eval(center[0]), type="boolean")
    camera_fov = get_value_from_data(parameters, "camera_fov", ["value", "min_limit", "max_limit", "min_visible", "max_visible"], [60.0, 0.0, 179.99, 30.0, 75.0])
    prop_params.add_parameter(group="scene", name="camera_fov", visual_name="Camera FOV", value=eval(camera_fov[0]), type="float", min_limit=eval(camera_fov[1]), max_limit=eval(camera_fov[2]), min_visible=eval(camera_fov[3]), max_visible=eval(camera_fov[4]))

    prop_params.add_group("background", "Background")
    data_bg = get_value_from_data(parameters, "bg_color", ["value"], [(34, 34, 34, 255)])
    prop_params.add_parameter(group="background", name="bg_color", visual_name="Background Color", value=eval(data_bg[0]), type="color")
    prop_params.add_group("axis_settings", "Axis Settings")
    data_show_axis = get_value_from_data(parameters, "show_axis", ["value"], [True])
    prop_params.add_parameter(group="axis_settings", name="show_axis", visual_name="Show Axis", value=eval(data_show_axis[0]), type="boolean")
    data_axis_corner = get_value_from_data(parameters, "axis_corner", ["value", "items", "min_limit", "max_limit"], [1, ['Left-Top', 'Left_Bottom', 'Right-Bottom', 'Right-Top'], 0, 3])
    prop_params.add_parameter(group="axis_settings", name="axis_corner", visual_name="Axis Corner", value=(eval(data_axis_corner[0]), eval(data_axis_corner[1])), type="combobox", min_limit=eval(data_axis_corner[2]), max_limit=eval(data_axis_corner[3]))

    data_axis_size = get_value_from_data(parameters, "axis_size", ["value", "min_limit", "max_visible"], [50.0, 0.1, 128.0])
    prop_params.add_parameter(group="axis_settings", name="axis_size", visual_name="Axis Size", value=eval(data_axis_size[0]), type="float", min_limit=eval(data_axis_size[1]), max_visible=eval(data_axis_size[2]))
    data_axis_width = get_value_from_data(parameters, "axis_width", ["value", "min_limit", "max_visible"], [2.0, 0.1, 4.0])
    prop_params.add_parameter(group="axis_settings", name="axis_width", visual_name="Axis Width", value=eval(data_axis_width[0]), type="float", min_limit=eval(data_axis_width[1]), max_visible=eval(data_axis_width[2]))
    data_axis_arrow_size = get_value_from_data(parameters, "axis_arrow_size", ["value", "min_limit", "max_visible"], [5.0, 0.1, 10.0])
    prop_params.add_parameter(group="axis_settings", name="axis_arrow_size", visual_name="Axis Arrow Size", value=eval(data_axis_arrow_size[0]), type="float", min_limit=eval(data_axis_arrow_size[1]), max_visible=eval(data_axis_arrow_size[2]))

    data_axis_shift_x = get_value_from_data(parameters, "axis_shift_x", ["value", "min_limit", "max_visible"], [50, 0, 128])
    prop_params.add_parameter(group="axis_settings", name="axis_shift_x", visual_name="Axis Shift X", value=eval(data_axis_shift_x[0]), type="integer", min_limit=eval(data_axis_shift_x[1]), max_visible=eval(data_axis_shift_x[2]))
    data_axis_shift_y = get_value_from_data(parameters, "axis_shift_y", ["value", "min_limit", "max_visible"], [50, 0, 128])
    prop_params.add_parameter(group="axis_settings", name="axis_shift_y", visual_name="Axis Shift Y", value=eval(data_axis_shift_y[0]), type="integer", min_limit=eval(data_axis_shift_x[1]), max_visible=eval(data_axis_shift_x[2]))
    data_axis_x_color = get_value_from_data(parameters, "axis_x_color", ["value"], [(255, 0, 0, 255)])
    prop_params.add_parameter(group="axis_settings", name="axis_x_color", visual_name="X Axis Color", value=eval(data_axis_x_color[0]), type="color")
    data_axis_y_color = get_value_from_data(parameters, "axis_y_color", ["value"], [(0, 255, 0, 255)])
    prop_params.add_parameter(group="axis_settings", name="axis_y_color", visual_name="Y Axis Color", value=eval(data_axis_y_color[0]), type="color")
    data_axis_z_color = get_value_from_data(parameters, "axis_z_color", ["value"], [(0, 0, 255, 255)])
    prop_params.add_parameter(group="axis_settings", name="axis_z_color", visual_name="Z Axis Color", value=eval(data_axis_z_color[0]), type="color")
    prop_params.add_group("grid_settings", "Grid Settings")
    data_show_grid = get_value_from_data(parameters, "show_grid", ["value"], [True])
    prop_params.add_parameter(group="grid_settings", name="show_grid", visual_name="Show Grid", value=eval(data_show_grid[0]), type="boolean")
    data_grid_step_size = get_value_from_data(parameters, "grid_step_size", ["value", "min_limit", "min_visible", "max_visible"], [1.0, 0.0, 0.0, 5.0])
    prop_params.add_parameter(group="grid_settings", name="grid_step_size", visual_name="Grid Step Size", value=eval(data_grid_step_size[0]), type="float", min_limit=eval(data_grid_step_size[1]), min_visible=eval(data_grid_step_size[2]), max_visible=eval(data_grid_step_size[3]))

    data_grid_count = get_value_from_data(parameters, "grid_count", ["value", "min_limit", "max_visible"], [10, 2, 24])
    prop_params.add_parameter(group="grid_settings", name="grid_count", visual_name="Lines Count", value=eval(data_grid_count[0]), type="integer", min_limit=eval(data_grid_count[1]), max_visible=eval(data_grid_count[2]))

    data_grid_subdivs = get_value_from_data(parameters, "grid_subdivs", ["value", "min_limit", "min_visible", "max_visible"], [5, 1, 1, 10])
    prop_params.add_parameter(group="grid_settings", name="grid_subdivs", visual_name="Grid Subdivs", value=eval(data_grid_subdivs[0]), type="integer", min_limit=eval(data_grid_subdivs[1]), min_visible=eval(data_grid_subdivs[2]), max_visible=eval(data_grid_subdivs[3]))
    data_grid_center = get_value_from_data(parameters, "grid_center", ["value"], [True])
    prop_params.add_parameter(group="grid_settings", name="grid_center", visual_name="Draw Center", value=eval(data_grid_center[0]), type="boolean")
    data_grid_color = get_value_from_data(parameters, "grid_color", ["value"], [(178, 178, 178, 128)])
    prop_params.add_parameter(group="grid_settings", name="grid_color", visual_name="Grid Color", value=eval(data_grid_color[0]), type="color")
    data_grid_subgrid_color = get_value_from_data(parameters, "grid_subgrid_color", ["value"], [(178, 178, 178, 64)])
    prop_params.add_parameter(group="grid_settings", name="grid_subgrid_color", visual_name="Subgrid Color", value=eval(data_grid_subgrid_color[0]), type="color")
    data_grid_center_color = get_value_from_data(parameters, "grid_center_color", ["value"], [(229, 229, 229, 192)])
    prop_params.add_parameter(group="grid_settings", name="grid_center_color", visual_name="Center Lines Color", value=eval(data_grid_center_color[0]), type="color")

    if file_exist is False:
        prop_params.save_xml(file_path)
    return prop_params


def read_style_settings_from_file(file_path, host_widget):
    set_name = "Style Settings"
    label_width = 92
    file_exist = False
    parameters = []
    if os.path.isfile(file_path):
        file_exist = True
        tree = ET.parse(file_path)
        (groups, parameters) = from_tree_to_data(tree)
        root = tree.getroot()
        set_name = root.attrib["name"] if "name" in root.attrib.keys() else "Style Settings"
        label_width = int(root.attrib["label_width"]) if "label_width" in root.attrib.keys() else 92
    params = ParametersSet(host=host_widget, name=set_name, label_width=label_width)
    styles_data = StylesClass()
    style_names = styles_data.get_names()

    style_names = get_value_from_data(parameters, "style_names", ["value", "items", "min_limit", "max_limit"], [styles_data.get_current_style_index(), style_names, 0, len(style_names) - 1])
    params.add_parameter(name="style_names", visual_name="Style", value=(eval(style_names[0]), eval(style_names[1])), type="combobox", min_limit=eval(style_names[2]), max_limit=eval(style_names[3]))

    use_colors = get_value_from_data(parameters, "use_colors", ["value"], [True])
    params.add_parameter(name="use_colors", visual_name="Use Style Colors", value=eval(use_colors[0]), type="boolean")

    if file_exist is False:
        params.save_xml(file_path)
    return (params, styles_data)
