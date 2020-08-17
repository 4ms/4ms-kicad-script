# This script is barely tested, and not meant for public use.
# Use at your own risk!

#Output files:
output_dir = 'Symbols2'
csv_output_filename = output_dir+'/library_bom.csv'

default_bom_filename = 'bom.csv'

# Set the column names found in the bom file here:
itemnum_header = 'Item#'
refs_header = 'Designator'
desc_header = 'Designation'
manu_header = 'Manufacturer'
manuNo_header = 'Manufacter Part#'
footprint_header = 'Package'

itemnum_field = 'ID'
desc_field = 'Specifications'
manu_field = 'Manufacturer'
manuNo_field = 'Part Number'


# These are the file names we should use for common component prefixes.
# If not found here, the library will be named by the prefix (example: Z.lib)
library_name_prefix_map = {
        "C": "Capacitor",
        "ZC": "Capacitor",
        "R": "Resistor",
        "L": "Inductor",
        "FI": "Inductor",
        "Q": "Crystal",
        "X": "Crystal",
        "D": "Diode",
        "CR": "Diode",
        "PG": "Diode",
        "FU": "Fuse",
        "F": "Fuse",
        "PCT": "Fuse",
        "J": "Connector",
        "P": "Connector",
        "T": "Transistor",
        "Q": "Transistor",
        "ZT": "Transistor",
        "JP": "Jumper",
        "PT": "Jumper",
        "ML": "Varistor",
        "U": "IC",
        "IC": "IC",
        "G": "Battery",
        "BAT": "Battery",
        "BUZ": "Buzzer",
        "RL": "Relay",
        "RS": "Resistor",
        "REF": "Reference",
        "V": "Regulator",
        "SW": "Switch",
        "POT": "Potentiometer",
        "VR": "Potentiometer",
        "LED": "LED",
}

VALUE_FIELD_IDX = 1
FOOTPRINT_FIELD_IDX = 2
DATASHEET_FIELD_IDX = 3

import os
import sys
import csv
import re
from pathlib import Path
from autoSymbolName import *
from fileUtil import *
from symbolUtil import *

def readCacheLib(dirname):
    for path in Path(dirname).glob('*-cache.lib'):
        cachepath = path
    if cachepath is None:
        return None

    with open(cachepath) as f:
        print("Found cache library: "+cachepath.name)
        dat = f.read()
    return dat

def writeSchDatToFiles(schdat):
    for sch in schdat:
        with open(sch, "w") as f:
            print("Writing file: "+sch)
            f.write(schdat[sch])

def findLibByRefInSchdat(ref, schdat):
    lib_id = None
    matching_sch = None
    ref_prefix = getRefPrefix(ref)

    #Search by Library line (sometimes kicad sets the ref to X?, so this doesn't always work
    e_ref = re.escape(ref)
    regex = re.compile(r'\nL ([^ ]*) ' + e_ref + r'\n')
    for sch in schdat:
        ref_matches = regex.findall(schdat[sch])
        if len(ref_matches) > 0:
            matching_sch = sch
            print("Found library part name for "+ref+": " + ref_matches[0] + " in sheet "+matching_sch)
            break
    #Search by RefDes field line (Not sure if F 0 is guarenteed to be RefDes, but seems to be?)
    if matching_sch is None:
        regex = re.compile(r'^L ([^ ]+) '+ref_prefix+r'\?(?:\n[^\$].+)+\nF 0 "'+ref+r'" ', re.MULTILINE)
        for sch in schdat:
            ref_matches = regex.findall(schdat[sch])
            if len(ref_matches) > 0:
                matching_sch = sch
                print("Found ref des "+ref+": " + ref_matches[0] + " in sheet "+matching_sch)
                break

    if matching_sch is not None:
        full_part_name = ref_matches[0]
        if len(full_part_name) > 0:
           lib_id = full_part_name

    return lib_id, matching_sch

def mergeFieldsIntoSymbol(sym, existing_libsymdat):
    """ Given a symbol object
        And a text block of an existing library-format symbol,
        Merge the two and return the resulting text.
    """
    try:
        field_text = createAllFieldText(sym['field_list'])
    except:
        print("ERROR: symbol field_list not present")
        return sym

    sym, numfound = re.subn(
            r'\n(\$FPLIST\n)',
            r'\n' + field_text + r'\1',
            existing_libsymdat,
            re.MULTILINE | re.DOTALL)
    if numfound == 0:
        sym, numfound = re.subn(
                r'\n(DRAW\n)',
                r'\n' + field_text + r'\1',
                existing_libsymdat,
                re.MULTILINE | re.DOTALL)
        if numfound == 0:
            print("ERROR: could not merge fields "+field_text)
    return sym

def pullFieldFromList(field_list, field_name):
    try:
        val = [b for a,b,c in field_list if a==field_name][0]
    except:
        val = ""
    return val

def createSymbol(refslist, field_list, schdat):
    symbol={}
    for ref in refslist:
        if len(ref)==0:
            continue
        print("Searching for ref "+ref)
        lib_id, found_sch = findLibByRefInSchdat(ref, schdat)
        if found_sch is None:
            print("ERROR: Ref "+ref+" not found in any schematics")
            continue
        if lib_id is None:
            print("ERROR: Ref "+ref+" found but symbol library cannot be determined.")
            continue

        s = lib_id.split(":")
        if len(s) > 1:
            lib_name = s[0]
            part_name = s[1]
        else:
            lib_name = ""
            part_name = s[0]
        symbol['src_lib'] = lib_name
        symbol['name'] = part_name
        symbol['example_ref'] = ref
        symbol['example_sheet'] = found_sch
        symbol['refslist'] = refslist
        symbol['field_list'] = field_list

        #These are used to make CSV creation a bit easier:
        symbol[itemnum_field] = pullFieldFromList(field_list, itemnum_field)
        symbol[desc_field] = pullFieldFromList(field_list, desc_field)
        symbol[manu_field] = pullFieldFromList(field_list, manu_field)
        symbol[manuNo_field] = pullFieldFromList(field_list, manuNo_field)
        symbol['bom_footprint'] = pullFieldFromList(field_list, "Footprint")
        symbol['sch_footprint'] = extractFieldValFromSchSymbol(ref, FOOTPRINT_FIELD_IDX, schdat[found_sch])
        symbol['fp3d'] = "" #Todo: pull this from footprint library?
        symbol['Value'] = extractFieldValFromSchSymbol(ref, VALUE_FIELD_IDX, schdat[found_sch]) #Todo: deduce this from description?
        symbol['Documentation'] = extractFieldValFromSchSymbol(ref, DATASHEET_FIELD_IDX, schdat[found_sch])
        if getRefPrefix(ref) == 'R' or getRefPrefix(ref) == 'C':
            symbol['field_list'].append(('Display', symbol['Value'], -1))

        #print("Symbol created.")
        break
    return symbol

def formatCommonSymNames(syms):
    """Deduce Library Symbol names for common parts
        (resistors and capacitors and inductors)
    """
    for sym in syms:
        try:
            name = sym['name']
            firstchar = name[0]
        except:
            continue

        sym['formatted_name'] = sym['name']
        try:
            desc = sym[desc_field]
        except:
            continue

        fp = sym['sch_footprint']

        symbolname = deduceSymbolName(name, desc, fp)
        if len(symbolname) > 0:
            if symbolname != sym['name']:
                print(sym['name']+" formatted to "+symbolname+" based on description field "+desc+" and footprint "+fp)
            sym['formatted_name'] = symbolname

    return syms

def makeUniqueNames(syms):
    """ Given a list of symbol dictionaries,
        Find which name fields are duplicated and make them unique
        Return the unique-ified list of dictionaries
    """
    uniquenames=[]
    dup_names=[]
    for sym in syms:
        if 'formatted_name' not in sym.keys():
            continue
        if sym['formatted_name'] in uniquenames:
            dup_names.append(sym['formatted_name'])
        else:
            uniquenames.append(sym['formatted_name'])

    for sym in syms:
        if 'formatted_name' not in sym.keys():
            continue
        if itemnum_field not in sym:
            print("ERROR: symbol with name "+sym['formatted_name']+" has no Item Number")
        if sym['formatted_name'] in dup_names:
            sym['formatted_name'] += "_" + sym[itemnum_field]
            num = 0
            testname = sym['formatted_name']
            while testname in dup_names:
                num += 1
                testname = sym['formatted_name'] + "_" + str(num)
            sym['formatted_name'] = testname

    return syms


def createLibFromCache(syms, src_libdat):
    libdata = []
    for sym in syms:
        if 'name' not in sym.keys():
            continue
        cache_sym_name = sym['src_lib']+"_"+sym['name']

        print("Extracting "+cache_sym_name)
        existing_libsymdat = extractSymFromLib(cache_sym_name, src_libdat)
        if (existing_libsymdat is not None):
            symdata = removeExtraFields(existing_libsymdat)
            refp = getRefPrefix(sym['example_ref'])
            if refp=='R' or refp=='C':
                symdata = makeFieldInvisibleInSymText(1, "", symdata)
            symdata = mergeFieldsIntoSymbol(sym, symdata)

            fp = sym['sch_footprint'] or sym['bom_footprint']
            if fp:
                if checkSymbolNeedsUpdating(cache_sym_name, "", fp, FOOTPRINT_FIELD_IDX, symdata):
                    print("Updating footprint field of symbol: "+sym['formatted_name']+" to "+fp)
                    symdata, num = updateSymbolField(cache_sym_name, "Footprint", fp, FOOTPRINT_FIELD_IDX, symdata)

            if cache_sym_name is not sym['formatted_name']:
                print("Creating symbol "+sym['formatted_name']+" from libary symbol "+cache_sym_name)
            unique_symdata = renameSymbol(cache_sym_name, sym['formatted_name'], symdata)
            libdata.append(unique_symdata)
        else:
            print("ERROR: Failed to extract symbol data from cache for ref "+sym['example_ref']+", lib: "+sym['src_lib']+"_"+sym['name'])
    return libdata

def deduceLibraryFilename(sym):
    try:
        prefix = getRefPrefix(sym['example_ref'])

        if prefix in library_name_prefix_map:
            return library_name_prefix_map[prefix]+".lib"
        else:
            if len(prefix) > 0:
                return prefix+".lib"
            else:
                return "Unknown.lib"
    except:
        return "Unknown.lib"

def writeSymbolsToLibraryFiles(syms, dirname):
    """ Given a list of sym dictionaries
        Create kicad symbol library files in dirname
        Symbols will be sorted into files by prefix
        Library files will be created, or overwritten if exists
    """
    syms_sorted = {}
    for sym in syms:
        libfilename = deduceLibraryFilename(sym)
        sym['dst_lib'] = libfilename.replace(".lib","")
        try:
            syms_sorted[libfilename].append(sym)
        except:
            syms_sorted[libfilename] = [sym]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # src_libdat = readAllLibraries(dirname)
    cache_libdat = readCacheLib(dirname)
    if cache_libdat is None:
        print("ERROR: No cache library found in input dir "+ dirname + "! Cache filename must end in *-cache.lib")
        return

    for libfilename, symlist in syms_sorted.items():
        libdata = createLibFromCache(symlist, cache_libdat)
        writeLibFile(libdata, libfilename)
        print("Writing library file: "+libfilename)

def writeLibFile(libdata, libsym_filename):
    """ Write (create or append) the filename given by libsym_filename
        by writing the symbol data in libdata
    """
    fullpath = output_dir + "/" + libsym_filename
    if os.path.exists(fullpath):
        #append:
        with open(fullpath, "r+") as f:
           existing_lib = f.readlines()

        #remove end library marker
        if existing_lib[-1:] == ['#End Library']:
            existing_lib = existing_lib[:-1]

        with open(fullpath, "w") as f:
            for line in existing_lib:
                f.write(line)
            for data in libdata:
                f.write(data)
            f.write("#\n#End Library")
    else:
        #create:
        with open(fullpath, "w") as f:
            f.write("EESchema-LIBRARY Version 2.4\n#encoding utf-8\n")
            for data in libdata:
                f.write(data)
            f.write("#\n#End Library")

def exportSymbolListCSV(syms, csv_filename):
    row = '"ID","Old Library","New Library",\
            "Lib Footprint", "BOM Footprint",\
            "Footprint.3dshapes","Description",\
            "Value","References","Sch File",\
            "Manufacturer","Manufacturer_No","Documentation"\n'
    for sym in syms:
        if 'name' not in sym.keys():
            continue
        row = row + '"'
        row = row + sym[itemnum_field] + '","'
        row = row + sym['src_lib'] + ':' + sym['name'] + '","'
        row = row + sym['dst_lib'] + ':' + sym['formatted_name'] + '","'
        row = row + sym['sch_footprint'] + '","'
        row = row + sym['bom_footprint'] + '","'
        row = row + sym['fp3d'] + '","'
        row = row + sym[desc_field] + '","'
        row = row + sym['Value'] + '","'
        row = row + ",".join(sym['refslist']) + '","'
        row = row + sym['example_sheet'] + '","'
        row = row + sym[manu_field] + '","'
        row = row + sym[manuNo_field] + '","'
        row = row + sym['Documentation'] + '"'
        row = row + "\n"

    with open(csv_output_filename,"a+") as f:
        f.write(row)
    return

def createSymbolsFromBom(input_dir, csv_filename):
    symbol_list=[]
    field_list=[]
    refslist=[]

    schdat = loadFilesWithExt(input_dir, '.sch')

    projname = os.path.basename(os.path.normpath(input_dir))

    with open(csv_filename) as csvfile:
        print("Using bom csv file: "+csv_filename)
        reader = csv.DictReader(csvfile)
        while itemnum_header not in reader.fieldnames:
            reader = csv.DictReader(csvfile)
            if reader is None:
                print("FATAL ERROR: CSV file does not have correct column names (first two lines scanned)")
                quit()
        i=0
        for row in reader:
            itemnum = projname + row[itemnum_header]
            refs = row[refs_header]
            desc = row[desc_header]
            manu = row[manu_header]
            manuNo = row[manuNo_header]
            bom_footprint = row[footprint_header]
            # print("Parsing Row#"+str(i))
            i=i+1
            if len(itemnum) > 0:
                if len(refslist)>0 and len(refslist[0])>1:
                    print("Attempting to create new symbol based on refs: "+refslist[0])
                    symbol = createSymbol(refslist, field_list, schdat)
                    if symbol is not None:
                        symbol_list.append(symbol)
                print("Found new item number "+itemnum+" on row "+str(i))
                refslist = re.split(r',\s*', refs)
                field_list=[]

                field_list.append(("Footprint", bom_footprint, 2))
                field_list.append((itemnum_field, itemnum, 4))
                field_list.append((desc_field, desc, 5))
                field_list.append((manu_field, manu, 6))
                field_list.append((manuNo_field, manuNo, 7))
                f_idx = 8
                #field_list.append(('Manufacturer_Desc', manuDesc, 8))
                #f_idx = 9
                extras_idx = 2

            else:
                field_list.append((manu_field+str(extras_idx), manu, f_idx))
                field_list.append(('Part Number'+str(extras_idx), manuNo, f_idx+1))
                # field_list.append(('Manufacturer_Desc'+str(extras_idx), manuDesc, f_idx+2))
                extras_idx = extras_idx + 1
                f_idx = f_idx + 3

    #FixMe: get rid of this duplicate code hack to read last line
    if len(refslist)>0 and len(refslist[0])>1:
        print("Attempting to create new symbol based on refs: "+refslist[0])
        symbol = createSymbol(refslist, field_list, schdat)
        if symbol is not None:
            symbol_list.append(symbol)
    return symbol_list


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        if input_dir[:len(input_dir)-1] != "/":
            input_dir = input_dir+"/"
        print("Using input directory: "+input_dir)
        if len(sys.argv) > 2:
            bomcsv_filename = sys.argv[2]
            print("Will look for bom file: " + bomcsv_filename)
        else:
            bomcsv_filename = input_dir+default_bom_filename
            print("No bom file specified, looking for " + bomcsv_filename)

        syms = createSymbolsFromBom(input_dir, bomcsv_filename)
        syms = formatCommonSymNames(syms)
        syms = makeUniqueNames(syms)
        writeSymbolsToLibraryFiles(syms, input_dir)
        print("Exporting CSV file:"+csv_output_filename)
        exportSymbolListCSV(syms, csv_output_filename)
    else:
        print("""
Please specify an input dir with .sch files and a *-cache.lib file.
The default BOM file name is input_dir/bom.csv
You can specify a different BOM file with the second argument.

The project name is taken from the first argument.

Example:
$ python3 bom2libsym.py ../myProjectFolder ../myBOMs/projectBOM.csv

**********************************************************************
Usage:

$ python3 bom2libsym.py ../myProjectFolder/ ../myBOMs/myProjectBOM.csv
$ ls Symbols/
$
$ # You can append multiple projects to the same library files:
$ python3 bom2libsym.py ../anotherProject/ ../myBOMs/anotherBOM.csv
$

Then from within Kicad, add the new symbol libraries to the project:
   Preferences > Manage Symbol Libraries > Project Specific Libraries
**********************************************************************

This script will scan a BOM csv file. For each line with an Item Number and Ref
Des (in a list like "R1, R68, R124"), it will scan all *.sch files in the given
input dir to find those components. Then it will take the library symbol name
used by the schematic for that ref des, and copy the library symbol data from
the library.  All .lib files must be in the given input dir (including standard
Kicad libraries, if any parts are using those) Then it adds the Manufacturer,
Manufacturer_No, Item Number, etc. data from the BOM to the new library symbol.
For resistors and capacitors, it will try to guess the value, voltage,
tolerance, and footprint and name the symbol accordingly. It also will make
sure all symbol names are unique by appending the Item Number as the suffix
(e.g.  FUSE_123456789).  The symbols are sorted by reference prefix and saved
into libraries in the Symbol/ directory. Some special names for libraries are
deduced, such as R => Resistor.lib, others will just be PREFIX.lib.  Libraries
are appended! So if you need to re-do a project, erase the Symbol dir.

Finally, a csv file is output into the Symbol dir. It's also appended, so
delete it if you re-do a project.

You can set the headings of the BOM file at the top of this script. You also
might just consider renaming your BOM

Todo: Create unique names for symbols with same name from different projects
Workaround: Open library in kicad, accept warning about duplicate names, save library.

Todo: Preserve ALIAS (remove current symbol from list, though)
Workaround: Paste ALIAS field back into lib file, if needed.

Todo: Ensure correct cache-lib is chosen, or else print error and quit
Workaround: Do not have multiple files in a project dir ending in -cache.lib

""")

