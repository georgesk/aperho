DESTDIR = 

clean:
	find . -name "*~" -o -name "__pycache__" | xargs rm -rf

build:

install:

.PHONY: clean build install
