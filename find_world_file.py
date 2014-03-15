#mike mommsen
import os
import shutil

# list of extensions for world files
# we can add more later, or maybe look for "w" in the extension
WORLDNAMES = ['.jgw', '.jgwx', '.tfw']

def findWorldFiles(indir):
    """finds all of the files that have a world file in the indir and returns a list of the basenames"""
    mylist = []
    allfiles = [os.path.splitext(x) for x in os.listdir(indir)]
    for base, extension in allfiles:
        if extension in WORLDNAMES:
            outname = os.path.join(indir, base)
            mylist.append(outname)
    return mylist

# we should also think about os.walk, but I don't really love it all that much to be honest    
def walkDir(indir):
    """takes a directory, digs through it and its subdirs and returns files with world files"""
    mylist = []
    allfiles = [os.path.join(indir, x) for x in os.listdir(indir)]
    for x in allfiles:
        if os.path.isdir(x):
            mylist += walkDir(x)
        else:
            basepath, filename = os.path.split(x)
            baseFileName, extension = os.path.splitext(filename)
            if extension in WORLDNAMES:
                outname = os.path.join(basepath, baseFileName)
                mylist.append(outname)
    return mylist
    
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
    """"""
    indir = r'I:\Aerials\MO\County\Pemiscot\Pemiscot59' #sys.argv[1]
    outdir = r'J:\GIS_Data\Working-MikeM\production\142358\1959' #sys.argv[2]
    worldfiles = findWorldFiles(indir)
    copyFromBaseNames(indir, outdir, worldfiles)
    print True

if __name__ == "__main__":
    main()
