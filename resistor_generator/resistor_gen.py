import sys

E96_base_values = [
    1.00, 1.02, 1.05,
    1.07, 1.10, 1.13,
    1.15, 1.18, 1.21,
    1.24, 1.27, 1.30,
    1.33, 1.37, 1.40,
    1.43, 1.47, 1.50,
    1.54, 1.58, 1.62,
    1.65, 1.69, 1.74,
    1.78, 1.82, 1.87,
    1.91, 1.96, 2.00,
    2.05, 2.10, 2.16,
    2.21, 2.26, 2.32,
    2.37, 2.43, 2.49,
    2.55, 2.61, 2.67,
    2.74, 2.80, 2.87,
    2.94, 3.01, 3.09,
    3.16, 3.24, 3.32,
    3.40, 3.48, 3.57,
    3.65, 3.74, 3.83,
    3.92, 4.02, 4.12,
    4.22, 4.32, 4.42,
    4.53, 4.64, 4.75,
    4.87, 4.99, 5.11,
    5.23, 5.36, 5.49,
    5.62, 5.76, 5.90,
    6.04, 6.19, 6.34,
    6.49, 6.65, 6.81,
    6.98, 7.15, 7.32,
    7.50, 7.68, 7.87,
    8.06, 8.25, 8.45,
    8.66, 8.87, 9.09,
    9.31, 9.53, 9.76,
]

#Values in E24 that aren't also in E96
extra_E24_base_values = [
    1.20, 1.60, 1.80, 
    2.20, 2.40, 2.70, 
    3.00, 3.30, 3.60, 
    3.90, 4.30, 4.70, 
    5.10, 5.60, 6.20, 
    6.80, 8.20, 9.10
]

E24_base_values = [
    1.0, 1.1, 1.2, 
    1.3, 1.5, 1.6, 
    1.8, 2.0, 2.2, 
    2.4, 2.7, 3.0,
    3.3, 3.6, 3.9,
    4.3, 4.7, 5.1,
    5.6, 6.2, 6.8,
    7.5, 8.2, 9.1
]

E96_plus_E24_values = E96_base_values + extra_E24_base_values
E96_plus_E24_values.sort()

multiplier_list = [
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000
]

min_value = {
    "5%": {
        "TH0.250": 1,
        "TH0.125": 1,
    },
    "1%": {
        "0201": 1,
        "0402": 1,
        "0603": 1,
        "0805": 1,
        "1206": 1,
        "1210": 1,
        "2010": 1,
        "2512": 1,
    },
    "0.1%": {
        "0201": 9999999,
        "0402": 4.7,
        "0603": 1,
        "0805": 1,
        "1206": 10,
        "1210": 10,
        "2010": 10,
        "2512": 10,
    },
}

max_value = {
    "5%": {
        "TH0.250": 10000000,
        "TH0.125": 10000000,
    },
    "1%": {
        "0201": 10000000,
        "0402": 10000000,
        "0603": 10000000,
        "0805": 10000000,
        "1206": 10000000,
        "1210": 10000000,
        "2010": 10000000,
        "2512": 10000000,
    },
    "0.1%": {
        "0201": 0,
        "0402": 240000,
        "0603": 1000000,
        "0805": 1500000,
        "1206": 1000000,
        "1210": 1000000,
        "2010": 1000000,
        "2512": 1000000,
    },
}


package_list = ["0201", "0402", "0603", "0805", "1206", "1210", "2010", "2512", "TH0.125", "TH0.250"]

wattage_dict = {
    "0201": "1/20W",
    "0402": "1/16W",
    "0603": "1/10W",
    "0805": "1/8W",
    "1206": "1/4W",
    "1210": "1/2W",
    "2010": "3/4W",
    "2512": "1W",
    "TH0.250": "1/4W",
    "TH0.125": "1/8W",
}

tolerance_list = ["5%", "1%", "0.1%"]

# UNI-ROYAL parts that JLCPCB stocks in its "Basic" category. These are the
# preferred primary part number (cheaper/always-stocked); Yageo is the fallback.
# Only 1% tolerance and these four packages have UNI-ROYAL parts in the Basic
# category. The part number is: package + prefix + 4-char value code + suffix
# e.g. a 2k 0402 is 0402WGF2001TCE. The value code is 3 significant digits
# followed by a decade multiplier (see get_uniroyal_value_code).
uniroyal_basic_fmt = {
    "0402": ("WGF", "TCE"),
    "0603": ("WAF", "T5E"),
    "0805": ("W8F", "T5E"),
    "1206": ("W4F", "T5E"),
}

# Manually-curated JLCPCB IDs for 0Ω parts in packages that have no UNI-ROYAL
# Basic option (the four packages above are resolved automatically via the db).
zero_ohm_ids = {
    "0201": "C270337",
    "0402": "C106231",
    "0603": "C21189",
    "0805": "C100045",
    "1206": "C19290",
    "1210": "C474103",
    "2010": "C270958",
    "2512": "C25469",
}

template_file = "resistor_template_kicad_sym"
jlc_file = "JLCPCB-ChipResistorSMT-20220531.csv"

def get_value_with_units(value):
    if value == 0:
        return str(value) + "Ω"
    if value < 1000:
        return str(value)[:4].rstrip('0').rstrip('.') + "Ω"
    elif value < 1000000:
        return str(value/1000)[:4].rstrip('0').rstrip('.') + "k"
    elif value < 1000000000:
        return str(value/1000000)[:4].rstrip('0').rstrip('.') + "M"
    else:
        return "ValueTooLarge"

def get_short_value(value):
    """
    Return Yageo value string:
    Max 4 characters, strip trailing 0's
    R = decimal place
    K = kilo
    M = mega
    """
    if value == 0:
        return "0R"
    if value < 1000:
        return str(value).replace(".", "R")[:4].rstrip('0')
    elif value < 1000000:
        return str(value/1000).replace(".", "K")[:4].rstrip('0')
    elif value < 1000000000:
        return str(value/1000000).replace(".", "M")[:4].rstrip('0')
    else:
        return "ValueTooLarge"

def get_4dig_value(value_ohms):
    if value_ohms < 100:
        return str(value_ohms).replace(".", "R").ljust(4, "0")
    elif value_ohms < 1000:
        return str(value_ohms)[:3].ljust(4, "0")
    elif value_ohms < 10000:
        return str(value_ohms)[:3].ljust(3, "0") + "1"
    elif value_ohms < 100000:
        return str(value_ohms)[:3].ljust(3, "0") + "2"
    elif value_ohms < 1000000:
        return str(value_ohms)[:3].ljust(3, "0") + "3"
    elif value_ohms < 10000000:
        return str(value_ohms)[:3].ljust(3, "0") + "4"


def get_uniroyal_value_code(value_ohms):
    """
    Return UNI-ROYAL's 4-character value code: 3 significant digits followed by
    a decade multiplier. Digits 0-9 mean x10^0 .. x10^9; the letters J, K, L mean
    x10^-1, x10^-2, x10^-3 (for values below 100Ω).
    e.g. 2k -> "2001", 49.9k -> "4992", 10M -> "1005", 10Ω -> "100J", 1Ω -> "100K"
    """
    if value_ohms == 0:
        return "0000"
    exp = 0
    v = float(value_ohms)
    while v < 100:
        v *= 10
        exp -= 1
    while v >= 1000:
        v /= 10
        exp += 1
    ddd = int(round(v))
    if ddd == 1000:   # rounding pushed us to the next decade
        ddd = 100
        exp += 1
    mult = {-1: "J", -2: "K", -3: "L"}.get(exp, str(exp))
    return "{:03d}{}".format(ddd, mult)


def get_uniroyal_partnum(tolerance, package, value_ohms):
    """
    Return the UNI-ROYAL part number for this value, or None if UNI-ROYAL has no
    Basic-category series for the given package/tolerance. Note that a returned
    part number is only a *candidate*; it must still be confirmed present and
    "Basic" in the JLCPCB database before it is preferred over Yageo.
    """
    if tolerance != "1%" or package not in uniroyal_basic_fmt:
        return None
    prefix, suffix = uniroyal_basic_fmt[package]
    return package + prefix + get_uniroyal_value_code(value_ohms) + suffix


_uniroyal_basic_index_cache = {}

def get_uniroyal_basic_index(jlcdb):
    """ Build (once, then cache) a dict mapping each Basic-category UNI-ROYAL
        MFR.Part number to its (JLCPCB_ID, description) tuple. This lets us look
        up the preferred part in O(1) instead of scanning the whole file per value.
    """
    idx = _uniroyal_basic_index_cache.get(id(jlcdb))
    if idx is None:
        idx = {}
        for comp in jlcdb:
            if "UNI-ROYAL" in comp and '"Basic"' in comp:
                fields = comp.split(",")
                idx[fields[3].strip('"')] = (fields[0].strip('"'), fields[8].strip('"'))
        _uniroyal_basic_index_cache[id(jlcdb)] = idx
    return idx


def get_jlcpcb_id_and_matchtype(jlcdb, value_ohms, package, tolerance):
    """ Returns a tuple of the matching JLCPCB_ID and the method used to find that ID
        The method is "uniroyal_basic", "partnum", "specs" or "not found"
        If no matches are found the JLCPCB ID will be "?"
    """

    # Preferred: a UNI-ROYAL part that JLCPCB stocks in its "Basic" category
    uniroyal_partnum = get_uniroyal_partnum(tolerance, package, value_ohms)
    if uniroyal_partnum:
        hit = get_uniroyal_basic_index(jlcdb).get(uniroyal_partnum)
        if hit:
            return hit[0], "uniroyal_basic", hit[1]

    # Default values
    found_partnum_match = False
    found_specs_match = False
    partnum_match = ""
    specs_match = ""
    partnum_match_fields = ""
    specs_match_fields = ""
    alt_manuf_partnum = "not found"
    alt_resistortoday_partnum = "not found"
    alt_fua_partnum = "not found"
    alt_bournes_partnum = "not found"
    alt_AR_partnum = "not found"
    alt2_AR_partnum = "not found"
    alt_uniroyal_partnum = "not found"
    alt_uniroyal_partnum2 = "not found"

    # Calc Yageo part number (primary matching technique)
    manuf_partnum  = get_manuf_partnum(tolerance, package, value_ohms)

    # For 0.1% resistors, JLCPCB has a scattering of manufacturers, so we need to look for many different part numbers
    if tolerance == "0.1%":
        val4dig = get_4dig_value(value_ohms)
        alt_manuf_partnum = manuf_partnum.replace("BRD", "BRE")
        alt_resistortoday_partnum = manuf_partnum.replace("RT", "PTFR").replace("BRE07", "B").strip("L").ljust(13, "0")
        alt_fua_partnum = "TD" + package[2]+package[3] + "G" + val4dig + "B"
        alt_bournes_partnum = "CRT" + package + "-BY-"+val4dig+"GLF"
        alt_AR_partnum = "AR" + package[2]+package[3] + "BTD"+val4dig
        alt2_AR_partnum = "AR" + package[2]+package[3] + "BTC"+val4dig
        alt_uniroyal_partnum = "TC" + package[2]+package[3] + "50B"+ val4dig + "TCC"
        alt_uniroyal_partnum2 = package + "WBF" + val4dig + "TCE"

    # For searching by specifications, we match particular format of the Description field in the JLCPCB CSV file. 
    # This may need to be updated for future csv files
    val = " " + get_value_with_units(value_ohms).strip("R").strip("Ω").lower() + "�" #Hex code fffd appears as a separator in the source csv file
    pack = " " + package + " "
    tol = "�" + tolerance + " "

    # Scan all lines in the file, checking for matching strings
    for comp in jlcdb:
        # First, check if there's a part number match
        if manuf_partnum in comp  or (
            tolerance=="0.1%" and  (
                    alt_manuf_partnum in comp or
                    alt_resistortoday_partnum in comp or
                    alt_fua_partnum in comp or
                    alt_bournes_partnum in comp or
                    alt_AR_partnum in comp or
                    alt2_AR_partnum in comp or
                    alt_uniroyal_partnum in comp or
                    alt_uniroyal_partnum2 in comp
                    )):
            partnum_match = comp.split(",")[0].strip('"')
            found_partnum_match = True
            partnum_match_fields = comp.split(",")[8].strip('"')

        # Failing a part number match, check for a specification match
        elif (val in comp) and (pack in comp) and (tol in comp):
            specs_match = comp.split(",")[0].strip('"')
            found_specs_match = True
            specs_match_fields = comp.split(",")[8].strip('"')

        if found_partnum_match and found_specs_match:
            break

    # A UNI-ROYAL Basic match is preferred (handled above), then a part number
    # match, then a specifications match.
    if found_partnum_match:
        return partnum_match, "partnum", partnum_match_fields
    elif found_specs_match:
        return specs_match, "specs", specs_match_fields
    else:
        return "?", "not found", "not found"


def get_jlcpcb_id(jlc, value_ohms, package, tolerance):
    id, method, _ = get_jlcpcb_id_and_matchtype(jlc, value_ohms, package, tolerance)
    # For 0Ω parts without a UNI-ROYAL Basic option, fall back to a curated ID
    if value_ohms == 0 and method != "uniroyal_basic":
        return zero_ohm_ids.get(package, id)
    return id

def get_manuf_partnum(tolerance, package, value_ohms):
    # 1% Yageo ~$0.005/ea e.g. 1.02k is  RC0603FR-071K02L
    # 0.1% Yageo 25ppm/C ~$0.04/ea e.g. 1.02k is RT0603BRD071K02L 
    if tolerance=="0.1%":
        return "RT"+package+"BRD07"+get_short_value(value_ohms)+"L"
    elif tolerance == "1%":
        if package == "2010":
            return "RC"+package+"FK-07"+get_short_value(value_ohms)+"L"
        else:
            return "RC"+package+"FR-07"+get_short_value(value_ohms)+"L"
    elif package == "TH0.125":
        return "299-"+ get_value_with_units(value_ohms).strip("Ω") +"-RC"
    elif package == "TH0.250":
        return "291-"+ get_value_with_units(value_ohms).strip("Ω") +"-RC"
    else:
        return "Unknown"


def gen_res(jlc, value_ohms, package, tolerance, tpl_data):
    value_with_units = get_value_with_units(value_ohms)
    value_short = get_short_value(value_ohms) ##not used
    wattage = wattage_dict[package]
    yageo_partnum  = get_manuf_partnum(tolerance, package, value_ohms)
    opttol = "_" + tolerance if tolerance == "0.1%" else ""
    footprint = "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" if package.startswith("TH") else "R_"+package

    # Choose the primary part number: a UNI-ROYAL part in JLCPCB's Basic category
    # is preferred; otherwise fall back to Yageo (Xicon for through-hole).
    if package.startswith("TH"):
        partnum = yageo_partnum
        manuf = "Xicon"
        jlc_id = ""
    else:
        jlc_id, method, _ = get_jlcpcb_id_and_matchtype(jlc, value_ohms, package, tolerance)
        if method == "uniroyal_basic":
            partnum = get_uniroyal_partnum(tolerance, package, value_ohms)
            manuf = "UNI-ROYAL"
        else:
            partnum = yageo_partnum
            manuf = "Yageo"
            # Curated fallback ID for 0Ω parts the scan can't place
            if value_ohms == 0:
                jlc_id = zero_ohm_ids.get(package, jlc_id)

    symdata = tpl_data
    symdata = symdata.replace(r'%VAL%', value_with_units)
    symdata = symdata.replace(r'%VALSHORT%', value_short) #not in template
    symdata = symdata.replace(r'%PKG%', package)
    symdata = symdata.replace(r'%FOOTPRINT%', footprint)
    symdata = symdata.replace(r'%OPTTOL%', opttol)
    symdata = symdata.replace(r'%TOL%', tolerance)
    symdata = symdata.replace(r'%WATTS%', wattage)
    symdata = symdata.replace(r'%PARTNUM%', partnum)
    symdata = symdata.replace(r'%JLCPCBID%', jlc_id)
    symdata = symdata.replace(r'%MANUF%', manuf)
    return symdata


if __name__ == "__main__":
    showusage = False
    outfile = ""
    errstr = ""
    minmult = 1
    maxmult = 1000000

    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    else:
        errstr = "Please specify an output file name"
        showusage = True

    package = "0603"
    if len(sys.argv) > 2:
        package = sys.argv[2]
        if package not in package_list:
            errstr = "Package parameter is not known"
            showusage = True

    tolerance = "1%"
    if len(sys.argv) > 3:
        tolerance = sys.argv[3]
        if tolerance not in tolerance_list:
            errstr = "Tolerance must be 1% or 0.1%"
            showusage = True

    if len(sys.argv) > 4:
        try:
            minmult = int(sys.argv[4])
        except:
            minmult = 1
        if minmult not in multiplier_list:
            errstr = "min_mult parameter is not a power of 10 between 1 and 1000000"
            showusage = True

    if len(sys.argv) > 5:
        try:
            maxmult = int(sys.argv[5])
        except:
            maxmult = 1000000
        if maxmult not in multiplier_list:
            errstr = "max_mult parameter is not a power of 10 between 1 and 1000000"
            showusage = True
        elif maxmult < minmult:
            errstr = "max_mult must be greater than or equal to min_mult"
            showusage = True

    try:
        with open(jlc_file) as db:
            jlc = db.readlines()
    except:
        jlc = []

    base_values = E24_base_values if package.startswith("TH") else E96_plus_E24_values

    if showusage:
        if errstr:
            print("\nERROR: " + errstr)
        print("""
    Usage: python3 resistor_gen.py libfilename {package} {tolerance} {min_mult} {max_mult} 

    Generates a Kicad 6 symbol library of E96+E24 resistors for a given
    package size and tolerance. The Part Number field is set to a UNI-ROYAL part
    when JLCPCB stocks one in its "Basic" category (1%, 0402/0603/0805/1206);
    otherwise it falls back to a Yageo RC-series part number (RT-series for 0.1%).
    JLCPCB part numbers will be added when found in JLCPCB's database.

    Parameters:
    {libfilename} is the output file name. Required. If you want Kicad to recognize the file, end it with .kicad_sym
    {package} can be 0201, 0402, 0603, 0805, or 1206 (default 0603). The 2010 package is also supported, but the part numbers have not been verified.
    {tolerance} can be 1% or 0.1% (default 1%)
    {min_mult} is lowest power of 10 for which to generate values (default 1}. This is inclusive, so if min_mult is 100, values starting at 100Ω will be output.
    {max_mult} is highest power of 10 for which to generate values (default 1000000}. This is inclusive, so if max_mult is 1000, then values up to 9.76k will be output.

    Note: A 0R resistor is added if tolerance is 1% and min_mult is 1

    There are some special commands that can be specified instead of libfilename. These are probably only useful for debugging or fine-tuning the algorithm that deduces the JLCPCB ID. These all output to stdout instead of a file. The other parameters (package, tolerance, etc) have the same meaning.

    print-partnums: print the primary part numbers (UNI-ROYAL Basic where available, else Yageo). Useful for importing into a distributor to verify the part numbers are orderable.
    print-bom: print a JLCPCB compatible BOM csv file. Useful for verifying the JLCPCB IDs are accurate.
    print-missing: print items with no JLCPCB ID
    print-matched-uniroyal: print items whose JLCPCB ID was matched to a UNI-ROYAL Basic-category part
    print-matched-partnum: print items with a JLCPCB ID that was matched by an automatically generated vendor part number (e.g. Yageo P/N)
    print-matched-specs: will print items with a JLCPCB ID that was matched by value/package/tolerance instead of part number

    """)

    elif outfile=="print-partnums":
        tpl = "%PARTNUM%"
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in base_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    elif outfile=="print-bom":
        print('"Comment", "Designator", "Footprint", "JLCPCB Part #"')
        i = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in base_values:
                val = m * v
                tpl = f"\"%VAL% %PKG% %TOL%\", \"R{i}\", \"R%PKG%\",  \"%JLCPCBID%\""
                i = i + 1
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    elif outfile=="print-missing":
        cnt = 0
        total = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in base_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    value_with_units = get_value_with_units(val)
                    manuf_partnum  = get_manuf_partnum(tolerance, package, val)
                    jlc_id = get_jlcpcb_id(jlc, val, package, tolerance)
                    if jlc_id == "?":
                        print(value_with_units, package, tolerance, manuf_partnum) 
                        cnt = cnt + 1
                    total = total + 1
        print(f"Missing: {cnt} of {total}")

    elif outfile in ("print-matched-specs", "print-matched-partnum", "print-matched-uniroyal"):
        wanted = {
            "print-matched-specs": "specs",
            "print-matched-partnum": "partnum",
            "print-matched-uniroyal": "uniroyal_basic",
        }[outfile]
        cnt = 0
        total = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in base_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    value_with_units = get_value_with_units(val)
                    jlc_id, method, specs = get_jlcpcb_id_and_matchtype(jlc, val, package, tolerance)
                    specs = specs.replace("Thin Film Resistor ","").replace("-55","").replace("~+155","").replace(" Chip Resistor - Surface Mount ROHS","").replace("150V","").replace("100V","").replace("25ppm/K","").replace("25ppm/","").replace("50ppm/","").replace("10ppm/","").replace("10ppm/K","").replace("~+125","").replace("100mW","").replace("125mW","").replace("1/8W","").replace("1/4W","").replace("�"," ")
                    if method == wanted:
                        print(value_with_units, package, tolerance, jlc_id, specs)
                        cnt = cnt + 1
                    total = total + 1
        print(f"Found: {cnt} of {total}")



    else:
        print(f"Generating values for {package} {tolerance} from {get_value_with_units(1.0 * minmult)} to {get_value_with_units(9.76 * maxmult)}")

        header = """(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)
"""
        footer = """)
"""


        libdata = header
        with open(template_file) as tpl:
            tpl_data = tpl.read()

            if tolerance == "1%" and minmult == 1:
                print("Generating 0Ω")
                libdata += gen_res(jlc, 0, package, tolerance, tpl_data)

            for m in multiplier_list:
                if m < minmult or m > maxmult:
                    continue
                for v in base_values:
                    val = round(m * v, 3)
                    if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                        libdata += gen_res(jlc, val, package, tolerance, tpl_data)

            libdata += footer
            with open(outfile, "w") as f:
                f.write(libdata)


