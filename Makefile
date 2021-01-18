# .SILENT:

all:
	exit

fseq: # temp for development 
	python3 opcg seq -vdm examples/fortran/airfoil/airfoil.F90 -o temp/

fcuda: # temp for development 
	python3 opcg cuda -vdm examples/fortran/airfoil/airfoil.F90 -o temp/

cseq: # temp for development 
	python3 opcg seq -vdm examples/cpp/airfoil/airfoil.cpp -o temp/

install:
	pip3 install -r requirements.txt

lint:
	mypy opcg
	pylint opcg --indent-string='  '

test:
	pytest

clean:
	rm -r temp/*