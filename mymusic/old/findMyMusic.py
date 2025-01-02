from musicBase import myMusicBase
from matchMyMusic import matchMyMusic
from matchMusicName import myMusicName


def findMusic():
    ## Basic stuff
    mmb = myMusicBase(debug=False)
    mmb.findArtistAlbums()
    return mmb

def getMusicStatus(mdbmap, mmb):    
    mmm = matchMyMusic(mdbmap)
    mmm.getArtistStatus()
    mmm.setMusicBase(mmb)
    unknownArtists = mmm.getUnknownArtists()    
    return mmb,mmm,unknownArtists