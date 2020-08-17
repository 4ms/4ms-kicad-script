import re
import os
import sys
import csv
from pathlib import Path
import datetime

DEBUG_LIMIT_LINES = 100000

old_lib_header = "Old Library"
new_lib_header = "New Library"
ref_header = "References"
filename_header = "Sch File"

#Global cache of files to minimize disk I/O
cached_sch_files = {}
errlog = ""

def process(csvfile):
    with open(csvfile) as f:
        reader = csv.DictReader(f)
        #print(reader.fieldnames)
        rows_read = 0
        for row in reader:
            rows_read += 1
            if rows_read>DEBUG_LIMIT_LINES:
                print("DEBUG mode: aborting after "+str(DEBUG_LIMIT_LINES)+" lines in the csv file.")
                break
            old_lib = row[old_lib_header]
            new_lib = row[new_lib_header]
            refs = row[ref_header]
            filename = row[filename_header]
            dirname = findDirname(filename)

            refslist = re.split(r',\s*', refs)
            for ref in refslist:
                print("Attempting to change the library of ref "+ref+" in "+dirname+"/*.sch to "+new_lib+", from "+old_lib)
                replaceLibByRefInDir(ref, dirname, old_lib, new_lib)

        flush_files()
    return

def findDirname(path):
    if os.path.isdir(path):
        if path[-1:] != '/':
            path += '/'
    return os.path.dirname(path)

def replaceLibByRefInDir(ref, dirname, old_lib, new_lib):
    global errlog
    found_it = False
    for schfile in Path(dirname).glob('*.sch'):
        if schfile not in cached_sch_files.keys():
            with open(schfile) as f:
                cached_sch_files[schfile] = f.read();
 
        newdat, cnt = replaceLibByRefInFile(old_lib, new_lib, ref, cached_sch_files[schfile])
        if cnt>0:
            cached_sch_files[schfile] = newdat
            print("Found in file "+schfile.name+". Replaced occurances: "+str(cnt))
            found_it = True

    if found_it is False:
        err = "ERROR: Ref "+ref+" with library "+old_lib+" not found in any .sch file in "+dirname+". Please manually change this part's lib to "+new_lib
        errlog += err + "\n"
        print(err)

    return

def replaceLibByRefInFile(old_lib, new_lib, ref, sch):
    #Search by Library line (sometimes kicad sets the ref to X?, so this doesn't always work
    newsch, cnt = re.subn(r'(?m)^L '+old_lib+r' ' + ref + r'\n', r'L '+new_lib+r' '+ref+r'\n', sch)
    if cnt == 0:
        #Search by RefDes field line (Not sure if F 0 is guarenteed to be RefDes, but seems to be?)
        newsch, cnt = re.subn(r'(?m)^L '+old_lib+r' ('+ref[0]+r'\?(?:\n[^\$].+)+\nF 0 "'+ref+r'" )', r'L '+new_lib+r' \1' , sch)
    return newsch, cnt

def flush_files():
    for filename, filedat in cached_sch_files.items():
        with open(filename, "w") as f:
            f.write(filedat)
            print("Wrote file: " + filename.name)
    return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csvfile = sys.argv[1]
        process(csvfile)
    else:
        print("Please specify a csv file")

    with open("symbol_rename.err", "a") as log:
        tm = str(datetime.datetime.now())
        log.write("renameSchSyms.py ran: "+tm+"\n")
        log.write(errlog)
    print("Wrote error log to symbol_rename.err")

