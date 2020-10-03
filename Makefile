.PHONY: typecheck tc test
typecheck:
	mypy src/ tests/
tc: typecheck
test:
	pytest
