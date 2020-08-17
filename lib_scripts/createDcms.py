import os
import sys
import re
from fileUtil import *
from bom2libsym import extractFieldFromLibSymbol, extractFieldFromLibSymbolByNum

#These are the symbol library field names to copy to the dcm file:
keyword_field_name = "Item Number"
description_field_name = "Description"
datasheet_field_idx = 3

dcm_header = "EESchema-DOCLIB  Version 2.0\n#\n"
dcm_footer = "#End Doc Library"

def removeExt(name):
    return os.path.splitext(name)[0]

def dcmToLib(name):
    return removeExt(name) + ".lib"

def libToDcm(name):
    return removeExt(name) + ".dcm"

def createDcmsThatDontExist(lib_dict, dcm_dict):
    for libname in lib_dict.keys():
        dcmname = libToDcm(libname)
        if dcmname not in dcm_dict.keys():
            dcm_dict[dcmname] = createEmptyDcm(dcmname)
    return dcm_dict
        
def createEmptyDcm(libname):
    global dcm_footer
    global dcm_header
    return dcm_header + dcm_footer

def addAllSymbolsToDcms(libs_dict, dcm_dict):
    for libname, libdata in libs_dict.items():
        dcmname = libToDcm(libname)
        print("Populating "+dcmname)
        dcm_dict[dcmname] = populateDcm(libdata, dcm_dict[dcmname])
    return dcm_dict

def populateDcm(libdata, dcmdata):
    symbols = getSymbolList(libdata)
    if len(symbols) == 0:
        print("Warning: no symbols found in library")
    for sym in symbols:
        dcm_fields = extractDcmFields(sym)
        if symbolExistsInDcm(dcm_fields['SymbolName'], dcmdata):
            print("Updating "+dcm_fields['SymbolName']+" in dcm file")
            dcmdata = updateDcm(dcm_fields, dcmdata)
        else:
            print("Inserting "+dcm_fields['SymbolName']+" into dcm file")
            dcmdata = insertIntoDcm(dcm_fields, dcmdata)

    return dcmdata

def getSymbolList(libdata):
    symlist = re.findall(r'(^DEF .*?^ENDDEF)', libdata, flags=re.MULTILINE | re.DOTALL)
    return symlist

def symbolExistsInDcm(symname, dcmdata):
    e_symname = re.escape(symname)
    findName = re.search(r'^\$CMP '+e_symname+r'\n', dcmdata, flags=re.MULTILINE)
    return (findName is not None)

def updateDcm(dcm_fields, dcmdata):
    dcm_entry = getDcmEntry(dcm_fields['SymbolName'], dcmdata)
    if len(dcm_entry) == 0:
        print("Error: symbol "+dcm_fields['SymbolName']+" was found in dcm file but could not be updated.")
        return dcmdata
    dcm_entry = updateOrInsertDcmField('D', dcm_entry, dcm_fields['Description'])
    dcm_entry = updateOrInsertDcmField('K', dcm_entry, dcm_fields['Keywords'], prepend=True)
    dcm_entry = updateOrInsertDcmField('F', dcm_entry, dcm_fields['Datasheet'])
    
    dcmdata = replaceDcmEntry(dcm_fields['SymbolName'], dcm_entry, dcmdata)
    return dcmdata

def dcmFieldExists(fieldprefix, entry):
    m = re.findall(r'\n'+fieldprefix+r' ', entry)
    if len(m)>0:
        return true
    else:
        return false

def updateOrInsertDcmField(fieldprefix, entry, newdata, prepend=False):
    entry, numfound = updateDcmField(fieldprefix, entry, newdata, prepend)
    if numfound == 0:
        entry, numfound = insertDcmField(fieldprefix, entry, newdata)
        if numfound == 0:
            print("Error: symbol was found in dcm file but new field \""+fieldprefix+" "+newdata+"\" could not be inserted.")
    return entry

def updateDcmField(fieldprefix, entry, newdata, prepend=False):
    if prepend and len(newdata)>0:
        newentry, num = re.subn(r'\n'+fieldprefix+r' (.*?)\n', r'\n'+fieldprefix+r' '+newdata+r', \1\n', entry)
    else:
        newentry, num = re.subn(r'\n'+fieldprefix+r' (.*?)\n', r'\n'+fieldprefix+r' '+newdata+r'\n', entry)
    return newentry, num

def insertDcmField(fieldprefix, entry, newdata):
    newentry, num = re.subn(r'\n\$ENDCMP', r'\n'+fieldprefix+r' '+newdata+r'\n$ENDCMP', entry)
    return newentry, num

def insertIntoDcm(dcm_fields, dcmdata):
    global dcm_footer
    dcmtxt = createDcmText(dcm_fields)
    dcmdata = stripDcmFooter(dcmdata)
    dcmdata += dcmtxt 
    dcmdata += dcm_footer
    return dcmdata

def stripDcmFooter(s):
    global dcm_footer
    return s[:s.rfind(dcm_footer)]

def getDcmEntry(symname, dcmdata):
    m = re.search(r'(^\$CMP '+symname+r'\n.*?^\$ENDCMP)', dcmdata, flags=re.MULTILINE | re.DOTALL)
    try:
        entry = m.group(1)
    except:
        entry = ""
    return entry

def replaceDcmEntry(symname, replacement_entry, dcmdata):
    dcmdata, num = re.subn(r'(^\$CMP '+symname+r'\n.*?^\$ENDCMP)', replacement_entry, dcmdata, flags=re.MULTILINE | re.DOTALL)
    return dcmdata

def extractDcmFields(sym):
    fields = {}
    fields['Description'] = extractFieldFromLibSymbol(description_field_name, sym)
    fields['Keywords'] = itemnum = extractFieldFromLibSymbol(keyword_field_name, sym)
    fields['Datasheet'] = extractFieldFromLibSymbolByNum(datasheet_field_idx, sym)
    fields['SymbolName'] = getSymbolName(sym)
    return fields

def getSymbolName(symdata):
    m = re.search(r'^DEF (.*?) .*$', symdata, flags=re.MULTILINE)
    try:
        symname = m.group(1)
    except:
        symname = ""
    return symname

def createDcmText(dcm_fields):
    if len(dcm_fields['SymbolName']) == 0:
        print("Error: No Symbol Name")
        return ""
    txt = "$CMP "+dcm_fields['SymbolName']+"\n"

    if len(dcm_fields['Description']) > 0:
        txt += "D "+dcm_fields['Description']+"\n"

    if len(dcm_fields['Keywords']) > 0:
        txt += "K "+dcm_fields['Keywords']+"\n"

    if len(dcm_fields['Datasheet']) > 0:
        txt += "F "+dcm_fields['Datasheet']+"\n"
    
    txt += "$ENDCMP\n#\n"
    return txt

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lib_dir = appendSlash(sys.argv[1])
        print("Using Library directory: "+lib_dir)

        libs_dict = loadFilesWithExt(lib_dir, '.lib')
        dcm_dict = loadFilesWithExt(lib_dir, '.dcm')
        dcm_dict = createDcmsThatDontExist(libs_dict, dcm_dict)
        dcm_dict = addAllSymbolsToDcms(libs_dict, dcm_dict) 
        writeFiles(dcm_dict)

    else:
        print("""
        Usage: python3 createDcms.py ../SymbolDirectory

        Reads all kicad library files (.lib) in a the given directory,
        and extracts the Item Number, 
        """)

