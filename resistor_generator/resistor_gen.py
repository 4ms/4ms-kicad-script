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
        "1206": 1,
        "1210": 4.7,
        "2010": 4.7,
        "2512": 4.7,
    },
}

max_value = {
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
        "1206": 1500000,
        "1210": 1000000,
        "2010": 1000000,
        "2512": 1000000,
    },
}


package_list = ["0201", "0402", "0603", "0805", "1206", "1210", "2010", "2512"]

wattage_dict = {
    "0201": "1/20W",
    "0402": "1/16W",
    "0603": "1/10W",
    "0805": "1/8W",
    "1206": "1/4W",
    "1210": "1/2W",
    "2010": "3/4W",
    "2512": "1W",
}

tolerance_list = ["1%", "0.1%"]

template_file = "resistor_template_kicad_sym"
jlc_file = "JLCPCB-ChipResistorSMT-20220531.csv"

def get_value_with_units(value):
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


def get_jlcpcb_id_and_matchtype(jlcdb, value_ohms, package, tolerance):
    """ Returns a tuple of the matching JLCPCB_ID and the method used to find that ID
        The method is either "partnum", "specs" or "not found"
        If no matches are found the JLCPCB ID will be "?"
    """

    # Default values
    found_partnum_match = False
    found_specs_match = False
    partnum_match = ""
    specs_match = ""
    partnum_match_fields = ""
    specs_match_fields = ""
    alt_yageo_partnum = "not found"
    alt_resistortoday_partnum = "not found"
    alt_fua_partnum = "not found"
    alt_bournes_partnum = "not found"
    alt_AR_partnum = "not found"
    alt2_AR_partnum = "not found"
    alt_uniroyal_partnum = "not found"

    # Calc Yageo part number (primary matching technique)
    value_short = get_short_value(value_ohms)
    yageo_partnum  = get_yageo_partnum(tolerance, package, value_short)

    # For 0.1% resistors, JLCPCB has a scattering of manufacturers, so we need to look for many different part numbers
    if tolerance == "0.1%":
        val4dig = get_4dig_value(value_ohms)
        alt_yageo_partnum = yageo_partnum.replace("BRD", "BRE")
        alt_resistortoday_partnum = yageo_partnum.replace("RT", "PTFR").replace("BRE07", "B").strip("L").ljust(13, "0")
        alt_fua_partnum = "TD" + package[2]+package[3] + "G" + val4dig + "B"
        alt_bournes_partnum = "CRT" + package + "-BY-"+val4dig+"GLF"
        alt_AR_partnum = "AR" + package[2]+package[3] + "BTD"+val4dig
        alt2_AR_partnum = "AR" + package[2]+package[3] + "BTC"+val4dig
        alt_uniroyal_partnum = "TC" + package[2]+package[3] + "50B"+ val4dig + "TCC"

    # For searching by specifications, we match particular format of the Description field in the JLCPCB CSV file. 
    # This may need to be updated for future csv files
    val = " " + get_value_with_units(value_ohms).strip("R").strip("Ω").lower() + "�" #Hex code fffd appears as a separator in the source csv file
    pack = " " + package + " "
    tol = "�" + tolerance + " "

    # Scan all lines in the file, checking for matching strings
    for comp in jlcdb:
        # First, check if there's a part number match
        if yageo_partnum in comp  or (
            tolerance=="0.1%" and  (
                    alt_yageo_partnum in comp or
                    alt_resistortoday_partnum in comp or
                    alt_fua_partnum in comp or
                    alt_bournes_partnum in comp or
                    alt_AR_partnum in comp or
                    alt2_AR_partnum in comp or
                    alt_uniroyal_partnum in comp
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

    # Part number matches are consider the best type of matches, so return that item if we matched one
    # Otherwise, return the item that matched on specifications
    if found_partnum_match:
        return partnum_match, "partnum", partnum_match_fields
    elif found_specs_match:
        return specs_match, "specs", specs_match_fields
    else:
        return "?", "not found", "not found"


def get_jlcpcb_id(jlc, value_ohms, package, tolerance):
    id, _, _ = get_jlcpcb_id_and_matchtype(jlc, value_ohms, package, tolerance)
    return id

def get_yageo_partnum(tolerance, package, value_short):
    # 1% Yageo ~$0.005/ea e.g. 1.02k is  RC0603FR-071K02L
    # 0.1% Yageo 25ppm/C ~$0.04/ea e.g. 1.02k is RT0603BRD071K02L 
    if tolerance=="0.1%":
        return "RT"+package+"BRD07"+value_short+"L"
    else:
        return "RC"+package+"FR-07"+value_short+"L"


def gen_res(jlc, value_ohms, package, tolerance, tpl_data):
    value_with_units = get_value_with_units(value_ohms)
    value_short = get_short_value(value_ohms)
    wattage = wattage_dict[package]
    yageo_partnum  = get_yageo_partnum(tolerance, package, value_short)
    if tolerance=="0.1%":
        opttol = "_" + tolerance
    else:
        opttol = ""
    jlc_id = get_jlcpcb_id(jlc, value_ohms, package, tolerance)

    symdata = tpl_data
    symdata = symdata.replace(r'%VAL%', value_with_units)
    symdata = symdata.replace(r'%VALSHORT%', value_short)
    symdata = symdata.replace(r'%PKG%', package)
    symdata = symdata.replace(r'%OPTTOL%', opttol)
    symdata = symdata.replace(r'%TOL%', tolerance)
    symdata = symdata.replace(r'%WATTS%', wattage)
    symdata = symdata.replace(r'%PARTNUM%', yageo_partnum)
    symdata = symdata.replace(r'%JLCPCBID%', jlc_id)
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

    if showusage:
        if errstr:
            print("\nERROR: " + errstr)
        print("""
    Usage: python3 resistor_gen.py libfilename {package} {tolerance} {min_mult} {max_mult} 

    Generates a Kicad 6 symbol library of E96+E24 resistors for a given
    package size and tolerance. Yageo RC-series resistor part numbers will be added
    to each symbol's Part Number field (RT-series for 0.1%).

    Parameters:
    {libfilename} is the output file name. Required. If you want Kicad to recognize the file, end it with .kicad_sym
    {package} can be 0201, 0402, 0603, 0805, or 1206 (default 0603)
    {tolerance} can be 1% or 0.1% (default 1%)
    {min_mult} is lowest power of 10 for which to generate values (default 1}. This is inclusive, so if min_mult is 100, values starting at 100Ω will be output.
    {max_mult} is highest power of 10 for which to generate values (default 1000000}. This is inclusive, so if max_mult is 1000, then values up to 9.76k will be output.
       
    There are some special commands that can be specified instead of libfilename. These are probably only useful for debugging or fine-tuning the algorithm that deduces the JLCPCB ID. These all output to stdout instead of a file. The other parameters (package, tolerance, etc) have the same meaning.

    print-partnums: print the Yageo part numbers. Useful for importing into mouser to verify the part numbers are orderable.
    print-bom: print a JLCPCB compatible BOM csv file. Useful for verifying the JLCPCB IDs are accurate.
    print-missing: print items with no JLCPCB ID
    print-matched-partnum: print items with a JLCPCB ID that was matched by an automatically generated vendor part number (e.g. Yageo P/N)
    print-matched-specs: will print items with a JLCPCB ID that was matched by value/package/tolerance instead of part number

    """)

    elif outfile=="print-partnums":
        tpl = "%PARTNUM%"
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    elif outfile=="print-bom":
        print('"Comment", "Designator", "Footprint", "JLCPCB Part #"')
        i = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                tpl = f"\"%VAL% %PKG% %TOL%\", \"R{i}\", \"R%PKG%\",  \"%JLCPCBID%\""
                i = i + 1
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    print(gen_res(jlc, val, package, tolerance, tpl))

    elif outfile=="print-missing":
        cnt = 0
        total = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    value_with_units = get_value_with_units(val)
                    value_short = get_short_value(val)
                    yageo_partnum  = get_yageo_partnum(tolerance, package, value_short)
                    jlc_id = get_jlcpcb_id(jlc, val, package, tolerance)
                    if jlc_id == "?":
                        print(value_with_units, package, tolerance, yageo_partnum) 
                        cnt = cnt + 1
                    total = total + 1
        print(f"Missing: {cnt} of {total}")

    elif outfile == "print-matched-specs" or outfile == "print-matched-partnum":
        cnt = 0
        total = 0
        for m in multiplier_list[multiplier_list.index(minmult):multiplier_list.index(maxmult)+1]:
            for v in E96_plus_E24_values:
                val = m * v
                if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                    value_with_units = get_value_with_units(val)
                    jlc_id, method, specs = get_jlcpcb_id_and_matchtype(jlc, val, package, tolerance)
                    specs = specs.replace("Thin Film Resistor ","").replace("-55","").replace("~+155","").replace(" Chip Resistor - Surface Mount ROHS","").replace("150V","").replace("100V","").replace("25ppm/K","").replace("25ppm/","").replace("50ppm/","").replace("10ppm/","").replace("10ppm/K","").replace("~+125","").replace("100mW","").replace("125mW","").replace("1/8W","").replace("1/4W","").replace("�"," ")
                    if outfile=="print-matched-specs" and method == "specs":
                        print(value_with_units, package, tolerance, jlc_id, specs)
                        cnt = cnt + 1
                    elif outfile=="print-matched-partnum" and method == "partnum":
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
            for m in multiplier_list:
                if m < minmult or m > maxmult:
                    continue
                for v in E96_plus_E24_values:
                    val = m * v
                    if val >= min_value[tolerance][package] and val <= max_value[tolerance][package]:
                        libdata += gen_res(jlc, val, package, tolerance, tpl_data)

            libdata += footer
            with open(outfile, "w") as f:
                f.write(libdata)


