## 4ms Kicad Scripts

Here are some utilities for working with Kicad.

**All of these scripts are Works In Progress. Use at your own risk!!**

  * makefp: PCB plugins (python scripts) to create a Eurorack faceplate from a PCB. Automatically determines smallest standard size that will fit, creates an outline and rail mounting slots, replaces all panel components with holes (using a look-up table that you must edit if you're not using standard 4ms libraries), removes all SMT components and traces, and creates a copper GND plane on the back (connecting all holes to it). It's not perfect and often requires some manual clean-up.

  * BOM-scripts: EEschema plugins that produce a BOM properly formatted for a PCBA service.

  * lib_scripts: a series of scripts used to create a KiCad symbol library from a BOM CSV file and a group of schematics that share common parts. Originally written for the [OpenVentilator](https://gitlab.com/openventilator/openventilator) project. When importing projects into Kicad from other EDA software, a library is created for each imported project, so these scripts are handy for essentially merging all the individual project libraries into a single shared library (and throw in some useful information from a BOM file while it's at it). We also have used these scripts to create the latest 4ms symbol libraries (atomic part library) since we have all MPN etc information in the BOM files.

  * lib_scripts/symLibConversion: This script does some of the rote search-and-replacement when updating a legacy 4ms library schematic to the new atomic libraries.

  * gerbv shortcuts. These are meant to be used with the old legacy gEDA gerbv program (not kicad's gerbv). They are templates that set the layer order and coloring to a standard format.

  * net_tools: Some PCBnew python plugins.

  * grep-replace-globallabel-with-locallabel: regex to replace all global labels with local labels in eechema. 

  * XY-pos-file-convert: A simple python script to convert Kicad's XY position file format to the one JLCPCB expects.

#### Deprecated Utilities ####

  * picknplace_assistant: Creates PDF files of front and back of PCB, showing the placement of each component. No longer being supported, as we've switched to using [Interactive HTML Bom](https://github.com/openscopeproject/InteractiveHtmlBom).

  * update\_kicad: OSX only. After you download and mount a Kicad nightly DMG, run this script to handle installing all the files, and properly merging the global fp/sym\_lib\_table files without having to manually add the 4ms libraries. This script also preserves your packages3d folder. No longer being supported, as our new library technique doesn't require modifying global library tables.

