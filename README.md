# Stacking Tool
## Overview
This Blender addon can be used to stack multiple meshes on top of each other in the direction of a specified axis. The created stack can be rotated and reordered using seeded randomization. Stacked objects will have no intersection with each other, so that their bounding boxes perfectly align.

![Stacking_Tool_Overview Image](https://github.com/flo-wolf/blender-stacking-tool/blob/master/images/stacking_tool_process_showcase_s.png?raw=true)

## Usage
The Stacking Tool is accessible through the Object Menu `Object > Stack Objects`. In order to use it, multiple meshes need to be selected, where one of them needs to be active (yellow selection outline).

The tool is divided into two main components: Stacking and Rotation. Each has different options which alter how the resulting stack will look like. The selected objects get stacked by clicking the 'OK' button, or when performing changes to the settings after the 'OK' button has been clicked. All changes this tool makes to the objects can be undone.


## Settings

![Stacking_Tool_Panel_Image](https://github.com/flo-wolf/blender-stacking-tool/blob/master/images/stacking_tool_panel_shadow.png?raw=true)

### Stacking
- **Axis** - The axis the selected objects should be stacked onto

- **Center Objects on Axis** – Toggle if all selected objects should be aligned on the specified axis with the active object, so that they are all in line with each other

- **Offset** – The distance between each stacked object

- **Stacking Order Seed** – Changing the seed shuffles the objects, so that the objects will have a different position in the stack. The active object will always be at the bottom.


### Rotation
- **Axis** - The axis the selected objects should be locally rotated around

- **Enable Rotation** – Toggle if the selected objects should get rotated

- **Rotate Active Object** –Toggle if the active object (yellow selection outline) gets rotated too

- **Rotation Angle Step** - The angle at which objects should get randomly rotated around the rotation axis

- **Rotation Seed** – Changing the rotation seed will result in different random rotations 


<br/><br/>


![Stacking_Tool_Overview Image](https://github.com/flo-wolf/blender-stacking-tool/blob/master/images/stacking_tool_stacks_showcase_m.png?raw=true)

