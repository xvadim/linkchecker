"""
    Copyright (C) 2000  Bastian Kleineidam

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
import re,string,os,urlparse
from UrlData import UrlData
from os.path import normpath

class FileUrlData(UrlData):
    "Url link with file scheme"

    def __init__(self,
                 urlName, 
                 recursionLevel, 
                 parentName = None,
                 baseRef = None, line=0):
        UrlData.__init__(self,
                 urlName, 
                 recursionLevel,
                 parentName=parentName,
                 baseRef=baseRef, line=line)
        if not parentName and not baseRef and \
           not re.compile("^file:").search(self.urlName):
            winre = re.compile("^[a-zA-Z]:")
            if winre.search(self.urlName):
                self.adjustWinPath()
            else:
                if self.urlName[0:1] != "/":
                    self.urlName = os.getcwd()+"/"+self.urlName
                    if winre.search(self.urlName):
                        self.adjustWinPath()
            self.urlName = "file://"+normpath(self.urlName)


    def buildUrl(self):
        UrlData.buildUrl(self)
        # cut off parameter, query and fragment
        self.url = urlparse.urlunparse(self.urlTuple[:3] + ('','',''))


    def adjustWinPath(self):
        "c:\\windows ==> /c|\\windows"
        self.urlName = "/"+self.urlName[0]+"|"+self.urlName[2:]


    def isHtml(self):
        return self.valid and re.compile("\.s?html?$").search(self.url)


    def __str__(self):
        return "File link\n"+UrlData.__str__(self)

