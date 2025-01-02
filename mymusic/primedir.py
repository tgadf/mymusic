""" Prime Directory Class """

__all__ = ["PrimeDir", "getPrimeDir"]

from string import ascii_uppercase, ascii_lowercase, digits


class PrimeDir:
    def __init__(self, debug=False):
        retvals = [x for x in ascii_uppercase]
        retvals += ["Num", "Xtra", "The"]
        retvals = sorted(retvals)
        self.primeDirectories = retvals

    def getPrimeDirs(self):
        return self.primeDirectories

    def getPrimeDir(self, artistName):
        try:
            start = artistName[0]
        except Exception as error:
            raise ValueError(f"Prime Directory cannot be found for {artistName}: {error}")

        if start in ascii_uppercase:
            if artistName.startswith("The "):
                return "The"
            return start
        elif start in ascii_lowercase:
            return "Xtra"
        elif start in digits:
            return "Num"
        else:
            return "Xtra"
            raise ValueError(f"Could not determine Prime Directory for Artist {artistName}")
            
            
def getPrimeDir(artistName):
    pd = PrimeDir()
    return pd.getPrimeDir(artistName)