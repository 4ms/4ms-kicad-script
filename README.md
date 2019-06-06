##4ms Kicad Scripts##

Here are some utilities for working with kicad.

**All of these scripts are Works In Progress. Use at your own risk!!**

  * makefp: PCB plugins (python scripts) to create a Eurorack faceplate from a PCB. Automatically determines smallest standard size that will fit, creates an outline and rail mounting slots, replaces all panel components with holes (using a look-up table that you must edit if you're not using standard 4ms libraries), removes all SMT components and traces, and creates a copper GND plane on the back (connecting all holes to it).

  * picknplace_assistant: Creates PDF files of front and back of PCB, showing the placement of each component.

  * update\_kicad: OSX only. After you download and mount a Kicad nightly DMG, run this script to handle installing all the files, and properly merging the global fp/sym\_lib\_table files without having to manually add the 4ms libraries. This script also preserves your packages3d folder.

  * gerbv shortcuts. These are meant to be used with the old legacy gerbv program (not kicad's gerbv). They are templates that set the layer order and coloring to a standard format.

  * BOM-scripts: EEschema plugins that produce a BOM properly formatted for a PCBA service.

  * grep-replace-globallabel-with-locallabel: regex to replace all global labels with local labels in eechema. 