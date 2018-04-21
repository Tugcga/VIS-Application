# VIS-Application

This is Python based application for view 3d-models. Support loading only obj-models.

Require Python 3.x and two modules: PyQt4 and visPy.

## Change hotkeys and interaction

All settings of hotkeys stored in the file application\data\shortcuts.xml By default it looks like the following:

```
<shortcuts>
    <command key="A" label="Fit Camera View" name="fit_camera" />
	<command key="Ctrl+C" label="Clear Scene" name="clear_scene" />
    <command key="Ctrl+O" label="Open..." name="open" />
    <command key="Ctrl+Q" label="Quit" name="quit" />
    <command key="Ctrl+E" label="Enable/Disable Layout Edit" name="edit_layout" />
    <command key="Ctrl+P" label="Scene Properties..." name="show_poroperties" />
	<command key="Ctrl+R" label="Render Settings..." name="show_render_settings" />
	<command key="Ctrl+V" label="Style Settings..." name="show_style_settings" />
    <camera>
        <orbit key="S" mouse="Right" />
        <pan key="S" mouse="Left" />
        <zoom key="S" mouse="Middle" />
    </camera>
</shortcuts>
```

In this file you can set hotkeys for all supported commands. Also in camera section you can set interaction keys. By default VIS-Application uses Softimage camera interaction keys: you can rotate camera by pressing "s" and right mouse button, pan camera by pressing "s" and left mouse button, zoom camera by pressing "s" and middle mouse button.  The following scheme for Blender default interaction keys:

```
<camera>
    <orbit key="" mouse="Middle" />
    <pan key="Shift" mouse="Middle" />
    <zoom key="Ctrl" mouse="Middle" />
</camera>
```

## Change layout

Layout of the VIS-Applications based on dockable widgets. Any window can be docked or floated. Turn on "View - Enable Layout Edit" for moving windows. To fix docked windows size select "View - Disable Layout Edit".

![Screen with the program window](screen.png?raw=true)