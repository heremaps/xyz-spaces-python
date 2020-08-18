.PHONY: all build install typing lint test

all: black build install typing lint test

black:
	black -l 79 xyzspaces tests
	isort --atomic .

build:
	python3 -m pip install -r requirements.txt

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .mypy_cache
	rm -fr .pytest_cache
	find . -name '.ipynb_checkpoints' -exec rm -fr {} +

dockerize:
	jupyter-repo2docker --user-id 1000 --env XYZ_TOKEN=${XYZ_TOKEN} .

install:
	python3 -m pip install -e .

typing:
	pytest -v -s --mypy xyzspaces

lint:
	isort --check --diff xyzspaces tests
	flake8 -v --statistics --count .
	black -l 79 --diff --check xyzspaces tests

test:
	pytest -v -s --cov=xyzspaces tests
	coverage html

draft_changelog:
	proclamation draft $(shell python -c "import xyzspaces; print(xyzspaces.__version__)")

build_changelog:
	proclamation build -o  $(shell python -c "import xyzspaces; print(xyzspaces.__version__)")
