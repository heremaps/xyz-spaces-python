Contributing to xyzspaces
=========================

Overview
--------

Contributions to xyzspaces are very welcome.  They are likely to
be accepted more quickly if they follow these guidelines.

Below are guidelines, when submitting a pull request:

- All existing tests should pass. Please make sure that the test
  suite passes, both locally and on
  `Travis CI <https://travis-ci.com/github/heremaps/xyz-spaces-python>`_.  Status on
  Travis will be visible on a pull request.

- New functionality should include tests.  Please write reasonable
  tests for your code and make sure that they pass on your pull request.

- Classes, methods, functions, etc. should have docstrings.  The first
  line of a docstring should be a standalone summary.  Parameters and
  return values should be documented explicitly.

- Follow PEP 8 when possible. We use `Black
  <https://black.readthedocs.io/en/stable/>`_,  `Flake8
  <http://flake8.pycqa.org/en/latest/>`_, `isort <https://pypi.org/project/isort/>`_, `typing <https://pypi.org/project/typing/>`_ and `darglint <https://pypi.org/project/darglint/>`_ to ensure a consistent code
  format throughout the project. For more details see
  :ref:`below <contributing_style>`.

- Imports should be grouped with standard library imports first,
  3rd-party libraries next, and xyzspaces imports third.  Within each
  grouping, imports should be alphabetized.  Always use absolute
  imports when possible, and explicit relative imports for local
  imports when necessary in tests.

- xyzspaces supports Python 3.6+.


Seven Steps for Contributing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are seven basic steps to contributing to *xyzspaces*:

1) Fork the *xyzspaces* git repository
2) Create a development environment
3) Install *xyzspaces* dependencies
4) Make changes to code and add tests
5) Run linting
6) Update the documentation
7) Submit a Pull Request

Each of these 7 steps is detailed below.


1) Forking the *xyz-spaces-python* repository using Git
-------------------------------------------------------

To the new user, working with Git is one of the more daunting aspects of contributing to *xyzspaces**.
It can very quickly become overwhelming, but sticking to the guidelines below will help keep the process
straightforward and mostly trouble free.  As always, if you are having difficulties please
feel free to ask for help.

The code is hosted on `GitHub <https://github.com/heremaps/xyz-spaces-python>`_. To
contribute you will need to sign up for a `free GitHub account
<https://github.com/signup/free>`_.

Some great resources for learning Git:

* Software Carpentry's `Git Tutorial <http://swcarpentry.github.io/git-novice/>`_
* `Atlassian <https://www.atlassian.com/git/tutorials/what-is-version-control>`_
* the `GitHub help pages <http://help.github.com/>`_.
* Matthew Brett's `Pydagogue <http://matthew-brett.github.com/pydagogue/>`_.

Getting started with Git
~~~~~~~~~~~~~~~~~~~~~~~~

`GitHub has instructions <http://help.github.com/set-up-git-redirect>`__ for installing git,
setting up your SSH key, and configuring git.  All these steps need to be completed before
you can work seamlessly between your local repository and GitHub.

.. _contributing.forking:

Forking
~~~~~~~

You will need your own fork to work on the code. Go to the `xyz-spaces-python project
page <https://github.com/heremaps/xyz-spaces-python>`_ and hit the ``Fork`` button. You will
want to clone your fork to your machine::

    git clone git@github.com:your-user-name/xyz-spaces-python.git xyz-spaces-python-yourname
    cd xyz-spaces-python-yourname
    git remote add upstream git://github.com/heremaps/xyz-spaces-python.git

This creates the directory `xyz-spaces-python-yourname` and connects your repository to
the upstream (main project) *xyzspaces* repository.

The testing suite will run automatically on Travis-CI once your pull request is
submitted.  However, if you wish to run the test suite on a branch prior to
submitting the pull request, then Travis-CI needs to be hooked up to your
GitHub repository.  Instructions for doing so are `here
<http://about.travis-ci.org/docs/user/getting-started/>`__.

Creating a branch
~~~~~~~~~~~~~~~~~~

You want your master branch to reflect only production-ready code, so create a
feature branch for making your changes. For example::

    git branch shiny-new-feature
    git checkout shiny-new-feature

The above can be simplified to::

    git checkout -b shiny-new-feature

This changes your working directory to the shiny-new-feature branch.  Keep any
changes in this branch specific to one bug or feature so it is clear
what the branch brings to *xyzspaces*. You can have many shiny-new-features
and switch in between them using the git checkout command.

To update this branch, you need to retrieve the changes from the master branch::

    git fetch upstream
    git rebase upstream/master

This will replay your commits on top of the latest xyzspaces git master.  If this
leads to merge conflicts, you must resolve these before submitting your pull
request.  If you have uncommitted changes, you will need to ``stash`` them prior
to updating.  This will effectively store your changes and they can be reapplied
after updating.

.. _contributing.dev_env:

2) Creating a development environment
---------------------------------------
A development environment is a virtual space where you can keep an independent installation of *xyzspaces*.
This makes it easy to keep both a stable version of python in one place you use for work, and a development
version (which you may break while playing with code) in another.

An easy way to create a *xyzspaces* development environment is as follows:

- Install either `Anaconda <http://docs.continuum.io/anaconda/>`_ or
  `miniconda <http://conda.pydata.org/miniconda.html>`_
- Make sure that you have :ref:`cloned the repository <contributing.forking>`
- ``cd`` to the *xyzspaces** source directory

Tell conda to create a new environment, named ``xyz_dev``, or any other name you would like
for this environment, by running::

      conda create -n xyz_dev python

This will create the new environment, and not touch any of your existing environments,
nor any existing python installation.

To work in this environment, you need to ``activate`` it. The instructions below
should work for both Windows, Mac and Linux::

      conda activate xyz_dev

Once your environment is activated, you will see a confirmation message to
indicate you are in the new development environment.

To view your environments::

      conda info -e

To return to you home root environment::

      conda deactivate

See the full conda docs `here <http://conda.pydata.org/docs>`__.

At this point you can easily do a *development* install, as detailed in the next sections.

3) Installing Dependencies
--------------------------

To run *xyzspaces* in an development environment, you must first install
*xyzspaces*'s dependencies. We suggest doing so using the following commands
(executed after your development environment has been activated)::

    pip install -r requirements.txt
    pip install -r requirements_dev.txt

This should install all necessary dependencies.


4) Making changes and writing tests
-------------------------------------

*xyzspaces* is serious about testing and strongly encourages contributors to embrace
`test-driven development (TDD) <http://en.wikipedia.org/wiki/Test-driven_development>`_.
This development process "relies on the repetition of a very short development cycle:
first the developer writes an (initially failing) automated test case that defines a desired
improvement or new function, then produces the minimum amount of code to pass that test."
So, before actually writing any code, you should write your tests.  Often the test can be
taken from the original GitHub issue.  However, it is always worth considering additional
use cases and writing corresponding tests.

Adding tests is one of the most common requests after code is pushed to *xyzspaces*.  Therefore,
it is worth getting in the habit of writing tests ahead of time so this is never an issue.

*xyzspaces* uses the `pytest framework <http://doc.pytest.org/en/latest/>`_.

Writing tests
~~~~~~~~~~~~~

All tests should go into the ``tests`` directory. This folder contains many
current examples of tests, and we suggest looking to these for inspiration.

Running the test suite
~~~~~~~~~~~~~~~~~~~~~~

The tests can then be run directly inside your Git clone (without having to
install *xyzspaces*) by typing::

    pytest -v --cov=xyzspaces tests

5) Run linting
----------------
For linting please refer :ref:`contributing style <contributing_style>`

6) Updating the Documentation
-----------------------------

*xyzspaces* documentation resides in the `docs` folder. Changes to the docs are
make by modifying the appropriate file in the `source` folder within `docs`.
*xyzspaces* docs use reStructuredText syntax, `which is explained here <http://www.sphinx-doc.org/en/stable/rest.html#rst-primer>`_
and the docstrings follow the `Sphinx Docstring standard <https://www.sphinx-doc.org/en/master/>`_.

Once you have made your changes, you may try if they render correctly by
building the docs using sphinx. To do so, you can type from project's root folder::

    sh scripts/build_docs.sh

The resulting html pages will be located in `docs/source/_build/html`.

7) Submitting a Pull Request
------------------------------

Once you've made changes and pushed them to your forked repository, you then
submit a pull request to have them integrated into the *xyzspaces* code base.

You can find a pull request (or PR) tutorial in the `GitHub's Help Docs <https://help.github.com/articles/using-pull-requests/>`_.

.. _contributing_style:

Style Guide & Linting
---------------------

xyzspaces follows the `PEP8 <http://www.python.org/dev/peps/pep-0008/>`_ standard
and uses `Black <https://black.readthedocs.io/en/stable/>`_,
`Flake8 <http://flake8.pycqa.org/en/latest/>`_, `isort <https://pypi.org/project/isort/>`_, `typing <https://pypi.org/project/typing/>`__ and `darglint <https://pypi.org/project/darglint/>`_ to ensure a consistent code
format throughout the project.

Continuous Integration (Travis CI) will run those tools and
report any stylistic errors in your code. Therefore, it is helpful before
submitting code to run the check yourself. To autoformat the code run::

    make black

To check linting errors run::

    make lint

To check typing errors run::

    make typing

Signing each Commit
--------------------------
As part of filing a pull request we ask you to sign off the Developer Certificate of Origin (DCO) in each commit. Any Pull Request with commits that are not signed off will be reject by the DCO check.
A DCO is lightweight way for a contributor to confirm that you wrote or otherwise have the right to submit code or documentation to a project. Simply add Signed-off-by as shown in the example below to indicate that you agree with the DCO.
An example signed commit message::

    README.md: Fix minor spelling mistake
    Signed-off-by: John Doe <john.doe@example.com>

Git has the -s flag that can sign a commit for you, see example below::

    $ git commit -s -m 'README.md: Fix minor spelling mistake'


