all:
	python -B ../../bntmx.py --target=c --grit=grit --build=build ../../maps
	gcc -Ibuild main.c ../../templates/c/bntmx.c build/src/* -o build/example

clean:
	rm -rf build
