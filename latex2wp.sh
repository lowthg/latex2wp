#! /bin/bash
rm -f "$1.html"
python ~/Documents/GitHub/latex2wp/latex2wp.py "$1.tex"
open -e "$1.html"
