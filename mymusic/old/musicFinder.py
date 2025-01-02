from searchUtils import findDirsPattern, findWalkExt
from fileUtils import getBaseFilename, getFileBasics, getBasename
from fsUtils import setFile
from ioUtils import saveFile, getFile
from timeUtils import clock, elapsed
from musicBase import musicBase
from musicPath import pathBasics


##############################################################################################################################
# My Music
##############################################################################################################################
class musicFinder(musicBase):
    def __init__(self, debug=False):
        self.name = "mymusic"
        musicBase.__init__(self, debug=debug)
        
        self.pb = pathBasics()

        
    def findMusic(self, skips=[]):
        print(self.getMusicDirPaths())
        for idir in self.getMusicDirPaths():
            keep = True
            for skip in skips:
                if idir.find(skip) != -1:
                    print("SKIPPING {0}!!!".format(skip))
                    keep = False
            if keep is False:
                continue

            print("Checking {0}...".format(idir), end='   \t')
            files = findWalkExt(basedir=idir, ext=self.musicext)
            print("Found {0} files.".format(len(files)))
            retval = {ifile: self.pb.getPaths(ifile).getDict() for ifile in files}
            print("Processed {0} paths.".format(len(retval)))
            savename = setFile(self.getDBDir(), "Music-{0}.p".format(getBasename(idir)))
            saveFile(ifile=savename, idata=retval, debug=True)
            
            
    def getMusicDBs(self):
        files = findExt(basedir=self.getDBDir(), ext="*.p")
        print("Found {0} DB Files".format(len(files)))
        return files
    
    
    ##################################################################################
    # File Pathname Analysis
    ##################################################################################
    def findMusicDBPaths(self):        
        for idirfile in self.dbs:
            dbdata = {}
            print("Analyzing {0}".format(idirfile))
            data = getFile(idirfile)
            print("\tFound {0} mp3s".format(len(data)))
            for mp3 in data:
                pbc = self.pb.getPaths(mp3)
                dbdata[mp3] = pbc.getDict()
                            
            mclass = getBaseFilename(idirfile)
            savename = setFile(self.getDBDir(), "{0}-Paths.p".format(mclass))
            saveFile(ifile=savename, idata=dbdata, debug=True)
    
    
    ##################################################################################
    # File Tag Analysis
    ##################################################################################
    def findMusicDBTags(self):        
        for idirfile in self.getMusicListFiles():
            dbdata = {}
            print("Analyzing {0}".format(idirfile))
            data = getFile(idirfile)
            print("\tFound {0} mp3s".format(len(data)))
            start, cmt = clock("\t  Getting Tags...")
            for mp3 in data:                
                mid = mp3ID(mp3)
                dbdata[mp3] = mid.getInfo()

            elapsed(start, cmt)
            mclass = getBaseFilename(idirfile)
            savename = setFile(self.getDBDir(), "{0}-Tags.p".format(mclass))
            saveFile(ifile=savename, idata=dbdata, debug=True)