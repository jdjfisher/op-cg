.SILENT:

seq:
	python3 opcg seq -vdm examples/fortran/airfoil/airfoil.F90 -o temp

cuda:
	python3 opcg cuda -vdm examples/fortran/airfoil/airfoil.F90 -o temp

install:
	pip3 install -r requirements.txt

test:
	pytest

clean:
	rm temp/*