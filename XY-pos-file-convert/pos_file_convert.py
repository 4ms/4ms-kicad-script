import os
import sys
import csv
import re
output_fields = ["Designator","Mid X","Mid Y","Layer","Rotation"]

def writeCSV(comp_data, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=output_fields, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
        wr.writeheader()
        for comp in comp_data:
            wr.writerow(comp)

def readCSV(csv_filename):
    comp_data = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comp_data.append(row)
    return comp_data

def convertToJLCPCB(kicad_comp_data):
    jlcpcb_comp_data = []
    for kcomp in kicad_comp_data:
        jcomp = {}
        jcomp["Designator"] = kcomp['Ref']
        jcomp["Mid X"] = kcomp['PosX']
        jcomp["Mid Y"] = kcomp['PosY']
        jcomp["Layer"] = kcomp['Side']
        jcomp["Rotation"] = kcomp['Rot']
        jlcpcb_comp_data.append(jcomp)
    return jlcpcb_comp_data

def doConvert(input_filename, output_filename):
    kicad_comp_data = readCSV(input_filename)
    jlcpcb_comp_data = convertToJLCPCB(kicad_comp_data)
    writeCSV(jlcpcb_comp_data, output_filename)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        print("Reading from: "+input_filename)
        if len(sys.argv) > 2:
            output_filename = sys.argv[2]
            print("Will output to: " + output_filename)
        else:
            output_filename = input_filename + "-jlcpcb.csv"
            print("No output file specified, will output to: " + output_filename)
    else:
        print("""
Please specify a Kicad .pos file (footprint position file) as the first argument.
Optionally, you may also specify an output file name.

python3 pos_file_convery.py KicadProject-all-pos.csv
""")
    
    doConvert(input_filename, output_filename)

