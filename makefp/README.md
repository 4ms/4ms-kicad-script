## Makefp plugins

These plugins convert a PCB file to a Eurorack-compatible faceplate. You must
manually add your own artwork on the silk and/or copper layers.

This works with Kicad 6. It does not work with Kicad 5 or earlier. It has not
been tested with Kicad nightlies (6.99).

## How to install:

  * These scripts use the 4ms KiCad library for faceplate holes. You must have
	this installed. Clone or download the 4ms KiCad lib repository
	[here](https://github.com/4ms/4ms-kicad-lib.git)

  * Inside the makefp folder, copy the `faceplate_footprint_lib_TEMPLATE.py`
	file and name it `faceplate_footprint_lib.py`. 

  * Edit `faceplate_footprint_lib.py` and change the path to the location of
	the `4ms_Faceplate.pretty` folder on your computer.

  * Install the plugin files by copying all *.py files in the makefp directory
	to the Kicad 6 plugin directory. To find the latter, open Kicad PCB Editor
	and select `Tools` > `External Plugins` >`Reveal Plugin Folder`.


  * As an alternative to the last step, you can create symlinks instead of
	copying (useful if you're using git to update the repository and want the
	plugins updated without having to re-copy them). Example on linux or macOS:

	```
	ln -s /full/path/to/4ms-kicad-script/makefp/kicad-6-plugin/* /full/path/to/KiCad/6.0/scripting/plugins/
	```

	On Windows, run as Admin (thanks @electron271)

	```
	mklink X:\full\path\to\4ms-kicad-script\makefp\kicad-6-plugin\* X:\full\path\to\KiCad\6.0\scripting\plugins\
	```


## How to use:

First, make a copy of the project you wish to convert to a Eurorack faceplate.
You can remove the schematic files and the sym-lib-table file if you wish (they
aren't used). Add the `4ms_Faceplate.pretty` library to the new project's
Project Specific Footprint Libraries.

There are 4 scripts which should be run in order:

  * Step 1: Remove Tracks and Vias: **This script is currently broken on Kicad
	6.** But, it's easy to manually do step 1. Just use the Selection Filter
	checkboxes (lower-right corner of PCB window) and check Vias and Tracks.
	Use the mouse to select everything (which will select all vias and tracks)
	and then delete all the selected items. Next delete all footprints on the
	front side (you can use Selection Filters as well as hiding back side
	components). You may also want to delete Graphics, Other Items, Text,
	Zones, Dimensions, etc... Use your judgement: whatever you don't want on
	the faceplate, delete.

  * Step 2: Create Outline. This script creates a Eurorack-sized outline on the
	Edge.Cuts layer that encloses the entire board, and adds rack-mounting
	slots in the right place. The height will be 5.059" (128.5mm) and the width
	will be a multiple of 0.2" (5.08mm) minus a fudge factor given in the A-100
	mechanical specifications. The script also moves the existing PCB outline
	on the Edge.Cuts layer to User.Comments layer. For narrow faceplates (<8HP), 
	the script will create too many rail-mounting slots. Just delete what you
	don't want.

  * Step 3: Convert Footprints. This script looks for any footprints on the
	back side that it recognizes as a faceplate component. These are things
	like jacks, pots, switches, buttons, sliders, LEDs. Then it replaces each
	one with a hole or cutout and flips it across the center Y axis. The hole
	or cutout is actually a footprint from the `4ms_Faceplate` library, and
	should be the proper size for the original component to fit on a faceplate.
	If you use faceplate components (jacks, etc) from outside of the 4ms
	footprint libraries, then you probably will need to edit the dictionary at
	the top of the script, adding your own footprints and replacements in.
	Tips:
	  - Faceplate footprints must be on the Back side (B.Cu layer). Anything on
		the front side is ignored
	  - Footprints on the back side that are in the `remove_fps` list will be
		removed. All others are ignored.
	  - The footprint name of each faceplate footprints must have an exact
		match in the `footprint_convert` dictionary at the top of the script.
	  - The path in `faceplate_footprint_lib.py` must be an absolute path to
		the `4ms_Faceplate.pretty` library (including the .pretty folder
		itself) .

  * Step 4: Make Ground Plane. This step creates a zone on the back side, and
	assigns it to the GND net. It also assigns each footprint's pin(s) to the
	GND net. This creates a solid plane on the back of the faceplate connecting
	all the holes. 

  * Step 5: This is not a script (yet) but is done manually. Add a
	`Rail_Connection_XXHP` footprint from the `4ms_Faceplate` library to the
	top and bottom of the faceplate PCB. Place them on the back side and assign
	the pads to the GND net. This creates a contact surface between a metallic
	case and the faceplate. Obviously, you will need to add the `4ms_Faceplate`
	library to your KiCad project in order to add these footprints.


