from pandas import DataFrame
from fsUtils import isDir, setDir
from fileUtils import getDirBasics, getBaseFilename
from listUtils import getFlatList
from searchUtils import findDirs, findAll, findNearest
from difflib import SequenceMatcher
from unicodedata import normalize
from os.path import join
from glob import glob
from timeUtils import clock, elapsed



def getOrganizedDBArtistAlbums(vals, dbKey):
    retval = {}
    for key in getAlbumTypes(dbKey, keys=True):
        albumTypes = getAlbumTypes(dbKey, key)        
        retval[key] = []
        for albumType in albumTypes:
            if vals.get(albumType) is not None:
                retval[key] += vals[albumType].values()
    return retval




def getArtistAlbums(discdf, idx):
    if not isinstance(discdf, DataFrame):
        raise ValueError("Not a DataFrame")
    
    try:
        artistAlbumsData = discdf[discdf.index == idx]
        artistAlbums     = artistAlbumsData["Albums"].to_dict().get(idx)
    except:
        return {}
        
    return artistAlbums


def getArtistIDX(artistMapData, db, discdf, debug=False):
    if not isinstance(artistMapData, dict):
        raise ValueError("No Artist Map Data")
    if not isinstance(discdf, DataFrame):
        raise ValueError("Not a DataFrame")        
    if not isinstance(artistMapData, dict):
        raise ValueError("artistMapData is not a DB!")

    if debug:
        print("ArtistMapData: {0} and DB: {1}".format(artistMapData, db))
    
    try:
        aMapData = artistMapData.get(db)
    except:
        if debug:
            print("DataBase [{0}] does not exist in artist map data".format(db))
        return None

    try:
        idx = aMapData.get('ID')
    except:
        if debug:
            print("ID and DataBase [{0}] does not exist in artist map data".format(db))
        return None
    
    ## Check
    if idx not in list(discdf.index):
        raise ValueError("ID {0} for {1} is not in the Index of the main DataFrame!".format(idx, db))
    
    return idx

def getArtistIDDBCounts(dbIDData):
    if isinstance(discogsIDData, DataFrame):
        return dbIDData.shape[0]
    return 0

def printArtistIDs(artistName, discogsArtistIDX, allmusicArtistIDX):
    print('\t{0: <40}{1: <15}{2: <15}'.format(artistName,str(discogsArtistIDX),str(allmusicArtistIDX)))

def printArtistIDDBResults(artistName, discogsIDData, allmusicIDData):
    print("\t{0: <40}{1: <15}{2: <15}".format("", 
                                              getArtistIDDBCounts(discogsIDData),
                                              getArtistIDDBCounts(allmusicIDData)))
    

def getOrganizedArtistAlbums(vals, dbKey):
    if vals is None or not isinstance(vals, dict):
        return {}
    retval = {}
    for key in [1,2,3,4]:
        albumTypes = getAlbumTypes(dbKey, key)        
        retval[key] = []
        for albumType in albumTypes:
            if vals.get(albumType) is not None:
                retval[key] += vals[albumType].values()
    return retval





def getMultiMatchedDirs():
    baseDirs = ["/Volumes/Music/Multi/Matched", "/Volumes/Music/Jazz/Matched"]
    baseDirs = ["/Volumes/Music/Jazz/Matched"]
    return baseDirs




def getArtistNameDirvalsMap(artistName):
    primeDir   = getPrimeDirectory(artistName)
    dirvals    = []
    for matchedDir in getMatchedDirs():
        primeDirVal = setDir(matchedDir, primeDir)
        possibleDir = setDir(primeDirVal, normalize('NFC', artistName), forceExist=False)
        if isDir(possibleDir):
            dirvals.append(possibleDir)
    return dirvals




def getMyArtistNames():
    artistNames = []
    for primeDir in getPrimeDirectories():
        artistPrimeDirMap = getArtistPrimeDirMap(primeDir)
        artistNames += artistPrimeDirMap.keys()
    print("Found {0} Artists In My Matched Directories".format(len(artistNames)))



def analyzePartiallyUnknownArtists(matchedResults):
    start, cmt = clock("Finding Possible New Matches")

    num = 2
    cutoff = 0.50


    discogMediaNames   = ['Albums', 'Singles & EPs', 'Compilations', 'Videos', 'Miscellaneous', 'Visual', 'DJ Mixes']
    allmusicMediaNames = ['Album']
    myMediaNames       = ['Random', 'Todo', 'Match', 'Title', 'Singles']

    additions = {}

    print("{0: <40}{1}".format("Artist", "# of Albums"))
    for i,(artistName, unknownVals) in enumerate(matchedResults["PartiallyUnknown"].items()):
        print("{0: <40}".format(artistName))
        for dbKey in dbKeys:
            key = dbKey['Key']
            if key != "AceBootlegs":
                continue
            if unknownVals.get(key) is not None:
                dirvals = unknownVals[key]
                print("{0: <40}{1}".format(artistName, key))

                myMusicAlbums = []
                for dirval in dirvals:
                    myMusicAlbums += getMyMusicAlbums(dirval, returnNames=True) + getMyMatchedMusicAlbums(dirval) + getMyUnknownMusicAlbums(dirval)
                if len(myMusicAlbums) == 0:
                    continue
                print("{0: <40}There are {1} my albums".format(artistName,len(myMusicAlbums)))


                ## Find Possible IDs
                possibleIDs = findPossibleArtistIDs(artistName, artistNameToID[key], artists[key], num, cutoff)
                print("     Possible IDs ===>",len(possibleIDs))
                maxRat = None
                for possibleID in possibleIDs:
                    print("\t{0: <15}".format(possibleID), end="")
                    artistAlbums = getRowData(artistAlbumsDB[key], rownames=possibleID)['Albums']
                    artistAlbums = getFlattenedArtistAlbums(artistAlbums)          
                    print("\t{0: <10}".format(len(artistAlbums)), end="")


                    ## Find overlapping albums
                    retval = getBestAlbumsMatch(artistAlbums, myMusicAlbums, cutoff=cutoff, debug=False)                
                    print("\t",round(retval,2), end="")
                    if retval > cutoff:
                        if maxRat is None:
                            maxRat = retval
                        if retval < maxRat:
                            print("")
                            continue
                        maxRat = retval
                        if additions.get(artistName) is None:
                            additions[artistName] = {}
                        additions[artistName][key] = {"Score": retval, "Value": {'ID': possibleID, 'Name': None}}

                        print("\t{0: <15} is a match!".format(possibleID))
                    else:
                        print("")

    print("")
    print("Found {0} new matches".format(len(additions)))
    elapsed(start, cmt)
    
    return additions