import re
using_rkm = True
format_in_rkm = False

if using_rkm or format_in_rkm:
    from rkm_codes import *

commonSymbolNamePrefixes = ['C', 'R', 'L']
commonSymbolFootprints = ['0402', '0603', '0805', '1206', '1210', '1212', '0612', '2010', '2512', '2616']
commonTempCoefs = ['C0G', 'NP0', 'X5R', 'X7R', 'X7S']

def deduceCapValue(description):
    m = re.search(r'[\d\.]+ ?[NnUuPp]F', description)
    try:
        guessedValue = m.group(0)
    except:
        guessedValue = ""
    return guessedValue

def deduceResValue(description):
    m = re.search(r'[\d\.]+ ?(?:[KkMmR]|(?:OHM))[\d]*', description)
    try:
        guessedValue = m.group(0)
    except:
        guessedValue = ""
    return guessedValue

def deduceIndValue(description):
    m = re.search(r'[\d\.]+ ?uH', description)
    try:
        guessedValue = m.group(0)
    except:
        guessedValue = ""
    return guessedValue

def correctCapitalization(value):
    val = value
    val = val.replace("K","k")
    val = val.replace("r","R")
    val = val.replace("N","n")
    val = val.replace("U","u")
    val = val.replace("µ","u")
    val = val.replace("P","p")
    val = val.replace("f","F")
    return val

def deduceSymbolName(name, description, sym_footprint=""):
    if name[0] not in commonSymbolNamePrefixes:
        return ""

    if name[0]=='C':
        value = deduceCapValue(description)
    elif name[0]=='R':
        value = deduceResValue(description)
    elif name[0]=='L':
        value = deduceIndValue(description)
    else:
        return name

    if value=="":
        return name

    try:
        #Value
        if format_in_rkm:
            fixed_value = value.replace("P", "p") #Commonly we write PF to mean pico-Farad not Peta-Farad
            fixed_value = fixed_value.replace("F", "")
            fixed_value = fixed_value.replace("OHM", "R")
            val = to_rkm(fixed_value, prec=2, strip_code=False)
            val = correctCapitalization(val)
            if "F" in value:
                val = val + "F"
        elif using_rkm:
            val = correctCapitalization(value)
            val = str(from_rkm(to_rkm(val, prec=2, strip_code=False)))
            val = val.replace(" d", "") #Odd artifact when value is just 1 to 3 digits
            if "F" in value:
                val = val + "F"
        else:
            val = correctCapitalization(value)

        #Footprint
        footprint=""
        for fp in commonSymbolFootprints:
            if description.find(fp) > -1 or sym_footprint.find(fp) > -1:
                footprint = "_"+fp
                break

        #Voltage
        m = re.search(r'[ ,]([\d]+[\.]?[\d]*V)[, $]',description)
        try:
            voltage = "_"+m.group(1)
        except:
            voltage = ""

        #Tolerance
        tolerance = ""
        if name[0] == 'R':
            m = re.search(r'[\d]+\.?[\d]*\%', description)
            try:
                tolerance = "_"+m.group(0)
            except:
                tolerance = ""

        #Wattage
        wattage = ""
        if name[0] == 'R':
            m = re.search(r'[ ,]([\d]+[\.]?[\/]?[\d]*W)[, $]',description)
            try:
                wattage = "_"+m.group(1)
            except:
                wattage = ""

        #TempCoef
        tempcoef = ""
        for tc in commonTempCoefs:
            if description.find(tc)>-1:
                tempcoef = "_"+tc
                break

        #hide most common values (default)
        # if footprint=="_0603":
        #     footprint = ""

        # if name[0] == 'C' and voltage == '_50V':
        #     voltage = ""

        if tolerance == "_1%":
            tolerance = ""

        if wattage == '_1/10W' or wattage == '_0.1W':
            wattage = ""

        tempcoef = ""

        formatted_value = val + footprint + voltage + tempcoef + wattage + tolerance
        #formatted_value = val + voltage + tempcoef + wattage + tolerance + footprint
        # print("Value "+value+" formatted to "+formatted_value)
        return formatted_value
    except:
        # print("Not able to deduce a symbol Value for name="+name+", Desc="+description)
        return name

