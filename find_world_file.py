#mike mommsen
import os
import shutil
WORLDNAMES = ['.jgw', '.jgwx', '.tfw'] # add more later

def findWorldFiles(indir):
    """"""
    mylist = []
    os.chdir(indir)
    allfiles = [os.path.splitext(x) for x in os.listdir('.')]
    for base, extension in allfiles:
        if extension in WORLDNAMES:
            mylist.append(base)
    return mylist
    
def walkDir(indir):
    """"""

def copyFromBaseNames(indir, outdir, baseNames):
    """"""
    allfiles = os.listdir('.') # pretty sure that dir is changed for us!!
    for x in allfiles:
        base = x.split('.')[0]
        if base in worldfiles:
            outpath = os.path.join(outdir, x)
            shutil.copyfile(x, outpath)

def main():
    """"""
    indir = r'I:\Aerials\MO\County\Pemiscot\Pemiscot59' #sys.argv[1]
    outdir = r'J:\GIS_Data\Working-MikeM\production\142358\1959' #sys.argv[2]
    worldfiles = findWorldFiles(indir)
    copyFromBaseNames(indir, outdir, worldfiles)
    print True

if __name__ == "__main__":
    main()
