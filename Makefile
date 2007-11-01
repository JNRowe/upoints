#
# vim: set sw=4 sts=4 tw=80 fileencoding=utf-8:
#
# earth_distance - Modules for working with points on a spherical object
# Copyright (C) 2007  James Rowe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

PYFILES := $(wildcard earth_distance/*.py)

PACKAGE_NAME := earth_distance
SNAPSHOT_DATE := $(shell date -I)

PYTHON := python
PYTHON_ENV := PYTHONPATH=$$PYTHONPATH:$(shell pwd)

RST2HTML := rst2html.py
RST2HTML_OPTIONS := --source-link --strict --generator \
	--stylesheet-path=doc/docutils.css --link-stylesheet

NOSE := nosetests
NOSE_OPTIONS := --with-doctest --with-coverage --cover-tests \
	--cover-inclusive --cover-package=$(PACKAGE_NAME) $(PACKAGE_NAME)

.PHONY: ChangeLog MANIFEST .hg_version check check-nose check-no_nose \
	check-docs clean dist docs snapshot

all: docs

DOCS := $(patsubst %.txt, %.html, $(wildcard doc/*.txt))
docs: html/index.html README.html $(DOCS)

%.html: %.txt
	$(RST2HTML) $(RST2HTML_OPTIONS) $< $@

html/index.html: $(PYFILES)
	epydoc $(PYFILES)

README.html: README
	$(RST2HTML) $(RST2HTML_OPTIONS) $< $@

check: check-docs check-nose
check-nose:
	echo ">>> nosetests"; \
	$(NOSE) $(NOSE_OPTIONS); \

check-no_nose: check-docs
	for i in $(PYFILES); do \
		echo ">>> $$i"; \
		module=`echo $$i | sed -e 's,\(.*\)/\(.*\).py,\1.\2,' -e 's,.__init__,,'`; \
		$(PYTHON_ENV) $(PYTHON) -c "import doctest, sys, $(PACKAGE_NAME); "\
			"sys.exit(doctest.testmod($$module,"\
			"optionflags=doctest.REPORT_UDIFF)[0])"; \
	done; \

check-docs:
	echo ">>> README"; \
	$(PYTHON_ENV) $(PYTHON) -c "import doctest, sys; sys.exit(doctest.testfile('README')[0])"

clean:
	rm -rf .hg_version ChangeLog MANIFEST README.html html \
		$(patsubst %.py, %.pyc, $(PYFILES))
	./setup.py clean --all

dist: check ChangeLog MANIFEST .hg_version
	./setup.py sdist

.hg_version:
	hg identify >$@

ChangeLog:
	hg log --no-merges --style changelog >$@

MANIFEST: docs
	hg manifest >$@
	echo $@ >>$@
	echo ChangeLog >>$@
	echo "README.html" >>$@
	find doc -name \*.html >>$@
	echo ".hg_version" >>$@
	find html -not -type d >>$@

snapshot: check ChangeLog
	rm -rf $(PACKAGE_NAME)-$(SNAPSHOT_DATE) \
		dist/$(PACKAGE_NAME)-$(SNAPSHOT_DATE).tar.bz2
	hg archive dist/$(PACKAGE_NAME)-$(SNAPSHOT_DATE)
	cp ChangeLog dist/$(PACKAGE_NAME)-$(SNAPSHOT_DATE)
	
	cd dist; \
		tar --create --bzip2 --file=$(PACKAGE_NAME)-$(SNAPSHOT_DATE).tar.bz2 \
		$(PACKAGE_NAME)-$(SNAPSHOT_DATE)
	
	rm -rf dist/$(PACKAGE_NAME)-$(SNAPSHOT_DATE)

