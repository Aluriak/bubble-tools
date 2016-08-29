
BUBBLE=complex
BUBBLE=basic
BUBBLE=loop
BUBBLE=overlap

CMD=python3 -m bubbletools

v:
	$(CMD) --validate bubbles/$(BUBBLE).bbl --profiling
c:
	$(CMD) --dot bubbles/$(BUBBLE).bbl


t: tests
tests:
	py.test bubbletools --doctest-module -v



