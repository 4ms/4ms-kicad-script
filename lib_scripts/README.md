### Lib Scripts ###

These scripts were used in the OpenVentilator Kicad project to facilitate
merging BOM CSV files with Kicad projects. The Kicad projects were created by
importing from other PCB software, and the libraries information was not
complete.

These scripts are used to scan one or more BOM files, extract the Manufacturer
and Part Number, etc. data, and then insert that data into the appropriate
symbols in one or more Kicad symbol library file. The scripts "know" which
library symbol to update by using the Reference Designator listed in the BOM,
and scanning one or more Kicad schematic files for a symbol with this RefDes.
If the RefDes is found in a schematic, and the schematic symbol lists a valid
library symbol, then that library symbol will be updated with the BOM data.

Alternatively, the scripts can create a new library file if no library files
already exist. The new library files can be split into various part types based
on Reference prefix (i.e. R = Resistor.lib, C = Capacitor.lib, D = Diode.lib,
etc..)

These scripts were used to create the 4ms lib-sym libraries.  The scripts in
the symLibConversion/ directory will help update a schematic using the old
lib-sch libraries.
