
BUBBLE=complex
BUBBLE=basic
BUBBLE=loop
BUBBLE=overlap


c:
	python3 bubble.py --dot bubbles/$(BUBBLE).bbl
v:
	python3 bubble.py --validate bubbles/$(BUBBLE).bbl --profiling


t: tests
tests:
	py.test . --doctest-module -v



