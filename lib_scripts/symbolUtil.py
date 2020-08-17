import re

lib_tags = "&X& &Y& 50 H I L CNN"
display_lib_tags = "&X& &Y& 50 V V C CNN"

def getRefPrefix(ref):
    prefix = ""
    for c in ref:
        if c.isalpha():
            prefix += c
        else:
            break
    return prefix

def checkSymbolNeedsUpdating(symbol_name, field_name, field_val, field_idx, libfiledata):
    e_symbol = re.escape(symbol_name)
    e_name = re.escape(field_name)
    e_val = re.escape(field_val)
    if field_idx<4:
        m = re.findall(
                r'^DEF '+e_symbol+r' .*(?:\n(?!ENDDEF).*)+\nF ?'+str(field_idx)+r' "'+e_val+r'" .*\n',
                libfiledata, flags=re.MULTILINE)
    else:
        m = re.findall(
                r'^DEF '+e_symbol+r' .*(?:\n(?!ENDDEF).*)+\nF ?\d+ "'+e_val+r'" .* "'+e_name+r'"\n',
                libfiledata, flags=re.MULTILINE)
    if len(m) == 0:
        return True
    else:
        return False

def updateSymbolField(symbol_name, field_name, field_val, field_idx, libfiledata):
    """ Substitute the given field value for a given symbol
        with the given name in libfiledata
    """
    if field_idx<4:
        libfiledata, num = updateUnnamedSymbolField(symbol_name, field_val, field_idx, libfiledata)
        print("Updated "+str(num)+" times")
        return libfiledata, num

    e_symbol = re.escape(symbol_name)
    e_name = re.escape(field_name)
    libfiledata, num = re.subn(
            r'^(DEF '+e_symbol+r' .*(?:\n(?!ENDDEF).*)+\nF ?\d+ ")[^"]*(" .* "'+e_name+r'"\n)',
            r'\g<1>'+field_val+r'\g<2>',
            libfiledata, flags=re.MULTILINE)
    return libfiledata, num

def updateUnnamedSymbolField(symbol_name, field_val, field_idx, libfiledata):
    if field_idx>=4:
        return libfiledata, 0
    e_symbol = re.escape(symbol_name)
    libfiledata, num = re.subn(
            r'^(DEF '+e_symbol+r' .*(?:\n(?!ENDDEF).*)+\nF ?'+str(field_idx)+r') ".*?" ',
            r'\g<1> "'+field_val+r'" ',
            libfiledata, flags=re.MULTILINE)
    #print("Updated "+str(num)+" times, unnamed symbol field "+str(field_idx)+" to "+field_val)
    return libfiledata, num

def insertSymbolField(symbol_name, field_name, field_val, field_idx, libfiledata):
    """ Insert a field into a symbol within a library
    """
    if field_name=="Datasheet":
        return insertSymbolFieldByNum(symbol_name, field_val, field_idx, libfiledata)

    e_symbol = re.escape(symbol_name)
    field_txt = createFieldText(field_name, field_val, field_idx)
    libfiledata, num = re.subn(
            r'^(DEF '+e_symbol+r' .*(?:\nF.*)+\n)',
            r'\1'+field_txt,
            libfiledata, flags=re.MULTILINE)
    return libfiledata, num

def insertSymbolFieldByNum(symbol_name, field_val, field_idx, libfiledata):
    """ Insert an unnamed field (F0 - F3) into a symbol within a library
    """
    if field_idx>=4:
        return libfiledata, 0
    e_symbol = re.escape(symbol_name)
    field_txt = createUnnamedFieldText(field_val, field_idx)
    libfiledata, num = re.subn(
            r'^(DEF '+e_symbol+r' .*(?:\nF.*)+\n)',
            r'\1'+field_txt,
            libfiledata, flags=re.MULTILINE)
    return libfiledata, num

def createFieldText(field_name, field_val, field_idx):
    lib_tags = "400 50 50 H I L CNN"
    field_text = "F"+str(field_idx)+" \""+field_val+"\" "+ lib_tags + " \""+field_name+"\"\n"
    return field_text

def createUnnamedFieldText(field_val, field_idx):
    lib_tags = "400 50 50 H I L CNN"
    field_text = "F"+str(field_idx)+" \""+field_val+"\" "+ lib_tags + "\n"
    return field_text

def cleanupFieldText(txt):
    txt_cleaned = txt.replace("\n","")
    txt_cleaned = txt_cleaned.replace("\"","")
    return txt_cleaned

# class Field():
#     def __init__(self):
#         self.name = ''
#         self.val=''
#         self.idx=-1
#         self.x=-150
#         self.y=-250
#         self.vis=False

# def createFieldTextFromList(field_obj_list):
#     field_text = ""
#     x_pos = -100
#     y_pos = -250
#     y_offset = -60
#     for fld in field_list:
#         if fld.name 

def createAllFieldText(field_list):
    field_text = ""
    x_pos = -100
    y_pos = -250
    y_offset = -60
    last_idx = 3
    for field_name, field_val, field_idx in field_list:
        if field_idx == -1:
            field_idx = last_idx + 1
        elif field_idx<4:
            continue
        print(field_name+" = "+field_val)
        field_val = cleanupFieldText(field_val)
        field_name = cleanupFieldText(field_name)
        if "Display" in field_name:
            field_attr = display_lib_tags
            field_attr = re.sub(r'(&Y&)', str(0), field_attr)
            field_attr = re.sub(r'(&X&)', str(150), field_attr)
        else:
            field_attr = lib_tags
            field_attr = re.sub(r'(&Y&)', str(y_pos), field_attr)
            field_attr = re.sub(r'(&X&)', str(x_pos), field_attr)
            y_pos = y_pos + y_offset
        field_text = field_text + "F "+str(field_idx)+" \""+field_val+"\" "+ field_attr + " \""+field_name+"\"\n"

        last_idx = field_idx
    return field_text

def renameSymbol(oldname, newname, symdata):
    if oldname is not newname:
        e_oldname = re.escape(oldname)
        symdata = re.sub(r'\n# '+e_oldname+r'\n', r'\n# '+newname+r'\n', symdata)
        symdata = re.sub(r'\nDEF '+e_oldname+r' ', r'\nDEF '+newname+r' ', symdata)
        symdata = re.sub(r'\nF ?1 ".*?" ', r'\nF1 "'+newname+r'" ', symdata)
    return symdata

def extractSymFromLib(part_name, lib_text):
    """ Given a symbol name and text of a library file,
        Return the kicad library-format symbol data
    """
    e_part_name = re.escape(part_name)
    m = re.search(
            r'(#\n# '+e_part_name+r'\n#\nDEF '+e_part_name+ r' .*?\nENDDEF\n)',
            lib_text,
            re.MULTILINE | re.DOTALL)
    try: symdat = m.group()
    except: symdat = None
    return symdat

def extractFieldValFromSchSymbol(ref, fieldnum, schdat):
    if fieldnum==0:
        return ref
    m = re.search(r'^F ?0 "'+ref+r'" .*(?:\nF ?\d+.*)*?\nF ?'+str(fieldnum)+r' "([^"]*)" ', schdat, re.MULTILINE)
    if m is None: return ""
    else: return m.group(1)

def fieldTextToAttributeList(field_text):
    attr_list = shlex.split(field_text, posix=False)
    return attr_list

def setFieldAttr(attr_idx, attr_val, field_text):
    """ Given the text of a library symbol 
        Make the field invisible.
        If field_name is "", then the field_num is used instead
    """
    try:
        attr_list = fieldTextToAttributeList(field_text)
        attr_list[attr_idx] = attr_val
        return ' '.join(attr_list)
    except:
        print("Could not set field attribute index "+str(attr_idx)+" to "+attr_val)
        return fld

def makeFieldInvisble(field_text):
    setFieldAttr(6, 'I', field_text)

def makeFieldVisble(field_text):
    setFieldAttr(6, 'V', field_text)

# def makeLibSymbolFieldInvisible(field_num, field_name, libsymbol_text):
#     fld = extractFieldFromLibSymbol(field_num, field_name, libsymbol_text)
    
def makeFieldInvisibleInSymText(field_num, field_name, libsymbol_text):
    #todo: field_name
    if field_num < 4:
        libsymbol_text = re.sub(r'^(F ?'+str(field_num)+r' .*? [HV]) [IV] ([CLR] [CLR]NN)$', 
                r'\1 I \2',
                libsymbol_text, flags=re.MULTILINE)
        return libsymbol_text

def extractFieldFromLibSymbol(field_num, field_name, libsymbol_text):
    fld = None
    if len(field_name) > 0:
        fld = extractFieldValFromLibSymbol(field_name, libsymbol_text)
    elif field_num < 4:
        fld = extractFieldValFromLibSymbolByNum(field_num, libsymbol_text)
    return fld

def extractFieldValFromLibSymbolByNum(field_num, libsymbol_text):
    m = re.search(r'\nF ?'+str(field_num)+r' "(.*?)" ', libsymbol_text)
    if m is None: return ""
    else: return m.group(1)

def extractFieldValFromLibSymbol(field_name, libsymbol_text):
    m = re.search(r'^F ?[\d]+ "(.*?)" .* "'+field_name+r'"$', libsymbol_text, flags=re.MULTILINE)
    if m is None: return ""
    else: return m.group(1)

def removeExtraFields(symdat):
    """ Given library-format symbol data,
        Remove fields F4 and up, and ALIAS field
    """
    symdat = re.sub(r'(?m)^F ?(?:[456789]|(?:\d\d)) .*\n','',symdat)
    symdat = re.sub(r'(?m)^ALIAS .*\n','',symdat)
    return symdat

