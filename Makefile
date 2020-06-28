cov:
	pytest -m "wbox or bbox" --cov=. --cov-config=coverage.ini --cov-report term-missing --cov-report html
