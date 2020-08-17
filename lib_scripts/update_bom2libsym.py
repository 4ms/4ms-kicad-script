# This script is barely tested, and not meant for public use.
# Use at your own risk!

default_library_dir = '../Symbols'
log_dir = 'logs/'
csv_output_filename = log_dir+'update_library_bom.csv'

default_bom_filename = 'bom.csv'

# Set the column names found in the bom file here:
itemnum_header = 'Item Number'
datasheet_header = 'Link to datasheet'
desc_header = 'Item Description'
manu_header = 'Mfr. Name'
manuNo_header = 'Mfr. Part Number'

import os
import sys
import csv
import re
from bom2libsym import pullFieldFromList
from fileUtil import *
from symbolUtil import *
notfound = []

def extractFieldsFromBoms(bom_dir):
    field_dict={}
    bom_filenames = [bom_dir+f for f in os.listdir(bom_dir) if f.endswith('.csv')]
    for bom_filename in bom_filenames:
        with open(bom_filename) as csvfile:
            print("----------")
            print("Using bom csv file: "+bom_filename)
            reader = csv.DictReader(csvfile)
            if itemnum_header not in reader.fieldnames:
                reader = csv.DictReader(csvfile)
            if itemnum_header not in reader.fieldnames:
                print("FATAL ERROR: CSV file does not have correct column names (first two lines scanned)")
                break
            i=0
            field_list = []
            lastline = False
            while not lastline:
                try:
                    row = next(reader)
                    itemnum = row[itemnum_header]
                    desc = row[desc_header]
                    manu = row[manu_header]
                    manuNo = row[manuNo_header]
                    datasheet = row[datasheet_header]
                except StopIteration:
                    lastline = True

                i=i+1
                if lastline or len(itemnum) > 0:
                    if len(field_list)>0:
                        found_duplicate_itemnum = False
                        try:
                            other_field_list = field_dict[last_itemnum]['fields']
                            other_filename = field_dict[last_itemnum]['filename']
                            found_duplicate_itemnum = True
                        except KeyError:
                            field_dict[last_itemnum] = {}
                            field_dict[last_itemnum]['filename'] = bom_filename
                            field_dict[last_itemnum]['fields'] = field_list
                            #print("Extracted fields for Item Number: "+last_itemnum + " ("+bom_filename+")")

                        if found_duplicate_itemnum:
                            print("**Item Number "+last_itemnum+" found in file: "+bom_filename+" and in file: "+other_filename)
                            diffs=""
                            other_flds = {}
                            for fld,val, num in other_field_list:
                                other_flds[fld] = val
                            this_flds = {}
                            this_longer = 0
                            for fld,val, num in field_list:
                                try:
                                    other_val = other_flds[fld]
                                except:
                                    other_val = "(blank)"

                                if other_val == val:
                                    continue
                                else:
                                    if len(val) > len(other_val):
                                        this_longer += 1
                                    else:
                                        this_longer -= 1
                                    diffs += "\t"+fld +", \""+ val +"\", \""+ other_val+"\"\n"
                            if len(diffs) > 0:
                                if (this_longer>0):
                                    print("<<Differences found, the entry in "+bom_filename+" has more fields which are longer, so using it")
                                    field_dict[last_itemnum] = {}
                                    field_dict[last_itemnum]['filename'] = bom_filename
                                    field_dict[last_itemnum]['fields'] = field_list
                                else:
                                    print(">>Differences found, the entry in "+other_filename+" has more fields which are longer, so using it")

                                print("\tField, "+bom_filename+", "+other_filename)
                                print(diffs)


                    print("Found Item Number: "+itemnum+" in file "+bom_filename+" on row "+str(i))
                    last_itemnum = itemnum
                    last_bom_filename = bom_filename
                    field_list = []
                    field_list.append(('Datasheet', datasheet, 3))
                    field_list.append(('Description', desc, 5))
                    field_list.append(('Manufacturer', manu, 6))
                    field_list.append(('Manufacturer_No', manuNo, 7))
                    f_idx = 8
                    extras_idx = 2

                else:
                    field_list.append(('Manufacturer'+str(extras_idx), manu, f_idx))
                    field_list.append(('Manufacturer_No'+str(extras_idx), manuNo, f_idx+1))
                    extras_idx = extras_idx + 1
                    f_idx = f_idx + 3

    return field_dict

def updateSymbolLibrary(field_dict, libs_dict):
    for itemnum, d in field_dict.items():
        fields = d['fields']
        for field_name, field_val, field_idx in fields:
            updateOrInsertField(itemnum, field_name, field_val, field_idx, libs_dict)
    return libs_dict

def updateOrInsertField(itemnum, field_name, field_val, field_idx, libs_dict):
    global notfound
    lib, symbol_name = findSymbolByItemnum(itemnum, libs_dict)
    if lib is None:
        if itemnum not in notfound:
            print("****ERROR****: Item Number: "+itemnum+" not found in any libraries")
            print("**** (not found: "+itemnum+") "+field_name+" = "+field_val)
            notfound.append(itemnum)
        else:
            print("**** (not found: "+itemnum+") "+field_name+" = "+field_val)
        return False

    if field_idx<3:
        return False

    if checkSymbolNeedsUpdating(symbol_name, field_name, field_val, field_idx, libs_dict[lib]):
        libs_dict[lib], num = updateSymbolField(symbol_name, field_name, field_val, field_idx, libs_dict[lib])
        if num > 1:
            print("ERROR: Symbol "+symbol_name+" found more than once in a single library file " + lib)
        if num > 0:
            print("Updated field "+field_name+" = "+field_val+ " into symbol "+symbol_name+" in library "+lib+".")
        elif field_val!="" and field_name!="":
            libs_dict[lib], num = insertSymbolField(symbol_name, field_name, field_val, field_idx, libs_dict[lib])
            if num>0:
                print("Inserted field "+field_name+" = "+field_val+ " into symbol "+symbol_name+" in library "+lib+".")
            else:
                print("ERROR: could not insert field "+field_name+" = "+field_val+ " into symbol "+symbol_name+" in library "+lib+".")
        else:
            print("Can't update")
    
    return True


def findSymbolByItemnum(itemnum, libs_dict):
    """ Given an Item Number and library data dict
        Return the name of the library it's found in, and the symbol name
    """
    e_itemnum = re.escape(itemnum)
    for libname, dat in libs_dict.items():
        m = re.search(r'^DEF ([^ ]*) .*(?:\n[^\$].+)+\nF ?\d+ "'+e_itemnum+r'".* "Item Number"\n', dat, re.MULTILINE)
        try:
            symname = m.group(1)
            return libname, symname
        except:
            continue
    return None, None


if __name__ == "__main__":
    if len(sys.argv) > 2:
        boms_dir = appendSlash(sys.argv[1])
        print("Using BOM directory: "+boms_dir)
        libs_dir = appendSlash(sys.argv[2])
        print("Will update symbol library files in: "+libs_dir)

        flds = extractFieldsFromBoms(boms_dir)
        libs_dict = loadFilesWithExt(libs_dir, '.lib')
        libs_dict = updateSymbolLibrary(flds, libs_dict)
        writeFiles(libs_dict)

        if len(notfound)>0:
            print("")
            print("The following item numbers were not found in any libraries. You must correct this, or manually create new library symbols:")
            for nf in notfound:
                filen = os.path.basename(flds[nf]['filename'])
                fl = flds[nf]['fields']
                desc = pullFieldFromList(fl, "Description")
                print(nf +", "+ filen + ", "+ desc)

    else:
        print("""
Please specify a dir with BOM csv files, and a symbol library dir.

**********************************************************************
Usage:
$ python3 update_bom2libsym.py csvBOMs/ ../SymbolLibraryDir/
**********************************************************************

This script will scan all csv files in the given directory. For each group of
lines beginning with an Item Number, it will search for that Item Number in all
.lib files in the SymbolLibraryDir. Then it will update or insert the
Description, Datasheet, and Manufacturer*, Manufacturer_No*, fields in the lib
file.

After running this script, to apply changes to schematics, you must run "Update
Fields from Library" in Kicad schematic editor. It's recommended to check all
fields except uncheck Reference, Value, and Footprint and any Manufacturer#
fields with # higher than 2.  Also consider checking "Reset fields which are
empty in library".

""")

