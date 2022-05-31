#coding=utf-8
from partnum_magic import *

### Test Functions

def test_res_value(value, expected_partno):
    [manufacturer, part_no, designation] = deduce_0603_resistor(value)
    if (expected_partno == part_no):
        print ("\tpass: " + value + " ==> " + part_no)
    else:
        print ("***\tFAIL: " + value + " ==> " + part_no + " Expected " + expected_partno)

def test_metric(value, expected_metric):
    if (expected_metric == None):
        expected_metric_printable = "None"
    else:
        expected_metric_printable = expected_metric

    if (deduce_resistor_metric(value) != expected_metric):
        print ("****\tFAIL: " + value + " should be " + expected_metric_printable)
    else:
        print ("\tPass: " + value + " metric is " + expected_metric_printable)

def test_smd_th(package, expected_SMD_TH, expected_points):
    [smd, points] = deduce_SMD_TH(package)
    if (smd == expected_SMD_TH and points == expected_points):
        print ("\tPass: " + package + " is " + str(points) + " points " + smd)
    else:
        print ("****\tFAIL: " + package + " expected to be " + str(expected_points) + ", " + expected_SMD_TH + " but was " + str(points) + ", " + smd)

def test_get_package(footprint, expected_package):
    package = get_package(footprint)
    if (package == expected_package):
        print ("\tPass: " + str(footprint) + " is " + str(package))
    else:
        print ("****\tFAIL: " + str(footprint) + " expected to be " + str(expected_package) + " but was " + str(package))


if __name__ == "__main__":
    print("Testing Metrics...")
    test_metric("400", "R")
    test_metric("400R", "R")
    test_metric("400r", "R")
    test_metric("400A", None)
    test_metric("400K", "K")
    test_metric("400k", "K")
    test_metric("400M", "M")
    test_metric("400m", None)
    test_metric("", None)
    test_metric("400KM", None)
    test_metric("400RM", None)
    test_metric("400RK", None)
    test_metric("400RMK", None)
    test_metric("400aRMK", None)
    test_metric("K400", None)
    test_metric("M400", None)
    test_metric("R400", None)
    test_metric("1K4", "K")
    test_metric("1M4", "M")
    test_metric("1R4", "R")

    test_metric("30Ω", "R")

    print("")
    print("Testing value deduction...")

    test_res_value("1m", "")
    test_res_value("50m", "")
    test_res_value("50.0m", "")
    test_res_value("50m0", "")
    test_res_value("0.1", "")

    test_res_value("1", "RC0603FR-071RL")
    test_res_value("1.", "RC0603FR-071RL")
    test_res_value("1R", "RC0603FR-071RL")

    test_res_value("1R2", "RC0603FR-071R2L")
    test_res_value("1.2", "RC0603FR-071R2L")
    test_res_value("1.2R", "RC0603FR-071R2L")

    test_res_value("12", "RC0603FR-0712RL")
    test_res_value("12R", "RC0603FR-0712RL")
    test_res_value("12.", "RC0603FR-0712RL")
    test_res_value("12.R", "RC0603FR-0712RL")
    test_res_value("12.0", "RC0603FR-0712RL")
    test_res_value("12.0R", "RC0603FR-0712RL")
    test_res_value("12.00R", "RC0603FR-0712RL")
    test_res_value("12.000R", "RC0603FR-0712RL")
    test_res_value("12.01R", "")

    test_res_value("12.3", "RC0603FR-0712R3L")
    test_res_value("12.3R", "RC0603FR-0712R3L")
    test_res_value("12R3", "RC0603FR-0712R3L")
    test_res_value("12R34", "")
    test_res_value("12.34", "")
    test_res_value("12.34R", "")

    test_res_value("123", "RC0603FR-07123RL")
    test_res_value("123R", "RC0603FR-07123RL")
    test_res_value("123.0R", "RC0603FR-07123RL")
    test_res_value("123.1R", "")
    test_res_value("0.1k", "RC0603FR-07100RL") #Todo: This is failing

    test_res_value("4k", "RC0603FR-074KL")
    test_res_value("4K", "RC0603FR-074KL")
    test_res_value("4.K", "RC0603FR-074KL")
    test_res_value("4.0K", "RC0603FR-074KL")
    test_res_value("4.00K", "RC0603FR-074KL")
    test_res_value("4.000k", "RC0603FR-074KL")
    test_res_value("4k000", "RC0603FR-074KL")

    test_res_value("4.7k", "RC0603FR-074K7L")
    test_res_value("4k7", "RC0603FR-074K7L")
    test_res_value("4k70", "RC0603FR-074K7L")
    test_res_value("4k70.", "")
    test_res_value("4k72", "RC0603FR-074K72L")
    test_res_value("4k729", "")

    test_res_value("43k", "RC0603FR-0743KL")
    test_res_value("43k7", "RC0603FR-0743K7L")
    test_res_value("43.7k", "RC0603FR-0743K7L")
    test_res_value("43.7k9", "")

    test_res_value("123k", "RC0603FR-07123KL")
    test_res_value("123K", "RC0603FR-07123KL")
    test_res_value("123.0K", "RC0603FR-07123KL")
    test_res_value("123.0k", "RC0603FR-07123KL")
    test_res_value("123k4" , "")
    test_res_value("123.4k" , "")
    test_res_value("123.4k9" , "")

    test_res_value("1230" , "RC0603FR-071K23L") #Todo: This is failing
    test_res_value("1239" , "")
    test_res_value("12349" , "")
    test_res_value("12k34" , "")
    test_res_value("12k349" , "")
    test_res_value("12k345" , "")

    test_res_value("30Ω", "RC0603FR-0730RL") #Todo: This is failing

    test_smd_th("D_SOD-123", "SMD", 2)
    test_smd_th("SOT23-3_PO132", "SMD", 3)
    test_smd_th("SOT23-3_PO123", "SMD", 3)
    test_smd_th("SOT23-3_PO213", "SMD", 3)
    test_smd_th("LED_PLCC-4", "SMD", 4)
    test_smd_th("C_0603", "SMD", 2)
    test_smd_th("C0603", "SMD", 2)
    test_smd_th("C_1206", "SMD", 2)
    test_smd_th("C1206", "SMD", 2)
    test_smd_th("C_1210", "SMD", 2)
    test_smd_th("C1210", "SMD", 2)
    test_smd_th("C_0402", "SMD", 2)
    test_smd_th("C0402", "SMD", 2)
    test_smd_th("R_0603", "SMD", 2)
    test_smd_th("R0603", "SMD", 2)
    test_smd_th("R_0402", "SMD", 2)
    test_smd_th("R0402", "SMD", 2)
    test_smd_th("LQFP-48_7x7mm_P0.5mm", "SMD", 48)
    test_smd_th("FA-238", "SMD", 4)
    test_smd_th("Button_RgbLED_SPST_TC002", "TH", 8)
    test_smd_th("Button_RgbLED_SPST_PB615303HL-7mm", "TH", 8)
    test_smd_th("TSOT-23-6", "SMD", 6)
    test_smd_th("L_Taiyo-Yuden_NR-40xx", "SMD", 2)
    test_smd_th("LED_0603_1608Metric", "SMD", 2)

    test_smd_th("Pins_2x08_2.54mm_TH_EuroPower", "TH", 16)
    test_smd_th("Pins_1x02_2.54mm_TH", "TH", 2)
    test_smd_th("Pins_1x06_2.54mm_TH_SWD", "TH", 6)
    test_smd_th("Pot_16mm_NoDet_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_16mm_CtrDet_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_16mm_21Det_RV16AF-4A", "TH", 3)
    test_smd_th("Pot_9mm_Knurl_Det", "TH", 5)
    test_smd_th("EighthInch_PJ398SM", "TH", 3)

    test_get_package("4ms_Package_SSOP:TSSOP-8_4.4x3mm_Pitch0.65mm", "TSSOP-8_4.4x3mm_Pitch0.65mm")
    test_get_package("4ms_Resistor:R_0805", "R0805")
    test_get_package("4ms_Resistor:C_0603", "C0603")
