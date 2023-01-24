"""
 Copyright 2009 Luca Trevisan

 Additional contributors: Radu Grigore

 LaTeX2WP3 version of LaTeX2WP for python3

 This file is part of LaTeX2WP, a program that converts
 a LaTeX document into a format that is ready to be
 copied and pasted into WordPress.

 You are free to redistribute and/or modify LaTeX2WP under the
 terms of the GNU General Public License (GPL), version 3
 or (at your option) any later version.

 I hope you will find LaTeX2WP useful, but be advised that
 it comes WITHOUT ANY WARRANTY; without even the implied warranty
 of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GPL for more details.

 You should have received a copy of the GNU General Public
 License along with LaTeX2WP.  If you can't find it,
 see <http://www.gnu.org/licenses/>.
"""


import re
from sys import argv
from math2html import math2html
from latex2wpstyle import *

# prepare variables computed from the info in latex2wpstyle
count = dict()
for thm in ThmEnvs:
    count[T[thm]] = 0
count["section"] = count["subsection"] = count["equation"] = 0

ref = {}

endlatex = "&fg="+textcolor
if HTML:
    endproof = "<img src=\"http://l.wordpress.com/latex.php?latex=\Box&fg=000000\">"


inthm = ""
itemno = -1
labelused = False

"""
 At the beginning, the commands \$, \% and \& are temporarily
 replaced by placeholders (the second entry in each 4-tuple).
 At the end, The placeholders in text mode are replaced by
 the third entry, and the placeholders in math mode are
 replaced by the fourth entry.
"""

esc = [["\\$", "_dollar_", "&#36;", "\\$"],
       ["\\%", "_percent_", "&#37;", "\\%"],
       ["\\&", "_amp_", "&amp;", "\\&"],
       ["\\>", "_greaterthan_", "&gt;", "&gt;"],
       ["\\<", "_lessthan_", "&lt;", "&lt;"],
       [">", "_greater_", ">", "&gt;"],
       ["<", "_lesser_", "<", "&lt;"],
       ["\_", "_underscore_", "_", "\\_"],
       ["\enspace", "_ensp_", "&ensp;", "&ensp;"]]

M = M + [["\\more", "<!--more-->"],
         ["\\newblock", "\\\\"],
         ["\\sloppy", ""],
         ["\\S", "&sect;"]]

Mnomath = [["\\\\", "<br/>\n"],
           ["\\ ", " "],
           ["\\`a", "&agrave;"],
           ["\\'a", "&aacute;"],
           ["\\\"a", "&auml;"],
           ["\\aa ", "&aring;"],
           ["{\\aa}", "&aring;"],
           ["\\`e", "&egrave;"],
           ["\\'e", "&eacute;"],
           ["\\\"e", "&euml;"],
           ["\\`i", "&igrave;"],
           ["\\'i", "&iacute;"],
           ["\\\"i", "&iuml;"],
           ["\\`o", "&ograve;"],
           ["\\'o", "&oacute;"],
           ["\\\"o", "&ouml;"],
           ["\\`o", "&ograve;"],
           ["\\'o", "&oacute;"],
           ["\\\"o", "&ouml;"],
           ["\\H o", "&ouml;"],
           ["\\`u", "&ugrave;"],
           ["\\'u", "&uacute;"],
           ["\\\"u", "&uuml;"],
           ["\\`u", "&ugrave;"],
           ["\\'u", "&uacute;"],
           ["\\\"u", "&uuml;"],
           ["\\v{C}", "&#268;"],
           ["\\^o", "&ocirc;"],
           ["\\=o", "&#333;"],
           ["\\salg", "&sigma;-algebra"],
           ["\\qed", "&#x2b1c;\n\n"],
           ["\\lbar", "&#x0142;"],
           ["\\amp", "&"]]


cb = re.compile("\\{|}")


def extract_body(m):
    """
      extract_body() takes the text between a \begin{document}
      and \end{document}, if present, (otherwise it keeps the
      whole document), normalizes the spacing, and removes comments
    """
    global labelpre
    
    begin = re.compile("\\\\begin\s*")
    m = begin.sub("\\\\begin",m)
    end = re.compile("\\\\end\s*")
    m = end.sub("\\\\end",m)
    
    beginenddoc = re.compile("\\\\begin\\{document}"
                             "|\\\\end\\{document}")
    parse = beginenddoc.split(m)
    if len(parse) == 1:
        m = parse[0]
    else:
        m = parse[1]

    """
      Looks for \labelpre before begin document, or in body if no begin document, to prepend all labels
    """
    labelpreobj = re.search(r"\\labelpre\s*\{(.*?)}", parse[0])
    labelpre = labelpreobj.group(1) if labelpreobj else ""

    """
      removes comments, replaces double returns with <p> and
      other returns and multiple spaces by a single space.
    """

    for e in esc:
        m = m.replace(e[0],e[1])

    comments = re.compile("%.*?\n")
    m = comments.sub(" ", m)
    m = "<p>" + m.strip() + "</p>" # remove leading and trailing whitespace, and enclose in paragraph

    multiplereturns = re.compile("\n\n+")
    m = multiplereturns.sub("_newparagraph_", m)
    spaces = re.compile("(\n|[ ])+")
    m = spaces.sub(" ", m)

    """
     removes text between \iffalse ... \fi and
     between \iftex ... \fi keeps text between
     \ifblog ... \fi
    """

    ifcommands = re.compile("\\\\iffalse|\\\\ifblog|\\\\iftex|\\\\fi")
    L = ifcommands.split(m)
    I = ifcommands.findall(m)
    m = L[0]
    for i in range(1, (len(L)+1)//2):
        if I[2*i-2] == "\\ifblog":
            m = m+L[2*i-1]
        m = m+L[2*i]

    """
     changes $$ ... $$ into \[ ... \] and reformats
     eqnarray* environments as regular array environments
    """

    doubledollar = re.compile("\\$\\$")
    L = doubledollar.split(m)
    m = L[0]
    for i in range(1, (len(L)+1)//2):
        m = m + "\\[" + L[2*i-1] + "\\]" + L[2*i]

    m = m.replace("\\begin{eqnarray*}", "\\[ \\setlength\\arraycolsep{2pt} \\begin{array}{rcl}")
    m = m.replace("\\end{eqnarray*}", "\\end{array} \\]")

    return m


def convert_sqb(m):
    """
    reformats optional parameters passed in square brackets
    """

    r = re.compile("\\\\item\\s*\\[.*?\\]")

    Litems = r.findall(m)
    Lrest = r.split(m)

    m = Lrest[0]
    for i in range(0, len(Litems)):
      s = Litems[i]
      s = s.replace("\\item", "\\nitem")
      s = s.replace("[", "{")
      s = s.replace("]", "}")
      m = m+s+Lrest[i+1]

    r = re.compile("\\\\begin\\s*\\{\\w+}\\s*\\[.*?\\]")
    Lthms = r.findall(m)
    Lrest = r.split(m)

    m = Lrest[0]
    for i in range(0, len(Lthms)):
      s = Lthms[i]
      s = s.replace("\\begin", "\\nbegin")
      s = s.replace("[", "__{")
      s = s.replace("]", "__}")
      m = m+s+Lrest[i+1]

    return m


def convert_tables(m):
    """
    formats tables
    """

    retable = re.compile("\\\\begin\s*\\{tabular}.*?\\\\end\s*\\{tabular}")
    tables = retable.findall(m)
    rest = retable.split(m)

    m = rest[0]

    for i in range(len(tables)):
        m = m + convertonetable(tables[i])
        m = m + rest[i+1]
    return m


def convert_macros(m):
    """
    implement simple macros
    """
    comm = re.compile("\\\\[a-zA-Z]*")
    commands = comm.findall(m)
    rest = comm.split(m)


    r = rest[0]
    for i in range(len(commands)):
        for s1, s2 in M:
            if s1 == commands[i]:
                commands[i] = s2
        r = r+commands[i]+rest[i+1]
    return r


def convertonetable(m):
    tokens = re.compile("\\\\begin\\{tabular}\s*\\{.*?}"
                        "|\\\\end\\{tabular}"
                        "|&|\\\\\\\\")

    align = {"c": "center", "l": "left", "r": "right"}

    m = m.replace("\\hline", "")
    T = tokens.findall(m)
    C = tokens.split(m)

    L = cb.split(T[0])
    border = "|" in L[3]
    format = L[3].replace("|", "")

    columns = len(format)
    m = "<table style=\"width:auto;margin-left:auto;margin-right:auto; border-collapse:collapse;border:none\">"
    if border:
        padding = "padding:4;border:1px solid"
    else:
        padding = "border:none;"
    p = 1
    i = 0

    end1 = "\\end{tabular}"
    while T[p-1] != end1:
        # m = m + "<td align="+align[format[i]]+">" + C[p] + "</td>"
        cell = C[p].strip()
        if i == 0:
            if cell == "" and T[p] == end1:
                break
            m = m + "<tr>"
        m = m + "<td style=\"text-align:"+align[format[i]]+";" + padding + "\">" + cell + "</td>"
        p = p+1
        i = i+1
        if T[p-1] == "\\\\":
            for i in range(p,columns):
                m = m+"<td></td>"
            m = m+"</tr>"
            i = 0
    if i > 0:
        m = m + "</tr>"
    m = m + "</table>"
    return m
 

def separate_math(m):
    """
    extracts the math parts, and replaces the with placeholders
    """
    mathre = re.compile("\\$.*?\\$"
                        "|\\\\begin\\{equation}.*?\\\\end\\{equation}"
                        "|\\\\begin\\{html}.*?\\\\end\\{html}"
                        "|\\\\\\[.*?\\\\\\]")
    math = mathre.findall(m)
    text = mathre.split(m)
    return math, text


def process_math(M):
    R = []
    counteq = 0
    global ref

    mathdelim = re.compile("\\$"
                           "|\\\\begin\\{equation}"
                           "|\\\\end\\{equation}"
                           "|\\\\begin\\{html}"
                           "|\\\\end\\{html}"
                           "|\\\\\\[|\\\\\\]")
    label = re.compile("\\\\label\\{.*?}")
    
    for m in M:
        md = mathdelim.findall(m)
        mb = mathdelim.split(m)

        """
          In what follows, md[0] contains the initial delimiter,
          which is either \begin{equation}, or $, or \[, and
          mb[1] contains the actual mathematical equation
        """

        ishtml = False
        
        if md[0] == "$":
            if mb[1].startswith('\\html'):
                for e in esc:
                    mb[1] = mb[1].replace(e[1], e[0])
                m = math2html(mb[1][5:])
            elif HTML:
                m = m.replace("$", "")
                m = m.replace("+", "%2B")
                m = m.replace(" ", "+")
                m = m.replace("'", "&#39;")
                m = "<img src=\"http://l.wordpress.com/latex.php?latex=%7B"+m+"%7D"+endlatex+"\">"
            else:
                m = "$latex {"+mb[1]+"}"+endlatex+"$"

        else:
            #if md[0].find("\\begin") != -1:
            #   count["equation"] += 1
            #   mb[1] = mb[1] + "\\ \\ \\ \\ \\ ("+str(count["equation"])+")"
            if md[0].find("html") != -1:
                m = mb[1]
                ishtml = True	
            else:
                if HTML:
                    mb[1] = mb[1].replace("+", "%2B")
                    mb[1] = mb[1].replace("&", "%26")
                    mb[1] = mb[1].replace(" ", "+")
                    mb[1] = mb[1].replace("'", "&#39;")
                    m = "<img src=\"http://l.wordpress.com/latex.php?latex=\displaystyle "+mb[1]+endlatex+"\">"
                else:
                    m = "$latex \displaystyle "+mb[1]+endlatex+"$"
            if m.find("\\label") != -1:
                mnolab = label.split(m)
                mlab = label.findall(m)
                """
                 Now the mathematical equation, which has already
                 been formatted for WordPress, is the union of
                 the strings mnolab[0] and mnolab[1]. The content
                 of the \label{...} command is in mlab[0]
                """
                lab = mlab[0]
                lab = cb.split(lab)[1]
                lab = lab.replace(":", "")
                count["equation"] += 1
                ref[lab] = count["equation"]
                m = mnolab[0]+mnolab[1]

                mcell = "<td " + eqtdstyle + ">"+m+"</td>"
                numcell = "<td style=\"width:40px;white-space:nowrap;border:none;text-align:right;font-style:normal;padding:0;\">("+str(count["equation"])+")</td>"
                m = "\n<table id=\"" + labelpre + lab + "\" " + eqtblstyle + "><tr>" + mcell + numcell + "</tr></table>\n"
            else:
                m = "\n<table " + eqtblstyle + "><tr><td " + eqtdstyle + ">" + m + "</td></tr></table>\n"

        for e in esc:
            if ishtml:
                m = m.replace(e[1],e[2])
            else:
                m = m.replace(e[1],e[3])

        R = R + [m]

    return R


def convertcolors(m, c):
    if m.find("begin") != -1:
        return "<span style=\"color:#"+colors[c]+";\">"
    else:
        return"</span>"


def convertitm(m):
    if m.find("begin") != -1:
        return "\n<ul>"
    else:
        return "</ul>\n"


def convertenum(m):
    global itemno
    
    if m.find("begin") != -1:
        itemno = 0
        return "\n<ol>"
    else:
        itemno = -1
        return "</ol>\n"


def convertbeginnamedthm(thname, thm, thmlabel):
    global inthm
    global labelused

    count[T[thm]] += 1
    inthm = thm
    labelused = True
    t = beginnamedthm.replace("_ThmType_", thm.capitalize())
    t = t.replace("_ThmNumb_", str(count[T[thm]]))
    t = t.replace("_ThmName_", thname)
    if thmlabel == "":
        t = t.replace("_ThmLabel_", "")
    else:
        t = t.replace("_ThmLabel_", " id=\""+labelpre+thmlabel+"\"")
    return t


def convertbeginthm(thm, thmlabel):
    global inthm
    global labelused

    count[T[thm]] += 1
    inthm = thm
    labelused = True
    t = beginthm.replace("_ThmType_", thm.capitalize())
    t = t.replace("_ThmNumb_", str(count[T[thm]]))
    if thmlabel == "":
        t = t.replace("_ThmLabel_", "")
    else:
        t = t.replace("_ThmLabel_", " id=\""+labelpre+thmlabel+"\"")
    return t


def convertendthm(thm):
    global inthm

    inthm = ""
    return endthm


def convertlab(m):
    global inthm
    global ref
    global itemno
    
    m = cb.split(m)[1]
    m = m.replace(":", "")
    if inthm != "":
        ref[m] = count[T[inthm]]
    elif itemno > 0:
        ref[m] = itemno
    else:
        ref[m] = count["section"]
    return "<a name=\""+labelpre+m+"\"></a>"


def convertproof(m):
    if m.find("begin") != -1:
        return beginproof
    else:
        return endproof

def convertnamedproof(m, label):
    if m.find("begin") != -1:
        return beginnamedproof.replace("_PfName_", label)
    else:
        return endproof

def convertsection(m, label):
      global labelused
 
      labelused = True
      L=cb.split(m)

      """
        L[0] contains the \\section or \\section* command, and
        L[1] contains the section name
      """

      if L[0].find("*") == -1:
          t = section
          count["section"] += 1
          count["subsection"] = 0

      else:
          t = sectionstar

      t = t.replace("_SecNumb_", str(count["section"]))
      t = t.replace("_SecName_", L[1])
      if label == "":
          t = t.replace("_SecLabel_", "")
      else:
          t = t.replace("_SecLabel_", " id=\""+labelpre+label+"\"")
      return t

def convertsubsection(m, label):
    global labelused

    labelused = True
    L = cb.split(m)

    if L[0].find("*") == -1:
        t = subsection
    else:
        t = subsectionstar

    count["subsection"] += 1
    t = t.replace("_SecNumb_", str(count["section"]) )
    t = t.replace("_SubSecNumb_", str(count["subsection"]) )
    t = t.replace("_SecName_", L[1])     
    if label == "":
        t = t.replace("_SecLabel_", "")
    else:
        t = t.replace("_SecLabel_", " id=\""+labelpre+label+"\"")
    return t


def converturl(m):
    L = cb.split(m)
    return "<a href=\"" + L[1].replace("\\broot", "") + "\">" + L[3] + "</a>"

def converturlnosnap(m):
    L = cb.split(m)
    return "<a class=\"snap_noshots\" href=\"" + L[1].replace("\\broot", "") + "\">" + L[3] + "</a>"

def convertimage(m):
    L = cb.split(m)
    return "<span style=\"text-align:center\"><img "+L[1]+" src=\""+L[3]+"\"></span>"

def convertstrike(m):
    L = cb.split(m)
    return "<s>"+L[1]+"</s>"


def process_text(t):
    global itemno
    global labelused
        
    p = re.compile(r"\\begin\{\w+}"
                   r"|\\nbegin\{\w+}\s*__\{.*?__}"
                   r"|\\end\{\w+}"
                   r"|\\item"
                   r"|\\nitem\s*\{.*?}"
                   r"|\\label\s*\{.*?}"
                   r"|\\section\s*\{.*?}"
                   r"|\\section\*\s*\{.*?}"
                   r"|\\subsection\s*\{.*?}"
                   r"|\\subsection\*\s*\{.*?}"
                   r"|\\href\s*\{.*?}\s*\{.*?}"
                   r"|\\hrefnosnap\s*\{.*?}\s*\{.*?}"
                   r"|\\image\s*\{.*?}\s*\{.*?}\s*\{.*?}"
                   r"|\\sout\s*\{.*?}")

    for s1, s2 in Mnomath:
        t = t.replace(s1, s2)

    ttext = p.split(t)
    tcontrol = p.findall(t)

    w = ttext[0]

    i = 0
    isinthm = False # set to true if command is followed by label command. Label should be processed at the same time
    while i < len(tcontrol):
        if (i+1 < len(tcontrol)) and (tcontrol[i+1].find(r"\label") != -1):
            label = cb.split(tcontrol[i+1])[1]
            label = label.replace(":", "")
        else:
            label = ""
        labelused = False
        if tcontrol[i].find("{itemize}") != -1:
            converted = convertitm(tcontrol[i])
            if isinthm:
                converted = endthmblock + converted + beginthmblock
            w = w + converted
        elif tcontrol[i].find("{enumerate}") != -1:
            converted = convertenum(tcontrol[i])
            if isinthm:
                converted = endthmblock + converted + beginthmblock
            w = w + converted
        elif tcontrol[i][0:5]=="\\item":
            if isinthm:
                w = w + endthmblock + "<li>" + beginthmblock
            else:
                w=w + "<li>"
            if itemno != -1:
                itemno=itemno+1
        elif tcontrol[i][0:6]=="\\nitem":
                lb = tcontrol[i][7:].replace("{", "")
                lb = lb.replace("}", "")
                if isinthm:
                    w = w + endthmblock + "<li>" + lb + beginthmblock
                else:
                    w=w + "<li>" + lb
        elif tcontrol[i].find("\\hrefnosnap") != -1:
            w = w+converturlnosnap(tcontrol[i])
        elif tcontrol[i].find("\\href") != -1:
            w = w+converturl(tcontrol[i])
        elif tcontrol[i].find("{proof}") != -1:
            if tcontrol[i].startswith("\\n"):
                pfname = re.split("__\\}|__\\{", tcontrol[i])[1]
                w = w+convertnamedproof(tcontrol[i], pfname)
            else:
                w = w+convertproof(tcontrol[i])
        elif tcontrol[i].find("\\subsection") != -1:
            w = w+convertsubsection(tcontrol[i],label)
        elif tcontrol[i].find("\\section") != -1:
            w = w+convertsection(tcontrol[i],label)
        elif tcontrol[i].find("\\label") != -1:
            w=w+convertlab(tcontrol[i])
        elif tcontrol[i].find("\\image") != -1:
            w = w+convertimage(tcontrol[i])
        elif tcontrol[i].find("\\sout") != -1:
            w = w+convertstrike(tcontrol[i])
        elif tcontrol[i].find("\\begin") !=-1 and tcontrol[i].find("{center}")!= -1:
            w = w+"<div style=\"text-align:center\">"
        elif tcontrol[i].find("\\end")!= -1  and tcontrol[i].find("{center}") != -1:
            w = w+"</div>"
        else:
          for clr in colorchoice:
            if tcontrol[i].find("{"+clr+"}") != -1:
                w=w + convertcolors(tcontrol[i],clr)
          for thm in ThmEnvs:
            if tcontrol[i]=="\\end{"+thm+"}":
                w=w+convertendthm(thm)
                if not isinthm:
                    raise Exception("Theorem ended without begin")
                isinthm = False
            elif tcontrol[i]=="\\begin{"+thm+"}":
                w=w+convertbeginthm(thm,label)
                if isinthm:
                    raise Exception("Theorem inside theorem")
                isinthm = True
            elif tcontrol[i].find("\\nbegin{"+thm+"}") != -1:
                thmname = re.split("__\\}|__\\{", tcontrol[i])[1]
                w=w+convertbeginnamedthm(thmname,thm,label)
                if isinthm:
                    raise Exception("Theorem inside theorem")
                isinthm = True
        if labelused and label != "":
            w += ttext[i+1]
            i += 1
            convertlab(tcontrol[i])
        if isinthm:
            ttext[i+1] = ttext[i+1].replace("_newparagraph_", endthmblock + "_newparagraph_" + beginthmblock)
            ttext[i+1] = ttext[i+1].replace("__bmath", endthmblock + "__bmath")
            ttext[i+1] = ttext[i+1].replace("__emath", "__emath" + beginthmblock)
        w += ttext[i+1]
        i += 1

    return processfontstyle(w)

def processfontstyle(w):

        close = dict()
        ww = ""
        level = i = 0
        while i < len(w):
          special = False
          for k, v in fontstyle.items():
            l = len(k)
            if w[i:i+l] == k:
              level += 1
              ww += '<' + v + '>'
              close[level] = '</' + v + '>'
              i += l
              special = True
          if not special:
            if w[i] == '{':
              ww += '{'
              level += 1
              close[level] = '}'
            elif w[i] == '}' and level > 0:
              ww += close[level]
              level -= 1
            else:
              ww += w[i]
            i += 1
        return ww
    

def convert_ref(m):
    global ref
    
    p=re.compile("\\\\ref\s*\\{.*?}|\\\\eqref\s*\\{.*?}")

    T=p.split(m)
    M=p.findall(m)

    w = T[0]
    for i in range(len(M)):
        t=M[i]
        lab=cb.split(t)[1]
        lab=lab.replace(":", "")
        if t.find("\\eqref") != -1:
           w=w+"<a href=\"#"+labelpre+lab+"\">("+str(ref[lab])+")</a>"
        else:
           w=w+"<a href=\"#"+labelpre+lab+"\">"+str(ref[lab])+"</a>"
        w=w+T[i+1]
    return w

"""
The program makes several passes through the input.

In a first clean-up, all text before \begin{document}
and after \end{document}, if present, is removed,
all double-returns are converted
to <p>, and all remaining returns are converted to
spaces. If \labelpre command is present before begin{document},
this used to prepend all labels

The second step implements a few simple macros. The user can
add support for more macros if desired by editing the
convertmacros() procedure.

Then the program separates the mathematical
from the text parts. (It assumes that the document does
not start with a mathematical expression.) 

It makes one pass through the text part, translating
environments such as theorem, lemma, proof, enumerate, itemize,
\em, and \bf. Along the way, it keeps counters for the current
section and subsection and for the current numbered theorem-like
environment, as well as a  flag that tells whether one is
inside a theorem-like environment or not. Every time a \label{xx}
command is encountered, we give ref[xx] the value of the section
in which the command appears, or the number of the theorem-like
environment in which it appears (if applicable). Each appearence
of \label is replace by an html "name" tag, so that later we can
replace \ref commands by clickable html links.

The next step is to make a pass through the mathematical environments.
Displayed equations are numbered and centered, and when a \label{xx}
command is encountered we give ref[xx] the number of the current
equation. 

A final pass replaces \ref{xx} commands by the number in ref[xx],
and a clickable link to the referenced location.
"""


def text2wp(s: str) -> str:
    s = extract_body(s)
    s = convert_tables(s)
    s = convert_sqb(s)
    s = convert_macros(s)
    (math, text) = separate_math(s)

    # processes math and text separately, then puts the processed
    # math equations in place of the placeholders
    s = text[0]
    for i in range(len(math)):
        s = s+"__bmath"+str(i)+"__emath"+text[i+1]

    s = process_text(s)
    math = process_math(math)

    # converts escape sequences such as \$ to HTML codes
    # This must be done after formatting the tables or the '&' in
    # the HTML codes will create problems

    for e in esc:
        s = s.replace(e[1],e[2])

    # puts the math equations back into the text

    for i in range(len(math)):
        s = s.replace("__bmath"+str(i)+"__emath",math[i])

    # translating the \ref{} commands
    s = convert_ref(s)

    if HTML:
        s = "<head><style>body{max-width:55em;}a:link{color:#4444aa;}a:visited{color:#4444aa;}a:hover{background-color:#aaaaFF;}</style></head><body>"+s+"</body></html>"

    s = s.replace("_newparagraph_", "</p>\n<p>")
    s = s.replace("<i> </i>", " ")

    return s


if len(argv) > 1:
    inputfile = argv[1]
else:
    inputfile = 'test.tex'

print(inputfile)
if len(argv) > 2:
    outputfile = argv[2]
else:
    outputfile = inputfile.replace(".tex", ".html")

with open(inputfile) as f:
    s = f.read()

s = text2wp(s)

with open(outputfile, "w") as f:
    f.write(s)
