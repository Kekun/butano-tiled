all:
	python -B ../../bntmx.py --target=c --build=build ../../maps
	gcc -Ibuild/include main.c build/src/* -o build/example

clean:
	rm -rf build
