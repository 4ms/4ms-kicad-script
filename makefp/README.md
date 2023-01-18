## Make Eurorack Faceplate plugin

This plugin converts a PCB file to a Eurorack-compatible faceplate. You must
manually add your own artwork on the silk.

This works with Kicad 6 and Kicad 7. It does not work with Kicad 5 or earlier. 

## How to install:

  * These scripts use the 4ms KiCad library for faceplate holes. You must have
	this installed. Clone or download the 4ms KiCad lib repository
	[here](https://github.com/4ms/4ms-kicad-lib.git)

  * Inside the `makefp` directory, there is one directory for Kicad 6 and one
    for Kicad 7. Decide which one you are using and open that directory. Inside there
    you will see a file named `faceplate_footprint_lib_TEMPLATE.py`. Rename that file
	file to `faceplate_footprint_lib.py`. 

  * Open the `faceplate_footprint_lib.py` you just renamed in a text editor and
    change the line with the path (line 4) to the path of the `4ms_Faceplate.pretty` folder on
    your computer. For example, you might change line 4 to this:
    
    ```
    return "/Users/MyName/MyKicadStuff/4ms-kicad-lib/footprints/4ms_Faceplate.pretty"
    ```

  * Install the plugin files by copying the two files in the
    `makefp/kicad-#-plugin` directory to the Kicad plugin directory. 
    To find the latter, open Kicad PCB Editor and select `Tools` > `External
    Plugins` > `Reveal Plugin Folder`. Make sure you copy the two files
    (faceplate_footprint_lib.py and make_eurorack_fp.py) and not the
    `kicad-#-plugin` folder itself.


## How to use:

First, make a copy of the project you wish to convert to a Eurorack faceplate.
You can remove the schematic files and the sym-lib-table file if you wish (they
aren't used). Add the `4ms_Faceplate.pretty` library to the new project's
Project Specific Footprint Libraries.

Run the script by selecting the plugin from `Tools` > `External Plugins`.
If the plugin doesn't show up, you may have either installed it in the wrong
directory, or goofed up when you editted the path.

When you run the script the following will happen:

  * All tracks and vias will be removed

  * Drawings on the Edge.Cuts layer will be moved to the Cmts.User layer

  * The smallest standard Eurorack-sized rectangle that fits around the
    original PCB will be drawn on the Edge.Cuts layer (up to 28HP). Dimensions
    are from the A-100 mechanical specifications.

  * Rail-mount slots will be added at the proper places (4 total). For small
    boards you probably will want to delete a pair.

  * Footprints that recognized panel componets (pots, jacks, LEDs, etc) will be converted to a
    Faceplate Hole. See note below for details

  * Many footprints will be removed.

  * A ground plane will be created on the back side and given the net GND.

  * Each faceplate hole is connected to the ground plane.


After this, you need to manually do three things:
  * Inspect the board and delete any remaining components. The script is conservative
    and does not remove a component unless it's absolutely sure it can be deleted.
    Often there will be a handful of components remaining, which you must delete manually.

  * Add a `Rail_Connection_XXHP` footprint from the `4ms_Faceplate` library to the
	top and bottom of the faceplate PCB. Place them on the back side and assign
	the pads to the GND net. This creates a contact surface between a metallic
	case and the faceplate. TODO: Do this automatically

  * Add your artwork. Typically you will export a 2000dpi PNG file from your graphic
    design program, and then use Kicad's Image Converter tool to convert that to a 
    footrprint (select the option for Silkscreen layer). Save the converted file as a 
    new footprint library, and add the library to your project. Then place the footprint
    on the top of your board.

Note on converting footprints: This script looks for any footprints on the back
side that it recognizes as a faceplate component. These are things like jacks,
pots, switches, buttons, sliders, LEDs. Then it replaces each one with a hole
or cutout and flips it across the center Y axis. The hole or cutout is actually
a footprint from the `4ms_Faceplate` library, and should be the proper size for
the original component to fit on a faceplate. If you use faceplate components
(jacks, etc) from outside of the 4ms footprint libraries, then you probably
will need to edit the dictionary at the top of the script, adding your own
footprints and replacements in.
	Tips:
	  - Faceplate footprints must be on the Back side (B.Cu layer). Anything on
		the front side is ignored
	  - Footprints on the back side that are in the `remove_fps` list will be
		removed. All others are ignored.
	  - The footprint name of each faceplate footprints must have an exact
		match in the `footprint_convert` dictionary at the top of the script.
	  - The path in `faceplate_footprint_lib.py` must be an absolute path to
		the `4ms_Faceplate.pretty` library (including the .pretty folder
		itself).



