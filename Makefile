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


t: tests
tests:
	pytest bubbletools/ --doctest-module -v


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
