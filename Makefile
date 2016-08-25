
BUBBLE=complex
BUBBLE=basic
BUBBLE=loop
BUBBLE=overlap


v:
	python3 bubble.py --validate bubbles/$(BUBBLE).bbl --profiling
c:
	python3 bubble.py --dot bubbles/$(BUBBLE).bbl


t: tests
tests:
	py.test . --doctest-module -v



