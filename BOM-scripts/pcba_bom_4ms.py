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
import textwrap
import re
import partnum_magic

today = date.today()
wrapper = textwrap.TextWrapper(width=5)



def groupingMethod(self, other):
    """groupingMethod is a more advanced equivalence function for components which is
    used by component grouping. Normal operation is to group components based
    on their value and footprint.

    For the 4ms BOM we group components based on:
    Value, Specifications, Designation, Manufacturer, Part number, Footprint, Comments

    """
    result = True
    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
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

# 'hard coded' column list
columns = ['Item#', 'Manufacturer', 'Part #', 'Designator', 'Qnty', 'Designation', 'Package', 'SMD/TH', 'Layer', 'Points', 'Total Points', 'Comments']

# Create a new csv writer object to use as the output formatter
out = csv.writer( f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL )

# override csv.writer's writerow() to support encoding conversion (initial encoding is utf8):
def writerow( acsvwriter, columns ):
    utf8row = []
    for col in columns:
        utf8row.append( str(col) )  # currently, no change
    acsvwriter.writerow( utf8row )


# Output a set of rows as a header providing general information
#writerow( out, ['Source:', net.getSource()] )
# NEED TO ADD NAME OF MODULE/PROJECT, COMPANY NAME, EMAIL ADDRESS, AND DISPLAY THE DATE SOMEWHERE BETTER
writerow( out, ['4ms Company'] )
writerow( out, ['PCBA Project:', 'MODULE NAME'] )
writerow( out, ['EMAIL:', '4ms@4mscompany.com'] )
writerow( out, ['DATE:', today] )
writerow( out, ['Component Count:', len(components)] )
writerow( out, [] )
writerow( out, ['Item#', 'Manufacturer', 'Manufacter Part#', 'Designator', 'Quantity', 'Designation', 'Package', 'SMD/TH', 'Points', 'Total Points', 'Comments', 'Supplied by:'])


# Output all the interesting components individually first:
row = []

# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
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
              
    #deletes footprint library name from Footprint name
    fprint = str(c.getFootprint())
    package = re.sub(r".*:", "", fprint)
    
    refcheck = str(refs[0])
    value = c.getValue()
    designation = c.getField("Specifications")
    if (designation == "" or designation == None):
        designation = c.getField("Designation")

    #Automatically fill in part numbers for R0603 package
    if (refcheck == "R") and ('0603' in package) and (designation == ""):
        [manufacturer, part_no, designation] = partnum_magic.deduce_0603_resistor(value)

    else:
        manufacturer = c.getField("Manufacturer")
        part_no = c.getField("Part number")
        if (designation.startswith(value) == False):
            if (designation == ""):
                designation = value
            else:
                designation = value + ", " + designation


    #checks if package contains certain letters to decide if its SMD
    smdcheck = str(package[-4:]) #  package at end
    smdcheck2 = str(package[0:7]) # package at start
    headercheck = str(package[0:4]) #TH headers
    if (   smdcheck == ("0603") 
        or smdcheck == ("0805") 
        or smdcheck == ("1206")
        or smdcheck == ("323F")
        or smdcheck == ("-123")
        or smdcheck2 == ("CP_Elec")
        ):
        smd = ("SMD")
        points = int(2)
 
    elif (smdcheck == ("C33X")
        or smdcheck == ("OT23")
        ):
        smd = ("SMD")
        points = int(3)

    elif smdcheck == ("CC-4"):
        smd = ("SMD")
        points = int(4) 

    elif smdcheck2 == ("SOT-363"):
        smd = ("SMD")
        points = int(6)

    elif smdcheck2 == ("TSSOP-8"):
        smd = ("SMD")
        points = int(8)
        
    elif smdcheck2 == ("SOIC-14"):
        smd = ("SMD")
        points = int(14)

    #TH headers
    elif headercheck == ("Pins"):
        smd = ("TH")
        points = ("")
    
    else:
        smd = ("")
        points = ("")

    #cleans up some underscores
    if package == ("R_0603"):
        package = ("R0603") 
    if package == ("R_0402"):
        package = ("R0402") 
    if package == ("C_0603"):
        package = ("C0603")
    if package == ("C_0805"):
        package = ("C0805")
    if package == ("C_1206"):
        package = ("C1206")
    if package == ("C_1210"):
        package = ("C1210")

    #calculate total points
    totalpoints = (len(group) * points)

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

    # from column 7 upwards, use the fieldnames to grab the data
    for field in columns[12:]:
        row.append( net.getGroupField(group, field) );

    writerow( out, row  )

f.close()
