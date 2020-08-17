import re

class Convert:
    def __init__(self, old_lib, old_val, new_lib):
        self.old_lib = old_lib
        self.old_val = old_val
        self.new_lib = new_lib

    def convertSchematic(self, schdat):
        newsch = re.sub(r'(?m)^L ' + self.old_lib + r' ([^\$]+(?:\n[^\$].+)+\nF 1 "'+self.old_val+r'" )',
                r'L ' + self.new_lib + r' \1',
                schdat)
        return newsch
