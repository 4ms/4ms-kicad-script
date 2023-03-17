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
    Value, Specifications, Designation, Manufacturer, Part number, Footprint, Comments, Stage

    """
    result = True
    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
        print(self.getPartName())
        result = False
    elif self.getFootprint() != other.getFootprint():
        result = False
    elif self.getField("Specifications") != other.getField("Specifications"):
        result = False
    elif self.getField("Designation") != other.getField("Designation"):
        result = False
    elif self.getField("Manufacturer") != other.getField("Manufacturer"):
        result = False
    elif self.getField("Comments") != other.getField("Comments"):
        result = False

    return result

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

#FixMe: Don't use this list of columns twice
columns = ['Item#', 'Manufacturer', 'Part #', 'Designator', 'Qnty', 'Designation', 'Package', 'SMD/TH', 'Layer', 'Points', 'Total Points', 'Comments']

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
writerow( out, ['Component Count:', len(components)] )
writerow( out, [] )
writerow( out, ['Item#', 'Manufacturer', 'Manufacter Part#', 'Designator', 'Quantity', 'Designation', 'Package', 'SMD/TH', 'Points', 'Total Points', 'Comments', 'Supplied by:'])

row = []
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
item = 0
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    item += 1

    package = get_package(c.getFootprint())

    [smd, points] = deduce_SMD_TH(package)
    totalpoints = (len(group) * points)

    value = c.getValue()


    if (package=='R0603') and (c.getField("Specifications") == ""):
        [manufacturer, part_no, designation] = deduce_0603_resistor(value)

    else :
        designation = combine_specs_and_value(c)
        manufacturer = c.getField("Manufacturer")
        part_no = c.getField("Part Number") + c.getField("Part number") # we've used both lower and upper-case 'n' in the past 
    
    # if (c.getField("JLCPCB ID")):
    #     part_no = c.getField("JLCPCB ID")

    row.append( item )
    row.append( manufacturer )
    row.append( part_no )
    row.append( refs );
    row.append( len(group) )
    row.append( designation )
    row.append( package )
    row.append( smd )
    row.append( points )
    row.append( totalpoints )
    row.append( c.getField("Comments"))

    #FixMe: test if this line is doing anything
    for field in columns[12:]:
        row.append( net.getGroupField(group, field) );

    writerow( out, row  )

f.close()
