import string
from pandas import DataFrame, Series
from os.path import join
from glob import glob
from sys import prefix
from pathlib import PurePath

from primeDirectory import primeDirectory
from fsUtils import isDir, setDir, setFile, mkDir, isFile, setSubDir, dirUtil, fileUtil
from listUtils import getFlatList
from timeUtils import timestat
from searchUtils import findDirs, findSubDirs
from fileIO import fileIO
    

###############################################################################################################################
#
# My Album Path Mapping
#
###############################################################################################################################
class myAlbumPathMapping:
    def __init__(self, debug=False):
        self.directoryMapping = {}
        self.directoryMapping["BoxSet"]  = ["BoxSet"]
        self.directoryMapping["Bootleg"] = ["Bootleg"]
        self.directoryMapping["Mix"]     = ["Mix", "MixTape"]
        self.directoryMapping["Media"]   = ["Media"]
        self.directoryMapping["Unknown"] = ["Unknown"]
        self.directoryMapping["Random"]  = ["Random"]
        self.directoryMapping["Todo"]    = ["Todo"]
        self.directoryMapping["Rename"]  = ["Album", "Title"]
        self.directoryMapping["Match"]   = ["Match"]
        self.directoryMapping["Live"]    = ["Live", "LiveSet"]
        
        ## This one is special
        self.directoryMapping["UnMatched"] = []
        
    def getMappings(self):
        return self.directoryMapping.keys()
    
    def getOtherMappings(self):
        return [x for x in self.getMappings() if x not in ["Match", "UnMatched"]]
            
    def getMapping(self, name):
        return self.directoryMapping.get(name)
        
    def getMappingDirs(self):
        return getFlatList(self.directoryMapping.values())
    
    
    
###############################################################################################################################
#
# My Artist Albums
#
###############################################################################################################################
class myArtistAlbumPathData:
    def __init__(self, dirval, debug=False):
        self.dirval = dirval
        self.albums = []
        
    def albumInfo(self, album):
        return dirUtil(album).path
        
    def addAlbums(self, albums):
        if isinstance(albums, list):
            self.albums += [self.albumInfo(album) for album in albums]
        
    def addAlbum(self, album):
        if isinstance(album, str):
            self.albums.append(self.albumInfo(album))
        
        
        
###############################################################################################################################
#
# My Artist Albums
#
###############################################################################################################################
class myArtistPathData:
    def __init__(self, artistName, artistPrimeDirs, count=False, debug=False):
        super().__init__()
        self.artistName       = artistName
        self.artistPrimeDir   = artistPrimeDirs[0] if (isinstance(artistPrimeDirs,list) and len(artistPrimeDirs) == 1) else artistPrimeDirs
        self.count            = count
        self.debug            = debug
        
        self.mdirmap          = myAlbumPathMapping()
        self.albumData        = {albumType: None for albumType in self.mdirmap.getMappings()}
            

    ################################################################################################
    # Produce Dictionary of Results
    ###############################################################################################
    def getDict(self):
        if self.count is True:
            retval = {k: [v.getNumAlbums(),v.getNumFiles()] for k,v in self.albumData.items()}
        else:
            retval = {k: v.getNumAlbums() for k,v in self.albumTypeData.items()}            
        return retval
                
        
    ################################################################################################
    # Album Setter
    ################################################################################################
    def setArtistAlbumsPathData(self):
        self.setMyMatchedMusicAlbums()
        self.setMyUnmatchedMusicAlbums()
        self.setMyOtherMusicAlbums()


    ################################################################################################
    # Matched
    ################################################################################################
    def getMyMatchedMusicAlbums(self, dirval):
        return getFlatList([[p for p in findSubDirs(setDir(dirval,mdirval), "*")] for mdirval in self.mdirmap.getMapping("Match")])
    
    def setMyMatchedMusicAlbums(self):
        dirval    = self.artistPrimeDir
        musicdata = myArtistAlbumPathData(dirval=dirval)
        musicdata.addAlbums(self.getMyMatchedMusicAlbums(dirval))
        self.albumData["Match"] = musicdata
            
            
    ################################################################################################
    # Unmatched
    ################################################################################################
    def getMyUnmatchedMusicAlbums(self, dirval):
        return [x for x in findDirs(dirval) if dirUtil(x).name not in self.mdirmap.getMappingDirs()]
    
    def setMyUnmatchedMusicAlbums(self):
        dirval    = self.artistPrimeDir
        musicdata = myArtistAlbumPathData(dirval=dirval)
        musicdata.addAlbums(self.getMyUnmatchedMusicAlbums(dirval))
        self.albumData["UnMatched"] = musicdata


    ################################################################################################
    # Other Directory Mapping
    ################################################################################################
    def getMyOtherMusicAlbums(self, dirval, mname):
        return getFlatList([[p for p in findDirs(setDir(dirval,mdirval))] for mdirval in self.mdirmap.getMapping(mname)])
        
    def setMyOtherMusicAlbums(self):
        dirval    = self.artistPrimeDir
        for mname in self.mdirmap.getOtherMappings():
            musicdata = myArtistAlbumPathData(dirval=dirval)
            musicdata.addAlbums(self.getMyOtherMusicAlbums(dirval, mname))
            self.albumData[mname] = musicdata
        
        

    
###############################################################################################################################
#
# My Music Base
#
###############################################################################################################################
class myMusicPathData:
    def __init__(self, musicDir="/Volumes/Piggy/Music/Matched", install=False, debug=False):
        self.debug     = debug
        self.musicDir  = musicDir
            
        print("="*25,"myMusicPathData({0})".format(musicDir),"="*25)
        
        ### My Music Directory Names
        self.artistAlbums = None
        self.pd = primeDirectory()
        self.pdDirs = self.pd.getPrimeDirectories()
        self.musicDataDir = setDir(prefix, 'music')
        self.initializeData() if install is False else self.installData()
    
    def initializeData(self):
        return
        self.summary(self.getData(fast=True, local=False))
        
    def installData(self):
        if not isDir(self.musicDataDir):
            print("Install: Making Prefix Dir [{0}]".format(self.musicDataDir))
            mkDir(self.musicDataDir)
        if not isFile(self.getFilename(local=False)):
            print("Install: Creating Prefix Data From Local Data")
            fileIO().save(idata=fileIO().get(self.getFilename(local=True)), ifile=self.getFilename(local=False))
            
    def getSummary(self, mmpdData=None):
        mmpdData = self.artistAlbums if mmpdData is None else mmpdData
        if mmpdData is not None:
            mmpdDF = DataFrame({artistName: Series({albumType: len(albumTypeData.albums) for albumType,albumTypeData in artistData.albumData.items()}) for artistName,artistData in mmpdData.items()}).T
            return mmpdDF
        return None
            
    
    ###################################################################################################
    # Find Artist Albums and Organize
    ###################################################################################################
    def getFilename(self, local):
        fname = "musicPathData.p"
        fname = fname if local is True else setFile(self.musicDataDir, fname)
        return fname
    
    def saveData(self, artistAlbums=None, local=False):
        artistAlbums = self.artistAlbums if artistAlbums is None else artistAlbums
        savename = self.getFilename(local)
        fileIO().save(idata=artistAlbums, ifile=savename)
        
    def getData(self, local=False):
        savename = self.getFilename(local)
        return fileIO().get(savename)
        
    
    ###################################################################################################
    # Find Artist Albums and Organize
    ###################################################################################################
    def getArtistPathData(self, artistName, artistPrimeDirs=None):
        artistPrimeDirs = [self.getArtistMusicPath(artistName)] if artistPrimeDirs is None else artistPrimeDirs
        mapd = myArtistPathData(artistName=artistName, artistPrimeDirs=artistPrimeDirs, count=False)
        mapd.setArtistAlbumsPathData()
        return mapd
        
    def findMyMusic(self, primeDir=None, artistName=None):        
        artistAlbums    = {}
        if primeDir is None and artistName is None:
            ts = timestat("Find PrimeDir Artist Paths")
            pdPaths       = {pd: pdpath for pd,pdpath in {pd: setDir(self.musicDir,pd) for pd in self.pdDirs}.items() if dirUtil(pdpath).isDir()}
            pdArtistPaths = {pd: findDirs(pdpath) for pd,pdpath in pdPaths.items()}
            artistPaths   = {fsap.name: fsap.path for fsap in [dirUtil(ap) for ap in getFlatList(pdArtistPaths.values())]}
            artistAlbums  = {artistName: self.getArtistPathData(artistName,artistPath) for artistName,artistPath in artistPaths.items()}
            print("  Found {0} Artists From {1} Prime Directories".format(len(artistAlbums), len(pdArtistPaths)))
            ts.stop()
        elif primeDir is not None:
            ts = timestat("Finding All Artist Albums From [{0}] Prime Directory".format(primeDir))
            pdPaths       = {pd: pdpath for pd,pdpath in {pd: setDir(self.musicDir,pd) for pd in [primeDir]}.items() if dirUtil(pdpath).isDir()}
            pdArtistPaths = {pd: findDirs(pdpath) for pd,pdpath in pdPaths.items()}
            artistPaths   = {fsap.name: fsap.path for fsap in [dirUtil(ap) for ap in getFlatList(pdArtistPaths.values())]}
            artistAlbums  = {artistName: self.getArtistPathData(artistName,artistPath) for artistName,artistPath in artistPaths.items()}
            print("  Found {0} Artists From [{1}] Prime Directory".format(len(artistAlbums), primeDir))
            ts.stop()
        elif artistName is not None:
            ts = timestat("Finding [{0}] Artist Albums".format(artistName))
            artistAlbums = self.getArtistPathData(artistName)
            ts.stop()
        
        self.artistAlbums = artistAlbums
        return artistAlbums
    
    
    ###################################################################################################
    # Return Data
    ###################################################################################################
    def getArtistPrimeDir(self, artistName):
        return setDir(self.musicDir, self.pd.getPrimeDirectory(artistName))
                      
    def getArtistMusicPath(self, artistName):
        artistPrimeDir = self.getArtistPrimeDir(artistName)
        artistMusicDir = setDir(artistPrimeDir, artistName)
        artistMusicDir = artistMusicDir if dirUtil(artistMusicDir).isDir() else None
        return artistMusicDir
        
    def getArtists(self):
        return list(self.artistAlbums.keys()) if isinstance(self.artistAlbums,dict) else None