#mike mommsen
import os
import shutil
from itertools import groupby

# list of extensions for world files
# we can add more later, or maybe look for "w" in the extension
WORLDNAMES = ['.jgw', '.jgwx', '.tfw', '.tfwx']
    
def findWorldFiles(inlist):
    """takes a list of files and returns the ones that have a world file"""
    # the function to group photos into groups based off of basename (not extension
    keyfunc = lambda x: x.split('.')[0]
    mylist = []
    # sort the inlist just to make sure
    # i think that this is needed for groupby to work
    sortedinlist = sorted(inlist)
    # create a groupby object to loop through
    grouper = groupby(sortedinlist, keyfunc)
    # loop through the different basenames
    for key, g in grouper:
        # for each basename loop through the files that have that basename
        for x in g:
            # find the extension for the file
            basename, extension = os.path.splitext(x)
            # if one of the files is a worldfile
            if extension in WORLDNAMES:
                # add all of the files to mylist
                mylist += list(g)
                # and leave the inner loop, going back to looping through basenames
                break
    return mylist

def walkDir(indir):
    """"""
    # start a blank list
    mylist = []
    # ive always found os.walk to be strange, but it works hee
    for root, dirs, files in os.walk(indir):
        #
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
    
def copyFileListHierarchy(indir, outdir):
    """"""
    mylist = []
    for root, dirs, files in os.walk(indir):
        basefiles = findWorldFiles(root, files)
        if basefiles:
            outfilename = root[len(indir):]
            outpath = os.path.join(outdir, outfilename)
            os.mkdir(outpath)
            copyFileList(basefiles, outpath)
            print True
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
    indir = r'I:\Aerials\MD\County\Harford' #sys.argv[1]
    outdir = r'J:\GIS_Data\Working-MikeM\production\maryland\Harford\georeferenced_aerials' #sys.argv[2]
    readmode = 'r'#'r' | '' #sys.argv[3]
    writemode = ''#'r' | '' # sys.argv[4]
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    allfiles = os.listdir(indir)
    if readmode == 'r':
        worldfiles = walkDir(indir)
    else:
        allfiles = os.listdir(indir)
        worldfiles = findWorldFiles(allfiles)
    print worldfiles
    copyFileList(worldfiles, outdir)
    print True

if __name__ == "__main__":
    main()
