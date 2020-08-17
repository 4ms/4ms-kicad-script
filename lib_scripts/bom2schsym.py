# Usage:
# cd bom_script/
# cp ../*.sch ./
# python3 bom2schsym.py
# cp *.sch ../*.sch
#
# Use at your own risk!

# Some user-configurable stuff
# Set the filename for the bom here:
bomcsv_filename = 'bom.csv'

# Set the column names found in the bom file here:
itemnum_header = 'Item Number'
refs_header = 'Ref Des'
desc_header = 'Item Description'
manu_header = 'Mfr. Name'
manuNo_header = 'Mfr. Part Number'
manuDesc_header = 'Mfr. Part Description'

import os
import csv
import re

sch_files = [f for f in os.listdir('.') if f.endswith('.sch')]

def loadAllSchDat():
    schdat = {}
    for sch in sch_files:
        with open(sch) as f:
            print("Reading file: "+sch)
            schdat[sch] = f.read()
    return schdat

def writeSchDatToFiles(schdat):
    for sch in schdat:
        with open(sch, "w") as f:
            print("Writing file: "+sch)
            f.write(schdat[sch])

def findRefInSchdat(ref, schdat):
    regex = re.compile(r'\nL ([^ ]*) ' + ref + r'\n')
    matching_sch = None
    for sch in schdat:
        print("Searching in "+sch)
        hit = regex.findall(schdat[sch])
        if len(hit) > 0:
            matching_sch = sch
            #Todo: report an error if len(hit)>1
            break
    return matching_sch

def findXYPos(ref, filetext):
    m = re.search(r'\nL .*? '+ref+r'\n.*?\nP ([\d]+) ([\d]+)\n', filetext, re.MULTILINE)
    if m is not None:
        return (m.group(1), m.group(2))
    else:
        return None

def addFieldToSymInSch(ref, lines_to_insert, filetext):
    x,y = findXYPos(ref, filetext)
    xy_lines = re.sub(r'(&X&) (&Y&)', x+' '+y, lines_to_insert)
    newfile, numfound = re.subn(r'(\nL .*? '+ref+r'\n.*?)\n(\s+[\d-].*?\n\s+[\d-].*?\n\$EndComp)', r'\1\n' + xy_lines + r'\2', filetext, re.MULTILINE, re.DOTALL)
    return (newfile, numfound)

def addFieldsToAllRefs(refslist, schlines, schdat):
    for ref in refslist:
        if len(ref)==0:
            print("Ref is blank")
            continue

        found_sch = findRefInSchdat(ref, schdat)
        if found_sch is None:
            print("Ref not found in any .sch file")
            continue

        newfiletext, numfound = addFieldToSymInSch(ref, schlines, schdat[found_sch])
        if numfound>0:
            print("Found "+ref+" in file "+found_sch)
            schdat[found_sch] = newfiletext
        else:
            print("Not Found: "+ref)

    return schdat

def mergeBomIntoSch():
    schlines=""
    sch_tags = "H &X& &Y& 50  0001 C CNN"
    #lib_tags = "0 0 50 H I C CNN"
    refslist=[]

    schdat = loadAllSchDat()
    csvfile = open(bomcsv_filename)
    print("Using bom csv file: "+bomcsv_filename)
    reader = csv.DictReader(csvfile)
    i=0
    for row in reader:
        itemnum = row[itemnum_header]
        refs = row[refs_header]
        desc = row[desc_header]
        manu = row[manu_header]
        manuNo = row[manuNo_header]
        manuDesc = row[manuDesc_header]
        # print("Parsing Row#"+str(i))
        i=i+1
        if len(itemnum) > 0:
            if len(refslist)>0:
                print("Adding fields to schematic:")
                print(refslist)
                print(schlines)
                schdat = addFieldsToAllRefs(refslist, schlines, schdat)

            print("Found new item number "+itemnum+" on row "+str(i))
            schlines = ""
            refslist = re.split(r',\s*', refs)
            extras_idx = 2
            f_num = 8

            schlines = schlines + "F 4 \""+desc+"\" "+ sch_tags + " \"Description\"" + "\n"
            schlines = schlines + "F 5 \""+itemnum+"\" "+ sch_tags + " \"Item Number\"" + "\n"
            schlines = schlines + "F 6 \""+manu+"\" "+ sch_tags + " \"Manufacturer\"" + "\n"
            schlines = schlines + "F 7 \""+manuNo+"\" "+ sch_tags + " \"Manufacturer_No\"" + "\n"
            schlines = schlines + "F 8 \""+manuDesc+"\" "+ sch_tags + " \"Manufacturer_Desc\"" + "\n"

        else:
            schlines = schlines + "F "+str(f_num+1)+" \""+manu+"\" "+ sch_tags + " \"Manufacturer"+str(extras_idx)+"\"" + "\n"
            schlines = schlines + "F "+str(f_num+2)+" \""+manuNo+"\" "+ sch_tags + " \"Manufacturer_No"+str(extras_idx)+"\"" + "\n"
            schlines = schlines + "F "+str(f_num+3)+" \""+manuDesc+"\" "+ sch_tags + " \"Manufacturer_Desc"+str(extras_idx)+"\"" + "\n"
            extras_idx = extras_idx + 1
            f_num = f_num + 3

    return schdat


##main
new_sch_filedat = mergeBomIntoSch()
writeSchDatToFiles(new_sch_filedat)
