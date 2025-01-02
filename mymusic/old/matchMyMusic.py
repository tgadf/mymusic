from timeUtils import clock, elapsed
from listUtils import getFlatList
from musicBase import myMusicBase
from matchAlbums import matchAlbums
from ioUtils import getFile, saveFile
from fsUtils import isDir, setDir, mkDir, moveDir
from matchMusicName import myMusicName


class matchMyMusic:
    def __init__(self, mdb, debug=False):
        self.debug = debug
        self.mdb   = mdb
        self.mmb   = myMusicBase()
        self.mmn   = myMusicName()
        
        self.unknownArtists = {}
        self.artistAlbums   = {}
        
        self.matchedAlbums  = {}
        
        
    def setMusicBase(self, mmb):
        self.mmb = mmb
        
        
    def getAlbumStatus(self, force=False):
        self.artistAlbums = self.mmb.getArtistAlbums(force=force)
        

    def getArtistStatus(self):
        start, cmt = clock("Matching All Music Artists")

        ######################################################################
        #### Loop Over My Artists and Paths
        ######################################################################
        for primeDir in self.mmb.getPrimeDirectories():
            for artistName, artistPrimeDirs in self.mmb.getArtistPrimeDirMap(primeDir).items():
                if self.debug:
                    print("{0: <50}{1}".format(artistName,artistPrimeDirs))


                ######################################################################
                #### Get Database IDs
                ######################################################################
                isKnown = self.mdb.isKnownByName(artistName)
                if isKnown is False:
                    self.unknownArtists[artistName] = artistPrimeDirs
                    if self.debug:
                        print("\tUnknown (All)     --> {0}".format(artistName))
                        

        elapsed(start, cmt)
        print("Found {0} unknown artists".format(len(self.unknownArtists)))
        print("Found {0} total artists".format(len(self.artistAlbums)))

        
        
    def getUnknownArtists(self):
        return self.unknownArtists
    
    
    
    def getArtistNameMatchedDirs(self):
        self.artistMatchedDirs = {}
        for primeDir in self.mmb.getPrimeDirectories():
            self.artistMatchedDirs.update(self.mmb.getArtistPrimeDirMap(primeDir))
            

    
    def matchMyMusicAlbumsByArtist(self, db, artistName, albumType=None, ratioCut=0.95, maxCut=0.1):

        matchedAlbums = {}
        

        ######################################################################
        #### Get Artist Album Data
        ######################################################################
        artistAlbumsData = self.mmb.getArtistAlbumsByArtist(artistName)
    
    
        ######################################################################
        #### Get Unmatched Albums
        ######################################################################
        unMatchedAlbums = self.mmb.getUnMatchedAlbumsByArtist(artistName)
        dirval = self.mmb.getArtistMusicDir(artistName)
        if len(unMatchedAlbums) == 0:
            return matchedAlbums
            
            
        ######################################################################
        #### Loop Over Artist Name <-> Prime Map Items
        ######################################################################
        if self.mdb.isKnown(artistName) is True:
            myMusicData = self.mdb.getArtistData(artistName)
            try:
                artistID = myMusicData.getDBID(db)
            except:
                return matchedAlbums
        else:
            return matchedAlbums
            


        ######################################################################
        #### Get Database Albums
        ######################################################################
        artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistID)

        
        ######################################################################
        #### Loop over my albums
        ######################################################################
        for myAlbumName in unMatchedAlbums:

            bestMatchVal = {"Ratio": ratioCut, "Dir": None, "Album": None}

            for mediaType, mediaTypeAlbums in artistDBAlbumsFromID.items():
                if albumType is not None:
                    if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                        continue

                if self.debug:
                    print("\tMy album: {0}".format(myAlbumName))
                myFormattedAlbum = self.mmn.formatAlbum(myAlbumName, mediaType)

                ma = matchAlbums(cutoff=ratioCut)
                ma.match([myFormattedAlbum], mediaTypeAlbums)

                if ma.maxval < ratioCut or ma.maxval > ratioCut+maxCut:
                    continue
                if ma.maxval < bestMatchVal["Ratio"]:
                    continue

                bestMatch = ma.getBestMatch(myFormattedAlbum)

                bestMatchVal = {"Ratio": ma.maxval, "Dir": dirval, 
                                "Album": {"Name": bestMatch["Name"],
                                          "Code": bestMatch["Code"],
                                          "MediaType": mediaType}}
                matchedAlbums[myAlbumName] = bestMatchVal
                #print("{0: <30}{1: <15}{2: <30} --> {3}".format(artistName, db, myAlbumName, bestMatchVal["Album"]))
                #bestMatchVal["Match"].show(debug=True)
                    
        return matchedAlbums

                
    
    def matchMyMusicAlbums(self, db, albumType=1, ratioCut=0.95, maxCut=0.1):
        self.matchedAlbums = {}

        start, cmt = clock("Checking for Albums Matches Against {0} DB".format(db))
        
        
        print("{0: <40}{1: <15}{2: <45} --> {3}".format("Artist", "Database", "Album Name", "Matched Album"))

        ######################################################################
        #### Get Map of Artists and Unmatched Albums
        ######################################################################
        artistNames = self.mmb.getArtists()
        #artistAlbums = self.mmb.getArtistAlbums()


        ######################################################################
        #### Loop Over Artist Name <-> Prime Map Items
        ######################################################################
        for artistName in artistNames:
            matchedAlbums = self.matchMyMusicAlbumsByArtist(db, artistName, albumType, ratioCut, maxCut)
            if len(matchedAlbums) > 0:
                if self.matchedAlbums.get(db) is None:
                    self.matchedAlbums[db] = {}
                self.matchedAlbums[db][artistName] = matchedAlbums
                for myAlbumName,bestMatchVal in matchedAlbums.items():
                    print("{0: <40}{1: <15}{2: <45} --> {3}".format(artistName, db, myAlbumName, bestMatchVal["Album"]))

            
        elapsed(start, cmt)

        saveFile(ifile=self.mmn.moveFilename, idata=self.matchedAlbums, debug=True)
        print("Found {0} music <-> discogs albums maps".format(len(self.matchedAlbums)))
        

    def matchUnknownArtists(self, albumType=1, ratioCut=0.95):
        unknownArtists = self.getUnknownArtists()
        for unknownArtist in unknownArtists.keys():
            print("# ===>",unknownArtist)
            retval = self.matchUnknownArtist(unknownArtist, albumType, ratioCut)

            for db,dbdata in retval.items():
                bestMatch = {"ID": None, "Matches": 0, "Score": 0.0}
                for artistDBID,artistDBData in dbdata.items():
                    for mediaType,ma in artistDBData.items():
                        if ma.near == 0:
                            continue
                        if ma.near > bestMatch["Matches"]:
                            bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}
                        elif ma.near == bestMatch["Matches"]:
                            if ma.score > bestMatch["Score"]:
                                bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}

                if bestMatch["ID"] is not None:
                    print("mdb.add(\"{0}\", \"{1}\", \"{2}\")".format(unknownArtist, db, bestMatch["ID"]))
            
            
    def matchUnknownArtist(self, unknownArtist, albumType=None, ratioCut=0.95):
        ######################################################################
        #### Get Unknown Artist Albums and Potential DB Artists
        ######################################################################
        unMatchedAlbums = self.mmb.getUnMatchedAlbumsByArtist(unknownArtist)
        artistNameDBIDs = self.mdb.getArtistIDs(unknownArtist)
        
        #print(unknownArtist)
        #print(unMatchedAlbums)
        #print(artistNameDBIDs)
        #return

        
        ######################################################################
        #### Get Database Albums
        ######################################################################
        matches = {}
        for db,artistDBartists in artistNameDBIDs.items():
            
            dbMatches = {}
            for artistDBartist,artistDBIDs in artistDBartists.items():
                for artistDBID in artistDBIDs:
                    dbMatches[artistDBID] = {}
                    artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistDBID)

                    for mediaType, mediaTypeAlbums in artistDBAlbumsFromID.items():
                        if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                            continue

                        ma = matchAlbums(cutoff=ratioCut)
                        ma.match(unMatchedAlbums, mediaTypeAlbums)
                        #ma.show(debug=True)
                        
                        dbMatches[artistDBID][mediaType] = ma
                        
            matches[db] = dbMatches
            
        return matches
    
    def manuallyMatchUnknownArtist(self, unknownArtist, cutoff=0.8):
        ######################################################################
        #### Get Unknown Artist Albums and Potential DB Artists
        ######################################################################
        unMatchedAlbums = self.mmb.getUnMatchedAlbumsByArtist(unknownArtist)
        artistNameDBIDs = self.mdb.getArtistIDs(unknownArtist, cutoff=cutoff)
        
        print("Unknown Artist:   {0}".format(unknownArtist))
        try:
            print("UnMatched Albums: {0}".format(", ".join(unMatchedAlbums)))
        except:
            print("Could not show the unMatched Albums below:")
            print("-> ",unMatchedAlbums," <-")
        print("="*50)
        print(artistNameDBIDs)
        for db,artistDBartists in artistNameDBIDs.items():
            print("="*50)
            print("   {0}".format(db))
            for artistDBartist,artistDBIDs in artistDBartists.items():
                print("      {0}".format(artistDBartist))
                for artistDBID in artistDBIDs:
                    artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistDBID)
                    albums = [list(mediaTypeAlbums.values()) for mediaTypeAlbums in artistDBAlbumsFromID.values()]
                    print("mdb.add(\"{0}\", \"{1}\", \"{2}\")".format(unknownArtist, db, artistDBID))
                    print("         {0: <45}\t{1}".format(artistDBID, getFlatList(albums)))
                    

                    
    def getArtistDBMatchLists(self, dbartist):
        dbArtistData   = self.mdb.getArtistData(dbartist)
        retval = {"Matched": [], "Unmatched": []}
        albumTypesData = {k: [] for k in [1,2,3,4]}
        for db,dbIDdata in dbArtistData.items():
            try:
                dbID = dbIDdata["ID"]
                retval["Matched"].append(db)
            except:
                retval["Unmatched"].append(db)
        return retval
    
                    
    def getMatchedArtistAlbumsFromDB(self, dbartist, merge=True):
        dbArtistData   = self.mdb.getArtistData(dbartist)
        dbsToSearch    = self.getArtistDBMatchLists(dbartist)
        albumTypesData = {k: [] for k in [1,2,3,4]}
        for db in dbsToSearch["Matched"]:
            dbIDdata = dbArtistData[db]
            try:
                dbID = dbIDdata["ID"]
            except:
                raise ValueError("This db {0} should already be known for {1}".format(db, dbartist))

            dbAlbumsData = self.mdb.getArtistAlbumsFromID(db, dbID)

            for albumType in albumTypesData.keys():
                for mediaType, mediaTypeAlbums in dbAlbumsData.items():
                    if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                        continue                
                    #print(db,albumType,mediaType,mediaTypeAlbums)
                    albumTypesData[albumType] += list(mediaTypeAlbums.values())

        albumTypesData = {k: list(set(v)) for k,v in albumTypesData.items()}

        ############################
        ## Merge Albums
        ############################
        if merge is True:
            artistAlbums = getFlatList(albumTypesData.values())
        else:
            artistAlbums = albumTypesData

        return artistAlbums
    
    
    
    def searchForMutualDBEntriesByDB(self, db, cutoff=0.875, maxAdds=50, start=None, modVal=100, maxAlbumsForSearch=500):
        ######################################################################
        #### Get Map of Artists and Unmatched Albums
        ######################################################################
        dbartists = self.mdb.getArtists()
        cnts      = 0
        print("Searching for mutual DB matches for {0} artists".format(len(dbartists)))
        for ia,dbartist in enumerate(dbartists):
            if start is not None:
                if ia < start:
                    continue
            if ia % modVal == 0:
                print("## {0: <20} -- {1}".format("{0}/{1}".format(ia,len(dbartists)),dbartist))
            if cnts >= maxAdds:
                break
            
            status = self.mdb.getArtistDBData(dbartist, db)
            if status["ID"] is not None:
                continue
            artistAlbums = self.getMatchedArtistAlbumsFromDB(dbartist, merge=True)


            ########################################################
            ## Loop Over Unmatched DBs
            ########################################################
            dbMatches = {}
            artistDBartists = self.mdb.getArtistDBIDs(dbartist, db, num=10, cutoff=cutoff, debug=False)
            matchStatus = True
            for artistDBartist,artistDBIDs in artistDBartists.items():
                if matchStatus is False:
                    continue
                #print('  ',db,'\t',artistDBartist)
                for artistDBID in artistDBIDs:
                    #print('    ',artistDBID)
                    dbMatches[artistDBID] = {}
                    artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistDBID)

                    albumTypesData = {k: [] for k in [1,2,3,4]}
                    for albumType in albumTypesData.keys():
                        for mediaType, mediaTypeAlbums in artistDBAlbumsFromID.items():
                            if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                                continue
                            albumTypesData[albumType] += list(mediaTypeAlbums.values())

                    albumTypesData = {k: list(set(v)) for k,v in albumTypesData.items()}
                    dbArtistAlbums = getFlatList(albumTypesData.values())
                    if len(dbArtistAlbums) > maxAlbumsForSearch:
                        matchStatus = False
                        print("#\tNot checking {0} because there are {1} > {2} albums".format(dbartist, len(dbArtistAlbums), maxAlbumsForSearch))
                        continue


                    ma = matchAlbums(cutoff=cutoff)
                    ma.match(artistAlbums, dbArtistAlbums)
                    #ma.show(debug=True)

                    dbMatches[artistDBID] = ma

            if matchStatus is False:
                continue
                
                
            if len(dbMatches) > 0:
                bestMatch = {"ID": None, "Matches": 0, "Score": 0.0}
                for artistDBID,ma in dbMatches.items():
                    if ma.near == 0:
                        continue
                    if ma.near > bestMatch["Matches"]:
                        bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}
                    elif ma.near == bestMatch["Matches"]:
                        if ma.score > bestMatch["Score"]:
                            bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}

                if bestMatch["ID"] is not None:
                    cnts += 1                 
                    print("mdb.add(\"{0}\", \"{1}\", \"{2}\")".format(dbartist, db, bestMatch["ID"]))



            
    def searchForMutualDBEntries(self, cutoff=0.875, maxAdds=50, start=None, modVal=100, dbs=None):
        ######################################################################
        #### Get Map of Artists and Unmatched Albums
        ######################################################################
        dbartists = self.mdb.getArtists()
        cnts      = 0
        print("Searching for mutual DB matches for {0} artists".format(len(dbartists)))
        for ia,dbartist in enumerate(dbartists):
            if start is not None:
                if ia < start:
                    continue
            if ia % modVal == 0:
                print("## {0: <20} -- {1}".format("{0}/{1}".format(ia,len(dbartists)),dbartist))
            if cnts >= maxAdds:
                break
            artistAlbums = self.getMatchedArtistAlbumsFromDB(dbartist, merge=True)
            dbsToSearch  = self.getArtistDBMatchLists(dbartist)

            if dbs is not None:
                usefulDBs          = ['Discogs', 'MusicBrainz', 'AllMusic', 'LastFM']
            else:
                usefulDBs          = dbs
            usefulDBsToSearch  = list(set(dbsToSearch["Unmatched"]).intersection(set(usefulDBs)))


            ########################################################
            ## Loop Over Unmatched DBs
            ########################################################
            for db in usefulDBsToSearch:
                dbMatches = {}
                artistDBartists = self.mdb.getArtistDBIDs(dbartist, db, num=10, cutoff=cutoff, debug=False)
                
                for artistDBartist,artistDBIDs in artistDBartists.items():
                    #print('  ',db,'\t',artistDBartist)
                    for artistDBID in artistDBIDs:
                        #print('    ',artistDBID)
                        dbMatches[artistDBID] = {}
                        artistDBAlbumsFromID = self.mdb.getArtistAlbumsFromID(db, artistDBID)

                        albumTypesData = {k: [] for k in [1,2,3,4]}
                        for albumType in albumTypesData.keys():
                            for mediaType, mediaTypeAlbums in artistDBAlbumsFromID.items():
                                if mediaType not in self.mdb.getDBAlbumTypeNames(db, albumType):
                                    continue
                                albumTypesData[albumType] += list(mediaTypeAlbums.values())

                        albumTypesData = {k: list(set(v)) for k,v in albumTypesData.items()}
                        dbArtistAlbums = getFlatList(albumTypesData.values())
            

                        ma = matchAlbums(cutoff=cutoff)
                        ma.match(artistAlbums, dbArtistAlbums)
                        #ma.show(debug=True)
                        
                        dbMatches[artistDBID] = ma
                
                if len(dbMatches) > 0:
                    bestMatch = {"ID": None, "Matches": 0, "Score": 0.0}
                    for artistDBID,ma in dbMatches.items():
                        if ma.near == 0:
                            continue
                        if ma.near > bestMatch["Matches"]:
                            bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}
                        elif ma.near == bestMatch["Matches"]:
                            if ma.score > bestMatch["Score"]:
                                bestMatch = {"ID": artistDBID, "Matches": ma.near, "Score": ma.score}

                    if bestMatch["ID"] is not None:
                        cnts += 1                 
                        print("mdb.add(\"{0}\", \"{1}\", \"{2}\")".format(dbartist, db, bestMatch["ID"]))
                        

