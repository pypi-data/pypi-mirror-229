import os
import requests
import string

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
    
    def loadCachedFile (self) :
        def cache2content (bytes_: bytes) -> str :
            result = ""
            for i in bytes_ :
                result += string.printable[i]
            return result
        
        result = [f"class {os.path.splitext(os.path.basename(os.path.realpath (self.cachePath)))[0]} :"]
        
        for i in cache2content (
            open (self.cachePath, "rb").read ()
            ).splitlines () :
            result.append ("    " + i)
        
        r_string = ""
        
        for i in result :
            r_string += i + "\n"
        
        exec (r_string[:-1])
        self.isLoaded = True

    def downloadThenLoad (self) :
        self.download ()
        self.loadCachedFile ()