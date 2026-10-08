"""
Generate a blank Component Placement Template for new KiCad projects.

Coworker workflow:
  1. Copy "Component Placement Template.xlsx" into the new project folder
  2. Fill in: Display Name, X, Y, Component Type, Subtype
  3. KiCad Symbol auto-fills via VLOOKUP — do not edit
  4. Ref is assigned by the KiCad conversion script — do not edit once set

Run:  python3 make_placement_template.py
Output: Component Placement Template.xlsx  (same folder as this script)
"""
import os
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Component Type → Subtype  (friendly label, KiCad symbol string)
# Sorted by real-world usage frequency across 4ms projects.
# Named range name = key — must be a valid Excel identifier (no spaces/special chars)
# ---------------------------------------------------------------------------
OPTIONS = {
    "Pot": [
        ("16mm No Detent 10k",              "4ms_Potentiometer:16mm_NoDet_10k"),
        ("16mm No Detent 100k",             "4ms_Potentiometer:16mm_NoDet_100k"),
        ("16mm Center Detent 10k",          "4ms_Potentiometer:16mm_CtrDet_10k"),
        ("16mm 21-Detent 10k",              "4ms_Potentiometer:16mm_21Det_10k"),
        ("9mm No Detent 100k Knurled",      "4ms_Potentiometer:9mm_NoDet_100k_Knurled_Lined"),
        ("9mm Center Detent 100k Knurled",  "4ms_Potentiometer:9mm_CtrDet_100k_Knurled_Lined"),
        ("9mm No Detent 10k D-Shaft",       "4ms_Potentiometer:9mm_NoDet_10k_DShaft"),
        ("9mm Center Detent 10k D-Shaft",   "4ms_Potentiometer:9mm_CtrDet_10k_DShaft"),
        ("Slider LED 20mm 100k",            "4ms_Potentiometer:Pot_Slider_LED_20mm_100K"),
        ("Slider LED 30mm 10k",             "4ms_Potentiometer:Pot_Slider_LED_30mm_10K"),
        ("Slider Top-Up 60mm",              "4ms_Potentiometer:Pot_Slider_Top-Up_60RFT2-B"),
        ("TrimPot T73YE 10k",               "4ms_Potentiometer:TrimPot_T73YEt_10k"),
        ("TrimPot T73YE 100k",              "4ms_Potentiometer:TrimPot_T73YEt_100k"),
        ("TrimPot T73YE 1k",                "4ms_Potentiometer:TrimPot_T73YEt_1k"),
        ("TrimPot TC33X 100R",              "4ms_Potentiometer:TrimPot_TC33X_100R"),
        ("TrimPot TC33X 200R",              "4ms_Potentiometer:TrimPot_TC33X_200R"),
        ("TrimPot TC33X 1k",                "4ms_Potentiometer:TrimPot_TC33X_1k"),
        ("TrimPot TC33X 10k",               "4ms_Potentiometer:TrimPot_TC33X_10k"),
        ("TrimPot TC33X 20k",               "4ms_Potentiometer:TrimPot_TC33X_20k"),
        ("TrimPot TC33X 50k",               "4ms_Potentiometer:TrimPot_TC33X_50k"),
        ("TrimPot TC33X 100k",              "4ms_Potentiometer:TrimPot_TC33X_100k"),
        ("TrimPot TC33X DNP",               "4ms_Potentiometer:TrimPot_TC33X_DNP"),
    ],
    "Jack": [
        ("3.5mm Mono Switched",             "4ms_Jack:3.5mm_Mono_Switched"),
        ("3.5mm Mono Switched sm",          "4ms_Jack:3.5mm_Mono_Switched_sm"),
        ("3.5mm Mono Switched SymSmall",    "4ms_Jack:3.5mm_Mono_Switched_SymSmall_0.05"),
        ("3.5mm Stereo",                    "4ms_Jack:3.5mm_Stereo"),
        ("3.5mm Stereo sm",                 "4ms_Jack:3.5mm_Stereo_sm"),
        ("3.5mm Stereo SymSmall",           "4ms_Jack:3.5mm_Stereo_SymSmall_0.05"),
        ("3.5mm Stereo SMT Right Angle",    "4ms_Jack:3.5mm_Stereo_SMT_Right_Angle_Horizontal"),
        ("3.5mm Stereo Switched",           "4ms_Jack:3.5mm_Stereo_Switched_Jack"),
        ("1/4in Stereo",                    "4ms_Jack:1/4{dblquote}_Jack_Stereo"),
        ("Barrel 2.0mm PJ064",              "4ms_Jack:Barrel_2.0mmPin_PJ064"),
        ("Barrel 2.1mm Right Angle",        "4ms_Jack:Barrel_2.1mm_Right_Angle"),
        ("MIDI DIN5",                       "4ms_Jack:MIDI_DIN5_SD-50BV"),
    ],
    "LED": [
        ("RGB PLCC4",                       "4ms_LED:RGB_CA_PLCC4"),
        ("RGB Right Angle",                 "4ms_LED:RGB_CA_RightAngle"),
        ("Blue 0603",                       "4ms_LED:Blue_56mcd_0603"),
        ("Red 0603",                        "4ms_LED:Red_100mcd_0603"),
        ("White 0603",                      "4ms_LED:White_min200mcd_0603"),
        ("Green 0603",                      "4ms_LED:Green_350mcd_0603"),
        ("Yellow 0603",                     "4ms_LED:Yellow_23mcd_0603"),
        ("Dual SMD 4-pin",                  "4ms_LED:LED_Dual_SMD-4P"),
        ("Red 3mm TH",                      "4ms_LED:Red_3mm_TH"),
        ("White 3mm TH",                    "4ms_LED:White_3mm_TH"),
        ("Green 5mm TH",                    "4ms_LED:Green_5mm_TH"),
        ("Blue 3mm TH",                     "4ms_LED:Blue_3mm_TH"),
    ],
    "Button": [
        ("RGB 7mm Cap",                     "4ms_Switch:Button_SPST_RGB_7mmCap"),
        ("RGB 5.4mm Cap",                   "4ms_Switch:Button_SPST_RGB_5.4mmCap"),
        ("RGB 9mm Cap",                     "4ms_Switch:Button_SPST_RGB_9mmCap"),
        ("DPDT Orange Latching",            "4ms_Switch:Button_DPDT_Orange_Latching"),
        ("DPDT White Momentary",            "4ms_Switch:Button_DPDT_White_Mom"),
        ("PKS-01L-X",                       "4ms_Switch:Button_PKS-01L-X"),
        ("PKS-01 Black",                    "4ms_Switch:Button_PKS-01-BK"),
        ("PB20B",                           "4ms_Switch:Button_PB20B"),
        ("TL1105SPF Tactile SMT",           "4ms_Switch:Button_TL1105SPF160Q1RBLK"),
        ("TL1105JAF RA with Cap",           "4ms_Switch:Button_TL1105JAF160Q1RBLK"),
        ("PTS526 SMT Tactile",              "4ms_Switch:SW_Push_PTS526 SM15 SMTR2 LFS"),
        ("PTS810",                          "4ms_Switch:Button_PTS810"),
        ("B3F-4055",                        "4ms_Switch:Button_B3F-4055"),
        ("1TS009A",                         "4ms_Switch:Button_1TS009A"),
        ("SPST Momentary TS21",             "4ms_Switch:Button_SPST_Mom_TS21"),
        ("Tactile Pins 1+3 Shorted",        "4ms_Switch:TactSwitch_Pins13Shorted"),
    ],
    "Switch": [
        ("Toggle SPDT Sub-Mini 3-pos",      "4ms_Switch:Toggle_SPDT_SubMini_3pos"),
        ("Toggle SPDT Sub-Mini 2-pos",      "4ms_Switch:Toggle_SPDT_SubMini_2pos"),
        ("Encoder Rotary 11mm D-Shaft",     "4ms_Switch:Encoder_Rotary_11mm_SPST_DShaft"),
        ("Encoder Rotary 11mm PEC11R",      "4ms_Switch:Encoder_Rotary_11mm_SPST_PEC11R"),
        ("Encoder Rotary 12mm 24-Det",      "4ms_Switch:Encoder_Rotary_12mm_24DET_HollowKnurled"),
        ("Rocker 4-pin",                    "4ms_Switch:Rocker_4KD1R202A02RS"),
        ("Rocker 3-pin",                    "4ms_Switch:Rocker_3KD1R202A02RS"),
        ("DIP 2-pos",                       "4ms_Switch:SW_DIP_x02_CTS_219-2MST"),
        ("DIP 3-pos",                       "4ms_Switch:SW_DIP_x03_CTS_219-3MST"),
        ("Rotary 3-pos 6-pin",              "4ms_Switch:SW_Rotary3x6"),
        ("Slide SPST",                      "4ms_Switch:SPST_Slide_AS11CH"),
        ("Slide DPDT",                      "4ms_Switch:Slide_DPDT_SS22D06"),
    ],
    "Standoff": [
        ("M3x10mm Hex WA-SNTI",             "4ms_Hardware:Standoff_WA-SNTI_M3x10mm_Hex6mm"),
        ("M3x6mm Hex WA-SNTI",              "4ms_Hardware:Standoff_WA-SNTI_M3x6mm_Hex6mm"),
        ("M3x15mm Hex WA-SNTI",             "4ms_Hardware:Standoff_WA-SNTI_M3x15mm_Hex6mm"),
        ("Mounting Post Base Support",      "4ms_Hardware:Standoff_Mounting-Post_Base-Support"),
        ("Nylon Spacer 11mm",               "4ms_Hardware:Spacer Nylon, Unthreaded, Height=11mm, ID {gt}= 3mm, OD {lt} 6mm"),
        ("Mounting Hole M3 (no pad)",       "Mechanical:MountingHole"),
    ],
    "Connector": [
        ("USB-C Molex 2171790001",          "4ms_Connector:USB-C_Receptacle_Molex_2171790001"),
        ("USB-C AdamTech",                  "4ms_Connector:USB-C_Receptacle_AdamTech_USB-C31-S-VT-CS4-BK-PP"),
        ("USB-C GCT USB4730",               "4ms_Connector:USB-C_Receptacle_GCT_USB4730-GF-A"),
        ("USB Micro B",                     "4ms_Connector:USB_B_Micro_10118194-0011LF"),
        ("microSD Vertical TH",             "4ms_Connector:microSDCon_Vert_TH_PJS008U-3000"),
        ("microSD SMT",                     "4ms_Connector:microSDCon_SMT_104031-0811"),
    ],
    "Silk": [
        ("Silkscreen Label",                ""),
    ],
}

BLANK_ROWS = 50   # pre-formatted empty rows ready to fill

# ---------------------------------------------------------------------------
wb = Workbook()
ws      = wb.active
ws.title = "Coordinates"
ws_opts = wb.create_sheet("Options")
ws_lkup = wb.create_sheet("SymbolLookup")
ws_lkup.sheet_state = "hidden"

# -- SymbolLookup (hidden): flat Subtype → KiCad Symbol table
ws_lkup.cell(1, 1, "Subtype").font     = Font(bold=True)
ws_lkup.cell(1, 2, "KiCad Symbol").font = Font(bold=True)
lkup_row = 2
for type_opts in OPTIONS.values():
    for label, sym in type_opts:
        ws_lkup.cell(lkup_row, 1, label)
        ws_lkup.cell(lkup_row, 2, sym)
        lkup_row += 1
ws_lkup.column_dimensions["A"].width = 35
ws_lkup.column_dimensions["B"].width = 55

# -- Options sheet: one column per type for INDIRECT dropdown
type_to_col = {}
for col_idx, (type_name, type_opts) in enumerate(OPTIONS.items(), start=1):
    col_letter = get_column_letter(col_idx)
    type_to_col[type_name] = col_letter
    ws_opts.cell(1, col_idx, type_name).font = Font(bold=True)
    for row_idx, (label, _) in enumerate(type_opts, start=2):
        ws_opts.cell(row_idx, col_idx, label)
    ws_opts.column_dimensions[col_letter].width = 30

# Named ranges for INDIRECT
for type_name, col_letter in type_to_col.items():
    n = len(OPTIONS[type_name])
    ref = (f"{quote_sheetname('Options')}!"
           f"${col_letter}$2:${col_letter}${n + 1}")
    wb.defined_names[type_name] = DefinedName(name=type_name, attr_text=ref)

# -- Styles
thin     = Side(style="thin", color="CCCCCC")
cell_bdr = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(bold=True, color="FFFFFF", size=10)
AUTO_FILL = PatternFill("solid", fgColor="EAF0FB")
REF_FILL  = PatternFill("solid", fgColor="FFF2CC")
EMPTY_FILL = PatternFill("solid", fgColor="FAFAFA")

# -- Headers
# A=Ref  B=Display Name  C=X  D=Y  E=Component Type  F=Subtype  G=KiCad Symbol  H=Notes
COLS = [
    ("Ref",            "A", 10),
    ("Display Name",   "B", 28),
    ("X",              "C", 11),
    ("Y",              "D", 11),
    ("Component Type", "E", 18),
    ("Subtype",        "F", 32),
    ("KiCad Symbol",   "G", 45),
    ("Notes",          "H", 35),
]
for col, (header, col_letter, width) in enumerate(COLS, start=1):
    c = ws.cell(row=1, column=col, value=header)
    c.fill      = HDR_FILL
    c.font      = HDR_FONT
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border    = cell_bdr
    ws.column_dimensions[col_letter].width = width

ws.row_dimensions[1].height = 22

# -- Pre-format blank rows
for row_idx in range(2, BLANK_ROWS + 2):
    for col in range(1, 9):
        c = ws.cell(row_idx, col)
        c.border = cell_bdr
        if col == 1:
            types  = '"Pot","Jack","LED","Button","Switch","Standoff","Connector","Silk"'
            prefix = '"POT","J","LED","BUT","SW","H","J",""'
            c.value = (
                f'=IF(E{row_idx}="","",IFERROR(CHOOSE(MATCH(E{row_idx},{{{types}}},0),{prefix}),"")'
                f'&TEXT(COUNTIF($E$2:E{row_idx},E{row_idx}),"00"))'
            )
            c.fill  = REF_FILL
            c.font  = Font(color="999999", italic=True)
        elif col == 7:
            c.fill = AUTO_FILL
            c.value = f'=IFERROR(VLOOKUP(F{row_idx},SymbolLookup!$A:$B,2,0),"")'
            c.font  = Font(color="888888", italic=True)
        else:
            c.fill = EMPTY_FILL
        if col in (3, 4):
            c.number_format = "0.000"
            c.alignment = Alignment(horizontal="right")

# -- Data validation: Component Type (col E)
type_list = ",".join(OPTIONS.keys())
dv_type = DataValidation(
    type="list",
    formula1=f'"{type_list}"',
    allow_blank=True,
    showDropDown=False,
    showErrorMessage=True,
    errorTitle="Invalid type",
    error=f"Choose one of: {type_list}",
)
ws.add_data_validation(dv_type)
dv_type.sqref = "E2:E500"

# -- Data validation: Subtype (col F) — dependent on col E via INDIRECT
dv_sub = DataValidation(
    type="list",
    formula1="INDIRECT($E2)",
    allow_blank=True,
    showDropDown=False,
    showErrorMessage=False,
)
ws.add_data_validation(dv_sub)
dv_sub.sqref = "F2:F500"

# -- Conditional formatting: Ref cell turns orange when KiCad Symbol is filled but Ref is empty
orange_fill = PatternFill("solid", fgColor="FF9900")
ws.conditional_formatting.add(
    "A2:A500",
    Rule(type="expression",
         formula=['AND($G2<>"",$A2="")'],
         dxf=DifferentialStyle(fill=orange_fill))
)

ws.freeze_panes = "B2"

# ---------------------------------------------------------------------------
out = os.path.join(HERE, "Component Placement Template.xlsx")
wb.save(out)
print(f"Saved: {out}")
print(f"Types: {len(OPTIONS)}  |  Total subtypes: {sum(len(v) for v in OPTIONS.values())}")
