check:
	pycodestyle autopep8_quotes/autopep8_quotes.py setup.py
	pydocstyle autopep8_quotes/autopep8_quotes.py setup.py
	pylint \
		--reports=no \
		--disable=invalid-name \
		--disable=inconsistent-return-statements \
		--rcfile=/dev/null \
		autopep8_quotes/autopep8_quotes.py setup.py
	rstcheck README.rst
	scspell autopep8_quotes/autopep8_quotes.py setup.py tests/test_unify.py README.rst

coverage:
	@rm -f .coverage
	@coverage run tests/test_unify.py
	@coverage report
	@coverage html
	@rm -f .coverage
	@python -m webbrowser -n "file://${PWD}/htmlcov/index.html"

mutant:
	@mut.py -t autopep8_quotes -u tests/test_unify.py -mc

readme:
	@restview --long-description --strict
