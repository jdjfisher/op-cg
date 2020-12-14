.SILENT:

fseq:
	python3 opcg seq -vdm examples/fortran/airfoil/airfoil.F90 -o temp/seq

fcuda:
	python3 opcg cuda -vdm examples/fortran/airfoil/airfoil.F90 -o temp/cuda

cseq:
	python3 opcg seq -vdm examples/cpp/airfoil/airfoil.cpp -o temp/

install:
	pip3 install -r requirements.txt

test:
	pytest

clean:
	rm -r temp/*