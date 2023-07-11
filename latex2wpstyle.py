"""
 Copyright 2009 Luca Trevisan

 Additional contributors: Radu Grigore

 LaTeX2WP version 0.6.2

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

# Lines starting with #, like this one, are comments

# change to HTML = True to produce standard HTML
HTML = False

# color of LaTeX formulas
textcolor = "000000"

# colors that can be used in the text
colors = { "red" : "ff0000" , "green" : "00ff00" , "blue" : "0000ff" }
# list of colors defined above
colorchoice = ["red","green","blue"]


# counters for theorem-like environments
# assign any counter to any environment. Make sure that
# maxcounter is an upper bound to the any counter being used

T = {"theorem": 0, "lemma": 0, "proposition": 0, "definition": 0,
               "corollary": 0, "remark": 3, "example": 1, "claim": 4,
               "exercise": 2, "conjecture": 0}

# list of theorem-like environments
ThmEnvs = ["theorem","definition","lemma","proposition","corollary","claim",
           "remark","example","exercise", "conjecture"]

# the way \begin{theorem}, \begin{lemma} etc are translated in HTML
# the string _ThmType_ stands for the type of theorem
# the string _ThmNumb_ is the theorem number
# the string _ThmLabel_ is replaced by "" or "id=.."
# beginthmblock and endthmblock are used to end and start new paragraphs inside the thm environment
beginthm = "\n<blockquote_ThmLabel_ style=\"margin-right:0px;font-style:normal\"><b>_ThmType_ _ThmNumb_</b> <i>"

# translation of \begin{theorem}[...]. The string
# _ThmName_ stands for the content betwee the
# square brackets
beginnamedthm = "\n<blockquote_ThmLabel_ style=\"margin-right:0;font-style:normal\"><b>_ThmType_ _ThmNumb_ (_ThmName_)</b> <i>"
endthmblock = "</i>"
beginthmblock = "<i>"


#translation of \end{theorem}, \end{lemma}, etc.
endthm = "</i></blockquote>\n<p>\n"


beginproof = "<em>Proof:</em> "
beginnamedproof = "<em>Proof _PfName_:</em> "
endproof = "&#x2b1c;\n\n"

section = "\n<p>\n<hr>\n<h3_SecLabel_>_SecNumb_. _SecName_ </h3>\n<p>\n"
sectionstar = "\n<p>\n<hr>\n<h3_SecLabel_> _SecName_ </h3>\n<p>\n"
subsection = "\n<p>\n<hr>\n<h4_SecLabel_>  _SecNumb_._SubSecNumb_. _SecName_ </h4>\n<p>\n"
subsectionstar = "\n<p>\n<hr>\n<h4_SecLabel_> _SecName_ </h4>\n<p>\n"

# styling for math table
eqtblstyle = 'style="width:100%;border:none;margin-top:0;margin-bottom:0"'
eqtdstyle = 'style="border:none;text-align:center;padding:0"'

# Font styles. Feel free to add others. The key *must* contain
# an open curly bracket. The value is the namem of a HTML tag.
fontstyle = {
  r'{\em ' : 'em',
  r'{\bf ' : 'b',
  r'{\it ' : 'i',
  r'{\sl ' : 'i',
  r'\textit{' : 'i',
  r'\textsl{' : 'i',
  r'\emph{' : 'em',
  r'\textbf{' : 'b',
}

# Macro definitions
# It is a sequence of pairs [string1,string2], and
# latex2wp will replace each occurrence of string1 with an
# occurrence of string2. The substitutions are performed
# in the same order as the pairs appear below.
# Feel free to add your own.
# Note that you have to write \\ instead of \
# and \" instead of "

M = [     ["\\to","\\rightarrow"] ,
          ["\\B","\\{ 0,1 \\}" ],
#          ["\\E","\mathop{\\mathbb E}"],
          ["\\E","{\\mathbb E}"],
#          ["\\P","\mathop{\\mathbb P}"],
          ["\\P","{\\mathbb P}"],
          ["\\N","{\\mathbb N}"],
          ["\\Z","{\\mathbb Z}"],
          ["\\C","{\\mathbb C}"],
          ["\\R","{\\mathbb R}"],
          ["\\Q","{\\mathbb Q}"],
          ["\\xor","\\oplus"],
          ["\\eps","\\epsilon"],
          ["\\<","&lt;"],
          ["\\dart","&#x27A2;"]
    ]

