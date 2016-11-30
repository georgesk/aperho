# fichier Makefile principal du projet APERHO

SOURCES = $(shell find . -name "*.py" | grep -v manage.py)

all: doc/html/index.html

clean:
	rm -rf doc/*

doc/html/index.html: Doxyfile $(SOURCES)
	doxygen Doxyfile

.PHONY: all clean
