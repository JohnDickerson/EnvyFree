filename="scratch"

pdf:
	pdflatex ${filename}
	bibtex ${filename}||true
	bibtex ${filename}||true
	pdflatex ${filename}
	pdflatex ${filename}

read:	
	evince ${filename}.pdf &

clean:
	rm -f ${filename}.ps ${filename}.pdf ${filename}.log ${filename}.aux ${filename}.out ${filename}.dvi ${filename}.bbl ${filename}.blg *~
