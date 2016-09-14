
BUBBLE=overlap
BUBBLE=empty_pwn
BUBBLE=complex
BUBBLE=loop
BUBBLE=singleton
BUBBLE=basic
BUBBLE=disjoint


CMD=python3 -m bubbletools

v:
	$(CMD) validate bubbles/$(BUBBLE).bbl --profiling
c:
	$(CMD) dot bubbles/$(BUBBLE).bbl


t: tests
tests:
	py.test bubbletools --doctest-module -v


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
