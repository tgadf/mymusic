from fileUtils import getBaseFilename, getDirname, getExt, getBasename
from fsUtils import setDir, isFile
from musicBase import musicBase

class pbClass:
    def __init__(self, pbClass, pbArtist, pbAlbum, pbDisc, pbFile, pbExt):
        self.pbClass  = pbClass
        self.pbArtist = pbArtist
        self.pbAlbum  = pbAlbum
        self.pbDisc   = pbDisc
        self.pbFile   = pbFile
        self.pbExt    = pbExt
        
    def getDict(self):
        return self.__dict__



class pathBasics(musicBase):
    def __init__(self, debug=False):
        self.debug = debug
        musicBase.__init__(self, debug=False)
        
        self.mClass  = None
        self.mArtist = None
        self.mAlbum  = None
        self.mDisc   = None
        self.mFile   = None
        
    def stripBase(self, ifile, errors='ignore'):
        mdir = self.getMusicDir()
        if ifile.startswith(mdir) is True:
            ifile = ifile.replace(mdir, "")
            
            if ifile.startswith("/"):
                ifile = ifile[1:]
            else:
                if self.debug:
                    print("Not sure how to parse: {0}".format(ifile))
                self.mFile = ifile
                return
                            
            split   = "/iTunes Media/Music/"
            results = ifile.split(split)
            if len(results) == 2:
                musicClass = results[0]
                ifile      = results[1]
            else:
                if self.debug:
                    print("Not sure how to split: {0}".format(ifile))
                    print("Results --> {0}".format(results))
                self.mFile = ifile
                return

            self.mClass = musicClass
            self.mFile  = ifile
        else:
            if self.debug:
                print("File does not start with: {0}".format(mdir))
                
        self.mFile = ifile
        return
    
        
    def getPaths(self, ifile, errors='ignore'):
        if self.debug:
            print("Start: {0}".format(ifile))
            print("isFile: {0}".format(isFile(ifile)))
        mfile = ifile
        self.stripBase(ifile)

        if self.debug:
            print("Class: {0}".format(self.mClass))
            print("File:  {0}".format(self.mFile))
            
        filename = None
        ext      = None

        ## Try Artist/Album/File.mp3
        dirval,fval = getDirname(self.mFile),getBasename(self.mFile)
        if getExt(fval) in self.musicext:
            filename = fval
            ext      = getExt(fval)
            if self.debug:
                print("Found File: {0}".format(fval))
                print("Upstream:   {0}".format(dirval))
            
            ## Try Artist/Album
            if dirval is not None:
                artval,albval = getDirname(dirval),getBasename(dirval)
                if self.debug:
                    print("Artval/Albval:   {0}\t{1}".format(artval,albval))
                    print("Artval/Albval:   {0}\t{1}".format(getBasename(artval),getBasename(albval)))
                    print("Artval/Albval:   {0}\t{1}".format(getDirname(artval),getDirname(albval)))
                
                if not all([artval,albval]):
                    ## Assume single path is artist
                    artval = albval
                    self.mArtist = artval
                elif not any([getDirname(artval),getDirname(albval)]):
                    ## Assume artist, album path
                    if self.debug:
                        print("Artist: {0}".format(artval))
                        print("Album:  {0}".format(albval))
                    self.mArtist = artval
                    self.mAlbum  = albval
                    pass
                else:
                    ## Assume last path is the disc
                    self.mDisc = albval
                    artval,albval = getDirname(artval),getBasename(artval)
                    if self.debug:
                        print("Artval/Albval:   {0}\t{1}".format(artval,albval))
                        print("Artval/Albval:   {0}\t{1}".format(getBasename(artval),getBasename(albval)))
                        print("Artval/Albval:   {0}\t{1}".format(getDirname(artval),getDirname(albval)))

                    if not all([artval,albval]):
                        ## Assume single path is artist
                        artval = albval
                        self.mArtist = artval
                    elif not any([getDirname(artval),getDirname(albval)]):
                        ## Assume artist, album path
                        if self.debug:
                            print("Artist: {0}".format(artval))
                            print("Album:  {0}".format(albval))
                        self.mArtist = artval
                        self.mAlbum  = albval
                        pass
                    else:
                        artval1,artval2 = getDirname(artval),getBasename(artval)                        
                        if not all([artval1,artval2]):
                            raise ValueError("This shouldn't happen: {0}".format(artval))
                        else:
                            self.mArtist = artval2
                            self.mAlbum  = self.mDisc
                            if errors != 'ignore':
                                raise ValueError("Not sure what to do with {0}, {1}".format(artval1,artval2))
        else:
            print("Ext: {0}".format(getExt(fval)))
            raise ValueError("Not sure how to parse file: {0}".format(ifile))
            
        if self.debug:
            print("Dirname:  {0}".format(dirval))
            print("Filename: {0}".format(filename))
        
        return pbClass(self.mClass, self.mArtist, self.mAlbum, self.mDisc, filename, ext)