#! /bin/bash
rm -f "$1.html"
python3 ~/Documents/GitHub/latex2wp/latex2wp3.py "$1.tex"
open -e "$1.html"
