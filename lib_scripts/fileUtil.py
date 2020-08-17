import os

def loadFileList(file_name_list):
    """ Given a list of file names,
        Read all the files and
        Return a dictionary {Filename1: filedata1, Filename2: filedata2, ...}
    """
    dat = {}
    for fil in file_name_list:
        with open(fil) as f:
            print("Reading file: "+fil)
            dat[fil] = f.read()
    return dat

def loadFilesWithExt(sourcedir, extension):
    """ Given a directory and file extension
        Read all the files and
        Return a dictionary {Filename1: filedata1, Filename2: filedata2, ...}
    """
    file_list = [sourcedir+f for f in os.listdir(sourcedir) if f.endswith(extension)]
    file_dict = loadFileList(file_list)
    return file_dict

def writeFiles(file_dict):
    """ Given a dict of file data: {Filename: filedata}
        (Over)write the files 
    """
    for file_name, file_data in file_dict.items():
        with open(file_name, "w") as f:
            f.write(file_data)
            print("Writing file: "+file_name)

def appendSlash(pathname):
    if pathname[-1:] != "/":
        pathname = pathname+"/"
    return pathname
