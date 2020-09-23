# Contributing to XYZ Spaces for Python

Thank you for taking the time to contribute.

The following is a set of guidelines for contributing to this package.
These are mostly guidelines, not rules. Use your best judgement and feel free to propose
changes to this document in a pull request.

## Coding Guidelines
1. Lint your code contributions as per [pep8 guidelines](https://www.python.org/dev/peps/pep-0008/).

To help you out, we have included a `Makefile` in the root directory which supports the commands below:

Autoformat code using black:

```bash
make black
```

Check for typing errors:

```bash
make typing
```

Check for linting errors:

```bash
make lint
```

Run tests and coverage:

```bash
make test
```

2. Sort the imports in each python file as per [pep8 guidelines](https://www.python.org/dev/peps/pep-0008/#imports)
   Please execute the isort utility to have the imports sorted auto-magically.

#### Scripts

The scripts below are present in [/scripts](./scripts) directory:

- `build_docs.sh` to create internal API reference documentation
- `check_xyz_platform.py` runs a smoke test to check if the XYZ platform is alive and kicking
- `walk_spaces.py` can serve as a template for building a maintenance script walking overall spaces

#### Notebooks

Example notebooks are provided in [/docs/notebooks](./docs/notebooks).

## Signing each Commit

When you file a pull request, we ask that you sign off the
[Developer Certificate of Origin](https://developercertificate.org/) (DCO) in each commit.
Any Pull Request with commits that are not signed off will be rejected by the
[DCO check](https://probot.github.io/apps/dco/).

A DCO is a lightweight way to confirm that a contributor wrote or otherwise has the right
to submit code or documentation to a project. Simply add `Signed-off-by` as shown in the example below
to indicate that you agree with the DCO.

The git flag `-s` can be used to sign a commit:

```bash
git commit -s -m 'README.md: Fix minor spelling mistake'
```

The result is a signed commit message:

```
README.md: Fix minor spelling mistake

Signed-off-by: John Doe <john.doe@example.com>
```
