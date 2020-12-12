.SILENT:

seq:
	python3 opcg seq -vd examples/fortran/airfoil/airfoil.F90 -o temp

cuda:
	python3 opcg cuda -vd examples/fortran/airfoil/airfoil.F90 -o temp

install:
	pip3 install -r requirements.txt

test:
	echo "wip"

clean:
	rm temp/*