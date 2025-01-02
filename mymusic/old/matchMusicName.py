from ioUtils import getFile
from fsUtils import setDir, mkDir, isDir, moveDir

class myMusicName:
    def __init__(self, debug=False):
        self.debug = False
        
        self.abrv = {}
        self.abrv["AllMusic"]      = "AM"
        self.abrv["MusicBrainz"]   = "MC"
        self.abrv["Discogs"]       = "DC"
        self.abrv["AceBootlegs"]   = "AB"
        self.abrv["RateYourMusic"] = "RM"
        self.abrv["LastFM"]        = "LM"
        self.abrv["DatPiff"]       = "DP"
        self.abrv["RockCorner"]    = "RC"
        self.abrv["CDandLP"]       = "CL"
        self.abrv["MusicStack"]    = "MS"
        self.abrv["MetalStorm"]    = "MT"
        
        self.moveFilename = "myMusicAlbumMatch.yaml"
        

    def discConv(self, x):
        if x is None:
            return ""
        x = x.replace("/", "-")
        x = x.replace("¡", "")
        while x.startswith(".") and len(x) > 1:
            x = x[1:]
        x = x.strip()
        return x

        
    def formatAlbum(self, albumName, albumType):
        if albumType == 3:
            retval = albumName.replace("(Single)", "")
            retval = retval.replace("(EP)", "")
            retval = retval.strip()
            return retval
        return albumName
    
    
        
    def getMatchedDirName(self, albumName, albumID, db):
        if self.abrv.get(db) is None:
            raise ValueError("Could not find DB {0} in MyMusicName".format(db))
        dbAbrv = self.abrv[db]
        
        albumConvName  = self.discConv(albumName)
        matchedDirName = " :: ".join([albumConvName, "[{0}-{1}]".format(dbAbrv, albumID)])
        return matchedDirName

    

    def getUnMatchedDirName(self, matchedDirName, mediaDirType):
        vals = matchedDirName.split(" :: ")
        if len(vals) == 2:
            albumName  = vals[0]
            albumIDval = vals[1]
            try:
                albumID = int(albumIDval[(albumIDval.find("[")+3):albumIDval.rfind("]")])
            except:
                raise ValueError("Could not extract album ID from {0}".format(albumIDval))

            if sum([x in mediaDirType for x in ["Single", "EP"]]) > 0:
                albumName = "{0} (Single)".format(albumName)

            if sum([x in mediaDirType for x in ["Mix", "MixTape"]]) > 0:
                albumName = "{0} (MixTape)".format(albumName)

            return albumName
        else:
            raise ValueError("Could not extract album name from {0}".format(matchedDirName))
            
    
        
    def moveMyMatchedMusicAlbums(self, show=False):
        rename = True
        albumsToMove = getFile(ifile=self.moveFilename)
        print("Found {0} music <-> discogs albums maps".format(len(albumsToMove)))
        
        for db, dbValues in albumsToMove.items():
            if dbValues is None:
                continue
            for artistName, artistAlbums in dbValues.items():
                print("==>",artistName)
                for myAlbumName,albumVals in artistAlbums.items():
                    dirval   = albumVals["Dir"]
                    albumVal = albumVals["Album"]
                    ratio    = albumVals["Ratio"]
                    
                    dbAlbumName = albumVal["Name"]
                    dbAlbumCode = albumVal["Code"]
                    mediaType   = albumVal["MediaType"]


                    matchedDir = setDir(dirval, "Match")
                    mkDir(matchedDir)
                    
                    srcName = myAlbumName
                    srcDir  = setDir(dirval, srcName)
                    if not isDir(srcDir):
                        print("{0} does not exist".format(srcDir))
                        continue

                    mediaDir = setDir(matchedDir, self.discConv(mediaType))
                    mkDir(mediaDir)

                    if rename is True:
                        dstName = self.getMatchedDirName(self.discConv(dbAlbumName), dbAlbumCode, db)
                    else:
                        dstName = self.getMatchedDirName(myAlbumName, dbAlbumCode, db)

                    if show is True:
                        print('\t{0}'.format(mediaDir))
                        print("\t\t[{0}]".format(srcName))
                        print("\t\t[{0}]".format(dstName))
                        continue


                    dstDir  = setDir(mediaDir, dstName)
                    if isDir(dstDir):
                        print("{0} already exists".format(dstDir))
                        continue

                    print("\tMoving {0}  --->  {1}".format(srcDir, dstDir))
                    moveDir(srcDir, dstDir, debug=True)