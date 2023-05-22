#
# Example python script to generate a BOM from a KiCad generic netlist
#
# Example: Sorted and Grouped CSV BOM
#
"""
    @package
    Generate a csv BOM list.
    Components are sorted by ref and grouped by value
    Fields are (if exist)
    Item, Qty, Reference(s), Value, LibPart, Footprint, Datasheet

    Command line:
    python "pathToFile/bom_csv_grouped_by_value.py" "%I" "%O.csv"
"""

from __future__ import print_function

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader_4ms
import re
import csv
import sys
from datetime import date
import os
from partnum_magic import *


def get_project_info(net):
    full_path = net.getSource()
    [schematic_name, ext] = os.path.splitext(os.path.basename(full_path))
    [revisionpath, sch_file] = os.path.split(full_path)
    [projectpath, revision] = os.path.split(revisionpath)
    return [schematic_name, revision]

def combine_specs_and_value(c):
    value = c.getValue()
    designation = c.getField("Specifications")
    if (designation == "" or designation == None):
        designation = c.getField("Designation")
    if (designation.upper().startswith(value.upper()) == False):
        if (designation == ""):
            designation = value
        else:
            designation = value + ", " + designation
            
    return designation

def groupingMethod(self, other):
    """groupingMethod is a more advanced equivalence function for components which is
    used by component grouping. 
    For the 4ms BOM we group components based on:
    Value, Specifications, Designation, Manufacturer, Part number, Footprint, Comments

    """
    should_group = True
    if self.getValue() != other.getValue():
        should_group = False
    elif self.getFootprint() != other.getFootprint():
        should_group = False
    elif self.getField("Specifications") != other.getField("Specifications"):
        should_group = False
    elif self.getField("Designation") != other.getField("Designation"):
        should_group = False
    elif self.getField("Manufacturer") != other.getField("Manufacturer"):
        should_group = False
    elif self.getField("Comments") != other.getField("Comments"):
        should_group = False
    elif self.getField("Production Stage") != other.getField("Production Stage"):
        should_group = False
    elif self.getPartName() != other.getPartName():
        # PartName is the name of the part in the library
        # If either part name begins with the other (e.g. "10k_0402" and "10k_0402_7") then treat it like they're the same part.
        # Otherwise, treat them differently
        # Note: KiCad adds a "_1" or "_n" to the end of PartNames when parts may be from a different library version or not updated properly
        # But sometimes a DNP can cause part names to differ and we DO want those to be grouped differently
        print("PartNames differ: " + self.getRef() + " (" + self.getPartName() + ")" + " != " + other.getRef() + " (" + other.getPartName() + ")")

        # Don't group them if neither one is the same as the beginning of the other
        if not (self.getPartName().startswith(other.getPartName()) or other.getPartName().startswith(self.getPartName())):
            should_group = False
            print("<<< >>> will be grouped separately")
        else:
            print("======= one starts with the other and all other fields match, so they will be grouped")

    return should_group

# Grouping of components is done with the equivalence (__eq__) operator.
# Override the component equivalence operator now - it is important to do this
# before loading the netlist, otherwise all components will have the original
# equivalency operator
kicad_netlist_reader_4ms.comp.__eq__ = groupingMethod


if len(sys.argv) != 3:
    print("Usage ", __file__, "<generic_netlist.xml> <output.csv>", file=sys.stderr)
    sys.exit(1)

# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader_4ms.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    f = open(sys.argv[2], 'w')
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print( __file__, ":", e, sys.stderr )
    f = sys.stdout

# subset the components to those wanted in the BOM, controlled
# by <configure> block in kicad_netlist_reader.py
components = net.getInterestingComponents()

# Create a new csv writer object to use as the output formatter
out = csv.writer( f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL )

# override csv.writer's writerow() to support encoding conversion (initial encoding is utf8):
def writerow( acsvwriter, columns ):
    utf8row = []
    for col in columns:
        utf8row.append( str(col) )
    acsvwriter.writerow( utf8row )

[schematic_name, revision] = get_project_info(net)

# Output a set of rows as a header providing general information
writerow( out, ['4ms Company'] )
writerow( out, ['PCBA Project:', schematic_name, 'Revision: ', revision] )
writerow( out, ['EMAIL:', '4ms@4mscompany.com'] )
writerow( out, ['DATE:', date.today()] )
writerow( out, [] )
writerow( out, ['Group', 'Item#', 'Manufacturer', 'Manufacter Part#', 'Designator', 'Quantity', 'Designation', 'Package', 'Comments', 'Supplied by:'])


row = []
list_main = []
grouped = net.groupComponents(components)
item = 0

# Output component information organized by group, aka as collated:
for group in grouped:
    refs = ""
    for c in group:
        if len(refs) > 0:
            refs += ", "
        refs += c.getRef()
    package = get_package(c.getFootprint())
    value = c.getValue()
    qty = len(group)
    manufacturer = c.getField("Manufacturer")
    part_no = c.getField("Part Number") + c.getField("Part number")
    stage = c.getField("Production Stage")
    if part_no == "DNP":
        comments = "DNP"
    else:
        comments = ""

    if (package=='R0603') and (c.getField("Specifications") == ""):

        [manufacturer, part_no, designation] = deduce_0603_resistor(value)

    else :
        designation = combine_specs_and_value(c)
        manufacturer = c.getField("Manufacturer")
        part_no = c.getField("Part Number") + c.getField("Part number") # we've used both lower and upper-case 'n' in the past 
#to do: Add a code to recognize DNP in part name and print to COMMENTS column
    row = [stage, manufacturer, part_no, refs, qty, designation, package, comments]
    list_main.append(row)

#sort list of lists by Group    
list_main.sort(key=lambda x: x[0])


for row in list_main:
    item += 1
    row.insert(1, item)
    writerow( out, row )

f.close()
