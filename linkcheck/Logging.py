""" Logger classes.
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

Every Logger has to implement the following functions:
init(self)
  Called once to initialize the Logger. Why do we not use __init__(self)?
  Because we initialize the start time in init and __init__ gets not
  called at the time the checking starts but when the logger object is
  created.

newUrl(self,urlData)
  Called every time an url finished checking. All data we checked is in
  the UrlData object urlData.

endOfOutput(self)
  Called at the end of checking to close filehandles and such.
"""
import sys,time
import Config,StringUtil,linkcheck
_ = linkcheck.gettext

# ANSI color codes
ESC="\x1b"
COL_PARENT  =ESC+"[37m"   # white
COL_URL     =ESC+"[0m"    # standard
COL_REAL    =ESC+"[36m"   # cyan
COL_BASE    =ESC+"[35m"   # magenty
COL_VALID   =ESC+"[1;32m" # green
COL_INVALID =ESC+"[1;31m" # red
COL_INFO    =ESC+"[0m"    # standard
COL_WARNING =ESC+"[1;33m" # yellow
COL_DLTIME  =ESC+"[0m"    # standard
COL_RESET   =ESC+"[0m"    # reset to standard

# HTML colors
ColorBackground="\"#fff7e5\""
ColorUrl="\"#dcd5cf\""
ColorBorder="\"#000000\""
ColorLink="\"#191c83\""
TableWarning="<td bgcolor=\"#e0954e\">"
TableError="<td bgcolor=\"db4930\">"
TableOK="<td bgcolor=\"3ba557\">"
RowEnd="</td></tr>\n"
MyFont="<font face=\"Lucida,Verdana,Arial,sans-serif,Helvetica\">"

# keywords
KeyWords = ["Real URL",
    "Result",
    "Base",
    "Parent URL",
    "Info",
    "Warning",
    "D/L Time",
    "Check Time",
    "URL",
]
MaxIndent = max(map(lambda x: len(_(x)), KeyWords))+1
Spaces = {}
for key in KeyWords:
    Spaces[key] = " "*(MaxIndent - len(_(key)))

# return formatted time
def _strtime(t):
    return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(t))

class StandardLogger:
    """Standard text logger.
    Informal text output format spec:
    Output consists of a set of URL logs separated by one or more
    blank lines.
    A URL log consists of two or more lines. Each line consists of
    keyword and data, separated by whitespace.
    Unknown keywords will be ignored.
    """

    def __init__(self, fd=sys.stdout):
        self.errors=0
        self.warnings=0
        self.fd = fd


    def init(self):
        self.starttime = time.time()
        self.fd.write(Config.AppInfo+"\n"+
                      Config.Freeware+"\n"+
                      _("Get the newest version at ")+Config.Url+"\n"+
                      _("Write comments and bugs to ")+Config.Email+"\n\n"+
                      _("Start checking at ")+_strtime(self.starttime)+"\n")
        self.fd.flush()


    def newUrl(self, urldata):
        self.fd.write("\n"+_("URL")+Spaces["URL"]+urldata.urlName)
        if urldata.cached:
            self.fd.write(" (cached)\n")
        else:
            self.fd.write("\n")
        if urldata.parentName:
            self.fd.write(_("Parent URL")+Spaces["Parent URL"]+
	                  urldata.parentName+_(", line ")+
	                  str(urldata.line)+"\n")
        if urldata.baseRef:
            self.fd.write(_("Base")+Spaces["Base"]+urldata.baseRef+"\n")
        if urldata.url:
            self.fd.write(_("Real URL")+Spaces["Real URL"]+urldata.url+"\n")
        if urldata.downloadtime:
            self.fd.write(_("D/L Time")+Spaces["D/L Time"]+
	                  _("%.3f seconds\n") % urldata.downloadtime)
        if urldata.checktime:
            self.fd.write(_("Check Time")+Spaces["Check Time"]+
	                  _("%.3f seconds\n") % urldata.checktime)
        if urldata.infoString:
            self.fd.write(_("Info")+Spaces["Info"]+
	                  StringUtil.indent(
                          StringUtil.blocktext(urldata.infoString, 65),
			  MaxIndent)+"\n")
        if urldata.warningString:
            self.warnings = self.warnings+1
            self.fd.write(_("Warning")+Spaces["Warning"]+
	                  StringUtil.indent(
                          StringUtil.blocktext(urldata.warningString, 65),
			  MaxIndent)+"\n")
        
        self.fd.write(_("Result")+Spaces["Result"])
        if urldata.valid:
            self.fd.write(urldata.validString+"\n")
        else:
            self.errors = self.errors+1
            self.fd.write(urldata.errorString+"\n")
        self.fd.flush()


    def endOfOutput(self):
        self.fd.write(_("\nThats it. "))

        if self.warnings==1:
            self.fd.write(_("1 warning, "))
        else:
            self.fd.write(str(self.warnings)+_(" warnings, "))
        if self.errors==1:
            self.fd.write(_("1 error"))
        else:
            self.fd.write(str(self.errors)+_(" errors"))
        self.fd.write(_(" found.\n"))
        self.stoptime = time.time()
        self.fd.write(_("Stopped checking at ")+_strtime(self.stoptime)+
	              (_(" (%.3f seconds)") %
		      (self.stoptime - self.starttime))+"\n")
        self.fd.flush()
        self.fd = None



class HtmlLogger(StandardLogger):
    """Logger with HTML output"""

    def init(self):
        self.starttime = time.time()
        self.fd.write("<html><head><title>"+Config.AppName+"</title></head>"+
              "<body bgcolor="+ColorBackground+" link="+ColorLink+
              " vlink="+ColorLink+" alink="+ColorLink+">"+
              "<center><h2>"+MyFont+Config.AppName+"</font>"+
              "</center></h2>"+
              "<br><blockquote>"+Config.Freeware+"<br><br>"+
              _("Start checking at ")+_strtime(self.starttime)+"<br><br>")
        self.fd.flush()


    def newUrl(self, urlData):
        self.fd.write("<table align=left border=\"0\" cellspacing=\"0\""
              " cellpadding=\"1\" bgcolor="+ColorBorder+
              "><tr><td><table align=left border=\"0\" cellspacing=\"0\""
              " cellpadding=\"3\" bgcolor="+ColorBackground+
              "><tr><td bgcolor="+ColorUrl+">"+
              MyFont+"URL</font></td><td bgcolor="+ColorUrl+">"+MyFont+
              StringUtil.htmlify(urlData.urlName))
        if urlData.cached:
            self.fd.write("(cached)")
        self.fd.write("</font>"+RowEnd)
        
        if urlData.parentName:
            self.fd.write("<tr><td>"+MyFont+_("Parent URL")+
	                  "</font></td><td>"+
			  MyFont+"<a href=\""+urlData.parentName+"\">"+
                          urlData.parentName+"</a> line "+str(urlData.line)+
                          "</font>"+RowEnd)
        if urlData.baseRef:
            self.fd.write("<tr><td>"+MyFont+_("Base")+"</font></td><td>"+
	                  MyFont+urlData.baseRef+"</font>"+RowEnd)
        if urlData.url:
            self.fd.write("<tr><td>"+MyFont+_("Real URL")+"</font></td><td>"+
	                  MyFont+"<a href=\""+StringUtil.htmlify(urlData.url)+
			  "\">"+urlData.url+"</a></font>"+RowEnd)
        if urlData.downloadtime:
            self.fd.write("<tr><td>"+MyFont+_("D/L Time")+"</font></td><td>"+
	                  MyFont+("%.3f" % urlData.downloadtime)+
			  " seconds</font>"+RowEnd)
        if urlData.checktime:
            self.fd.write("<tr><td>"+MyFont+_("Check Time")+
	                  "</font></td><td>"+MyFont+
			  ("%.3f" % urlData.checktime)+" seconds</font>"+
                          RowEnd)
        if urlData.infoString:
            self.fd.write("<tr><td>"+MyFont+_("Info")+"</font></td><td>"+
	                  MyFont+StringUtil.htmlify(urlData.infoString)+
			  "</font>"+RowEnd)
        if urlData.warningString:
            self.warnings = self.warnings+1
            self.fd.write("<tr>"+TableWarning+MyFont+_("Warning")+
	                  "</font></td>"+TableWarning+MyFont+
			  urlData.warningString+"</font>"+RowEnd)
        if urlData.valid:
            self.fd.write("<tr>"+TableOK+MyFont+_("Result")+"</font></td>"+
                  TableOK+MyFont+urlData.validString+"</font>"+RowEnd)
        else:
            self.errors = self.errors+1
            self.fd.write("<tr>"+TableError+MyFont+_("Result")+"</font></td>"+
                  TableError+MyFont+urlData.errorString+"</font>"+RowEnd)
        
        self.fd.write("</table></td></tr></table><br clear=all><br>")
        self.fd.flush()        

        
    def endOfOutput(self):
        self.fd.write(MyFont+_("Thats it. "))
        if self.warnings==1:
            self.fd.write(_("1 warning, "))
        else:
            self.fd.write(str(self.warnings)+_(" warnings, "))
        if self.errors==1:
            self.fd.write(_("1 error"))
        else:
            self.fd.write(str(self.errors)+_(" errors"))
        self.fd.write(_(" found.")+"<br>")
        self.stoptime = time.time()
        self.fd.write(_("Stopped checking at ")+_strtime(self.stoptime)+
             (_(" (%.3f seconds)") % (self.stoptime - self.starttime))+
	     "</font></blockquote><br><hr noshade size=1><small>"+
             MyFont+Config.HtmlAppInfo+"<br>"+_("Get the newest version at ")+
             "<a href=\""+Config.Url+"\">"+Config.Url+
             "</a>.<br>"+_("Write comments and bugs to ")+"<a href=\"mailto:"+
             Config.Email+"\">"+Config.Email+
             "</a>.</font></small></body></html>")
        self.fd.flush()        
        self.fd = None


class ColoredLogger(StandardLogger):
    """ANSI colorized output"""

    def __init__(self, fd=sys.stdout):
        StandardLogger.__init__(self, fd)
        self.currentPage = None
        self.prefix = 0

    def newUrl(self, urlData):
        if urlData.parentName:
            if self.currentPage != urlData.parentName:
                if self.prefix:
                    self.fd.write("o\n")
                self.fd.write("\n"+_("Parent URL")+Spaces["Parent URL"]+
		              COL_PARENT+urlData.parentName+COL_RESET+"\n")
                self.currentPage = urlData.parentName
                self.prefix = 1
        else:
            if self.prefix:
                self.fd.write("o\n")
            self.prefix = 0
            self.currentPage=None
            
        if self.prefix:
            self.fd.write("|\n+- ")
        else:
            self.fd.write("\n")
        self.fd.write(_("URL")+Spaces["URL"]+COL_URL+urlData.urlName+
	              COL_RESET)
        if urlData.line: self.fd.write(_(", line ")+`urlData.line`+"")
        if urlData.cached:
            self.fd.write(" (cached)\n")
        else:
            self.fd.write("\n")
            
        if urlData.baseRef:
            if self.prefix:
                self.fd.write("|  ")
            self.fd.write(_("Base")+Spaces["Base"]+COL_BASE+urlData.baseRef+
	                  COL_RESET+"\n")
            
        if urlData.url:
            if self.prefix:
                self.fd.write("|  ")
            self.fd.write(_("Real URL")+Spaces["Real URL"]+COL_REAL+
	                  urlData.url+COL_RESET+"\n")
        if urlData.downloadtime:
            if self.prefix:
                self.fd.write("|  ")
            self.fd.write(_("D/L Time")+Spaces["D/L Time"]+COL_DLTIME+
	        (_("%.3f seconds") % urlData.downloadtime)+COL_RESET+"\n")
        if urlData.checktime:
            if self.prefix:
                self.fd.write("|  ")
            self.fd.write(_("Check Time")+Spaces["Check Time"]+COL_DLTIME+
	        (_("%.3f seconds") % urlData.checktime)+COL_RESET+"\n")
            
        if urlData.infoString:
            if self.prefix:
                self.fd.write("|  "+_("Info")+Spaces["Info"]+
                      StringUtil.indentWith(StringUtil.blocktext(
                        urlData.infoString, 65), "|      "+Spaces["Info"]))
            else:
                self.fd.write(_("Info")+Spaces["Info"]+
                      StringUtil.indentWith(StringUtil.blocktext(
                        urlData.infoString, 65), "    "+Spaces["Info"]))
            self.fd.write(COL_RESET+"\n")
            
        if urlData.warningString:
            self.warnings = self.warnings+1
            if self.prefix:
                self.fd.write("|  ")
            self.fd.write(_("Warning")+Spaces["Warning"]+COL_WARNING+
	                  urlData.warningString+COL_RESET+"\n")

        if self.prefix:
            self.fd.write("|  ")
        self.fd.write(_("Result")+Spaces["Result"])
        if urlData.valid:
            self.fd.write(COL_VALID+urlData.validString+COL_RESET+"\n")
        else:
            self.errors = self.errors+1
            self.fd.write(COL_INVALID+urlData.errorString+COL_RESET+"\n")
        self.fd.flush()        


    def endOfOutput(self):
        if self.prefix:
            self.fd.write("o\n")
        StandardLogger.endOfOutput(self)


class GMLLogger(StandardLogger):
    """GML means Graph Modeling Language. Use a GML tool to see
    your sitemap graph.
    """
    def __init__(self,fd=sys.stdout):
        StandardLogger.__init__(self,fd)
        self.nodes = []

    def init(self):
        self.fd.write("# created by "+Config.AppName+" at "+
	     _strtime(time.time())+
	    "\n# "+_("Get the newest version at ")+Config.Url+
            "\n# "+_("Write comments and bugs to ")+Config.Email+
	    "\ngraph [\n  directed 1\n")
        self.fd.flush()

    def newUrl(self, urlData):
        self.nodes.append(urlData)

    def endOfOutput(self):
        writtenNodes = {}
        # write nodes
        nodeid = 1
        for node in self.nodes:
            if node.url and not writtenNodes.has_key(node.url):
                self.fd.write("  node [\n")
		self.fd.write("    id     "+`nodeid`+"\n")
                self.fd.write('    label  "'+node.url+'"'+"\n")
                if node.downloadtime:
                    self.fd.write("    dltime "+`node.downloadtime`+"\n")
                if node.checktime:
                    self.fd.write("    checktime "+`node.checktime`+"\n")
                self.fd.write("    extern ")
		if node.extern: self.fd.write("1")
		else: self.fd.write("0")
		self.fd.write("\n  ]\n")
                writtenNodes[node.url] = nodeid
                nodeid = nodeid + 1
        # write edges
        for node in self.nodes:
            if node.url and node.parentName:
                self.fd.write("  edge [\n")
		self.fd.write('    label  "'+node.urlName+'"\n')
	        self.fd.write("    source "+`writtenNodes[node.parentName]`+
		              "\n")
                self.fd.write("    target "+`writtenNodes[node.url]`+"\n")
                self.fd.write("    valid  ")
                if node.valid: self.fd.write("1")
                else: self.fd.write("0")
                self.fd.write("\n  ]\n")
        # end of output
        self.fd.write("]\n")
        self.fd.flush()
        self.fd = None


class SQLLogger(StandardLogger):
    """ SQL output for PostgreSQL, not tested"""
    def init(self):
        self.fd.write("-- created by "+Config.AppName+" at "+
                _strtime(time.time())+
		"\n-- "+_("Get the newest version at ")+Config.Url+
		"\n-- "+_("Write comments and bugs to ")+Config.Email+"\n\n")
        self.fd.flush()

    def newUrl(self, urlData):
        self.fd.write("insert into linksdb(urlname,recursionlevel,parentname,"
	              "baseref,errorstring,validstring,warningstring,"
		      "infoString,valid,url,line,cached) values '"+
                      urlData.urlName+"',"+
		      `urlData.recursionLevel`+","+
		      StringUtil.sqlify(urlData.parentName)+","+
                      StringUtil.sqlify(urlData.baseRef)+","+
                      StringUtil.sqlify(urlData.errorString)+","+
                      StringUtil.sqlify(urlData.validString)+","+
                      StringUtil.sqlify(urlData.warningString)+","+
                      StringUtil.sqlify(urlData.infoString)+","+
                      `urlData.valid`+","+
                      StringUtil.sqlify(urlData.url)+","+
                      `urlData.line`+","+
                      `urlData.cached`+");\n")
        self.fd.flush()

    def endOfOutput(self):
        self.fd = None


class BlacklistLogger:
    """Updates a blacklist of wrong links. If a link on the blacklist
    is working (again), it is removed from the list. So after n days
    we have only links on the list which failed for n days.
    """
    def __init__(self):
        self.blacklist = {}

    def init(self):
        """initialize the blacklist
        We do nothing here because we have read the blacklist in the
        linkchecker script already.
	"""
        pass

    def newUrl(self, urlData):
        if urlData.valid:
            self.blacklist[urlData.getCacheKey()] = None
        elif not urlData.cached:
            self.blacklist[urlData.getCacheKey()] = urlData

    def endOfOutput(self):
        """write the blacklist"""
        fd = open(Config.BlacklistFile, "w")
        for url in self.blacklist.keys():
            if self.blacklist[url] is None:
                fd.write(url+"\n")


class CSVLogger(StandardLogger):
    """ CSV output. CSV consists of one line per entry. Entries are
    separated by a semicolon.
    """
    def init(self):
        self.fd.write("# created by "+Config.AppName+" at "+
                _strtime(time.time())+
		"\n# you get "+Config.AppName+" at "+Config.Url+
		"\n# write comments and bugs to "+Config.Email+"\n\n")
        self.fd.flush()

    def newUrl(self, urlData):
        self.fd.write(`urlData.urlName`+';'+
		      `urlData.recursionLevel`+';'+
		      `urlData.parentName`+';'+
                      `urlData.baseRef`+';'+
                      `urlData.errorString`+';'+
                      `urlData.validString`+';'+
                      `urlData.warningString`+';'+
                      `urlData.infoString`+';'+
                      `urlData.valid`+';'+
                      `urlData.url`+';'+
                      `urlData.line`+';'+
                      `urlData.cached`+'\n')
        self.fd.flush()

    def endOfOutput(self):
        self.fd = None

