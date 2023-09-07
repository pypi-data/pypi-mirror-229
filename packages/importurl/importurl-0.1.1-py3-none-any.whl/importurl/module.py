import os
import requests
import string
import sys

class Module :
    def __init__ (self, url: str, cache_path: str="module.pymodule") :
        self.url = url
        if os.path.exists (cache_path) and os.path.isfile (cache_path) :
            self.isCached = True
        else :
            self.isCached = False
        self.cachePath = cache_path
        self.isLoaded = False
    
    def download (self) -> int :
        def content2cache (text: str) :
            result : list = []
            c = 0
            for i in text :
                for j in string.printable :
                    if i == j :
                        result.append (c)
                        c = 0
                        break
                    c += 1
            return bytes (result)
        response = requests.get (self.url)
        open (self.cachePath, "wb").write (content2cache (str (response.content)[2:-1]))
        self.isCached = True
    
    def deleteCachedFile (self) :
        os.remove (self.cachePath)
        self.isCached = False
    
    def deleteAllData (self) :
        os.remove (self.cachePath)
        self.isCached = False
        os.remove (f"c:\\pylib\\{os.path.splitext(os.path.basename(os.path.realpath (self.cachePath)))[0]}.py")
        del self
    
    def loadCachedFile (self) :
        def cache2content (fp: str) :
            data = open (fp, "rb").read()
            result = ""
            for i in data :
                result += string.printable[i]
            return result
        try :
            os.mkdir ("c:\\pylib")
        except :
            pass
        open (f"c:\\pylib\\{os.path.splitext(os.path.basename(os.path.realpath (self.cachePath)))[0]}.py", "w").write (cache2content (self.cachePath))
        if not "c:\\pylib" in sys.path :
            result = ["c:\\pylib"]
            for i in sys.path :
                result.append (i)
            sys.path = result
        self.isLoaded = True

    def downloadThenLoad (self) :
        self.download ()
        self.loadCachedFile ()