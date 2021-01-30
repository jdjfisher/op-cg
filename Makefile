# .SILENT:

all:
	exit

fseq: # temp for development 
	python3 opcg seq -vd -soa examples/fortran/airfoil/airfoil.F90 -o temp/

fcuda: # temp for development 
	python3 opcg cuda -vd examples/fortran/airfoil/airfoil.F90 -o temp/

cseq: # temp for development 
	python3 opcg seq -vd examples/cpp/airfoil/airfoil.cpp -o temp/

install:
	pip3 install -r requirements.txt

alias:
	echo 'Create an alias with this' 
	alias opcg="python3 ${CURDIR}/opcg"

lint:
	mypy opcg
	pylint opcg --indent-string='  '

test:
	pytest

clean:
	rm -r temp/*