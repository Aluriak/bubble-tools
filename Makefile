# Options
RENDER=--render
ORIENTED=--oriented
TO=dot
TO=gexf

# TARGET
BUBBLE=overlap
BUBBLE=empty_pwn
BUBBLE=loop
BUBBLE=singleton
BUBBLE=complex
BUBBLE=disjoint
BUBBLE=basic
BUBBLE=hard_test


CMD=python3 -m bubbletools
OPT=$(RENDER) $(ORIENTED)

validate:
	$(CMD) validate bubbles/$(BUBBLE).bbl --profiling
dot:
	$(CMD) dot bubbles/$(BUBBLE).bbl output/$(BUBBLE).dot $(OPT)
gexf:
	$(CMD) gexf bubbles/$(BUBBLE).bbl output/$(BUBBLE).gexf $(ORIENTED)
embedded-js:
	# generate only one html file
	$(CMD) js bubbles/$(BUBBLE).bbl output/js-single-file.html $(ORIENTED) --render width_as_cover=True
js:
	$(CMD) js bubbles/$(BUBBLE).bbl output/test-site $(ORIENTED) --render width_as_cover=True
js-per-file:
	# same recipe as above, but with manual recreation of test-site and generation of only graph/code.js
	- rm -r output/test-site-single-file/
	cp -r bubbletools/_js_dir_template output/test-site-single-file/
	$(CMD) js bubbles/$(BUBBLE).bbl output/test-site-single-file/js/graph.js $(ORIENTED)
	xdg-open ./output/test-site-single-file/index.html


t: tests
tests:
	pytest bubbletools/ -vv --doctest-module


##########################################
#### PYPI
##########################################
test_register:
	python3 setup.py register -r https://testpypi.python.org/pypi
test_upload:
	python3 setup.py sdist upload -r https://testpypi.python.org/pypi
test_install:
	pip3 install -U -i https://testpypi.python.org/pypi bubbletools

register:
	python3 setup.py register
upload:
	python3 setup.py sdist upload
install:
	yes y | pip3 uninstall bubbletools
	pip3 install bubbletools
install_deps:
	python -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); print(c['options']['install_requires'])" | xargs pip install -U
fullrelease:
	fullrelease
