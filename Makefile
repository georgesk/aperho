# fichier Makefile principal du projet APERHO

SOURCES = $(shell find . -name "*.py" | grep -v manage.py)
VERSION_DOXY = $(shell grep "PROJECT_NUMBER  " Doxyfile | awk '{print $$3}')
VERSION_GIT  = $(shell git tag | tail -1| sed 's/v\(.*\)/\1/')

all: version doc/html/index.html

clean:
	rm -rf doc/*

doc/html/index.html: Doxyfile $(SOURCES)
	doxygen Doxyfile
	
version:
	@if [ "$(VERSION_DOXY)" = "$(VERSION_GIT)" ]; then \
	  echo "Version OK : $(VERSION_DOXY)"; \
	else \
	  echo "Upgraded to $(VERSION_GIT)"; \
	  sed 's/\(PROJECT_NUMBER *= *\).*/\1$(VERSION_GIT)/' Doxyfile > \
	    Doxyfile.tmp && mv Doxyfile.tmp Doxyfile; \
	fi

.PHONY: all clean version
