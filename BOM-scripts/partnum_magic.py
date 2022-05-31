import re
import string

def deduce_SMD_TH(package):
    """
    checks if package contains certain letters to decide if its SMD
    """

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

    return [smd, points]


def get_package(footprint):
    """
    removes footprint library name from footprint name
    Changes R_ to R and C_ to C (example: R_0603 => R0603)
    """
    fprint = str(footprint)
    package = re.sub(r".*:", "", fprint)
    package = package.replace('R_0','R0');
    package = package.replace('C_0','C0');
    package = package.replace('R_1','R1');
    package = package.replace('C_1','C1');
    return package


def deduce_resistor_metric(value):
    """
    Returns the metric multiplier of the given human-readable resistor value
    Finds various invalid cases and returns None
    Returns None (invalid), "R", "K", or "M"
    """
    if len(value) == 0:
        return None

    if value.find('m') >= 0:
        return None  #Todo: figure out part numbers for milliOhm values

    if value[0] == '0':
        return None  #Todo: handle metric shifts: 0.12k => 120R, and 1230R => 1.23k

    value = value.upper()

    num_letters = count_letters(value)
    if (num_letters == 0):
        return "R"

    if (num_letters > 1):
        return None

    if (count_characters("[KMR]", value) != 1):
        return None

    if (value.find('K') > 0):
        return 'K'
    elif (value.find('M') > 0):
        return 'M'
    elif (value.find('R') > 0):
        return 'R'
    else:
        return None

def is_malformed(value, metric):
    """
    Returns True if given value is not a valid number
    Cases such as 1k2 and 1.2k are both considered valid
    But 1k2.3 or 1.2k3 are not
    The only valid metrics allowed are "K", "M" and "R" (not case-sensitive).
    """
    if len(value) == 0: 
        return True
    elif count_characters("\.", value) > 1:
        return True
    elif metric == None:
        return True

    metric_pos = value.upper().find(metric)
    has_metric_and_decimal = (metric_pos > 0) and (value.find('.') > 0)
    value_ends_in_metric = metric_pos == (len(value)-1)

    if (has_metric_and_decimal and not value_ends_in_metric) : #e.g: 1.2k3 and 1k2.3 are invalid
        return True
    return False


def deduce_0603_resistor(value):
    """
    Deduce a resistors part number based on a given human-readable value.
    Values can be something like "1.2k" or "1k23" or "123.0M" or "45.0" or "45R"
    If it can't be deduced, empty strings are returned
    Otherwise, returns a tuple of three strings: manufacturer, part_no, designation

    As of now, only 0603 Yageo RC-series Thick Film resistors are supported
    Todo: Deduce metric shifts, such as 1230R == 1.23K, and 0.1k == 100R
    Todo: figure out part numbers for 4-sig-fig resistors, e.g. 12k34
    Todo: figure out part numbers for milliOhm resistors, e.g. 50m
    Todo: Handle ohm symbol the same as R
    Todo: Check with actual Yageo part numbers (mouser API?)
    """
    metric = deduce_resistor_metric(value)

    if is_malformed(value, metric):
        return ["", "", ""]

    manuf_value = value.upper()
    metric_pos = manuf_value.find(metric)
    decimal_pos = manuf_value.find('.')

    if (decimal_pos >= 0):
        manuf_value = manuf_value.replace(".", metric, 1)
        if (metric_pos >= 0):
            manuf_value = manuf_value[:metric_pos]
    
    elif (metric_pos < 0 ):
        manuf_value = manuf_value + metric

    manuf_value = manuf_value.rstrip("0")

    if count_digits(manuf_value) > 3:
        return ["", "", ""]

    manufacturer = ("Yageo")
    part_no = ("RC0603FR-07" + str(manuf_value) + "L")
    designation = (str(value) + ", 1%, 1/10W, 0603")

    return [manufacturer, part_no, designation]


### Helper Functions

def count_letters(thestring):
    return sum(1 for m in re.finditer("[a-zA-Z]", thestring))

def count_characters(chars, thestring):
    return sum(1 for m in re.finditer(chars, thestring))

def count_digits(thestring):
    return sum(1 for m in re.finditer("[0-9]", thestring))

def print_check(value):
    [manufacturer, part_no, designation] = deduce_0603_resistor(value)
    print ("Value: " + value + "\t==>\t" + part_no)


### Test Functions

# def test_res_value(value, expected_partno):
#     [manufacturer, part_no, designation] = deduce_0603_resistor(value)
#     if (expected_partno == part_no):
#         print ("\tpass: " + value + " ==> " + part_no)
#     else:
#         print ("***\tFAIL: " + value + " ==> " + part_no + " Expected " + expected_partno)

# def test_metric(value, expected_metric):
#     if (expected_metric == None):
#         expected_metric_printable = "None"
#     else:
#         expected_metric_printable = expected_metric

#     if (deduce_resistor_metric(value) != expected_metric):
#         print ("****\tFAIL: " + value + " should be " + expected_metric_printable)
#     else:
#         print ("\tPass: " + value + " metric is " + expected_metric_printable)

# def test_smd_th(package, expected_SMD_TH, expected_points):
#     [smd, points] = deduce_SMD_TH(package)
#     if (smd == expected_SMD_TH and points == expected_points):
#         print ("\tPass: " + package + " is " + str(points) + " points " + smd)
#     else:
#         print ("****\tFAIL: " + package + " expected to be " + str(expected_points) + ", " + expected_SMD_TH + " but was " + str(points) + ", " + smd)

# def test_get_package(footprint, expected_package):
#     package = get_package(footprint)
#     if (package == expected_package):
#         print ("\tPass: " + str(footprint) + " is " + str(package))
#     else:
#         print ("****\tFAIL: " + str(footprint) + " expected to be " + str(expected_package) + " but was " + str(package))

