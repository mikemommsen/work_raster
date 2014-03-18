#mike mommsen
import os
import shutil
from itertools import groupby

# list of extensions for world files
# we can add more later, or maybe look for "w" in the extension
WORLDNAMES = ['.jgw', '.jgwx', '.tfw', '.tfwx']
    
def findWorldFiles(inlist):
    """takes a list of files and returns the ones that have a world file"""
    keyfunc = lambda x: x.split('.')[0]
    mylist = []
    # lets check into if it has to be sorted or something like that
    grouper = groupby(inlist, keyfunc)
    for key, g in grouper:
        for x in g:
            basename, extension = os.path.splitext(x)
            if extension in WORLDNAMES:
                mylist += list(g)
                break
    return mylist

def walkDir(indir):
    """"""
    keyfunc = lambda x: x.split('.')[0]
    mylist = []
    for root, dirs, files in os.walk(indir):
        # create a group object that groups
        basefiles = findWorldFiles(files)
        fullnames = [os.path.join(root, x) for x in basefiles]
        mylist += fullnames
    return mylist

def copyFileList(inlist, outdir):
    """takes a list of files and copies them to the outdir leaving the names the same"""
    for x in inlist:
        basepath, filename = os.path.split(x)
        dst = os.path.join(outdir, filename)
        shutil.copy(x, dst)
    return True

# because we are doing the walk we should allow for a copy flat and a copy hierarchy option

def copyFromBaseNames(indir, outdir, baseNames):
    """takes a list of basenames and copys every extension of those files from indir to outdir"""
    allfiles = os.listdir(indir)
    for x in allfiles:
        base = x.split('.')[0]
        if base in worldfiles:
            src = os.path.join(indir, x)
            dst = os.path.join(outdir, x)
            shutil.copyfile(src, dst)

def main():
    # lets make this so we can run both one dir, or the entire
    """"""
    indir = r'I:\Aerials\CA\County\LosAngeles' #sys.argv[1]
    outdir = r'J:\GIS_Data\Working-MikeM\production\los_angeles' #sys.argv[2]
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    allfiles = os.listdir(indir)
    worldfiles = walkDir(indir)
    print worldfiles
    #fullpathworldfiles = [os.path.join(indir, x) for x in worldfiles]
    copyFileList(worldfiles, outdir)
    print True

if __name__ == "__main__":
    main()
