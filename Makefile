
.PHONY: typecheck tc
typecheck:
	pytest --mypy -m mypy
tc: typecheck
