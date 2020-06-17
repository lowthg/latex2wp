@echo on
del "%1.html"
python %HOMEPATH%/Documents/GitHub/latex2wp/latex2wp.py "%1.tex"
notepad "%1.html"