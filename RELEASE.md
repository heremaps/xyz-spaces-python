# Release process

This document describes the release process of xyzspaces, and is mostly intended for package maintainers.


## Preparation

The following are mandatory pre-release steps to bring the repository into a proper shape:

- Increment `__version__` variable in [xyzspaces/__version__.py](xyzspaces/__version__.py) as desired.
- Make sure all tests listed in `CONTRIBUTING.md` pass successfully.
- Make sure badges appear as expected in the [README.md on GitHub](https://github.com/heremaps/xyz-spaces-python/blob/master/README.md).
- Run `make build_changelog` to collect changes and prepend them to `CHANGELOG.md`, then edit this file manually if needed and commit these changes.


## Release on PyPI

- Create a new release in the GitHub UI by clicking on [Draft a new release](https://github.com/heremaps/xyz-spaces-python/releases/new) button, then update the tag version and release description.
- Click on the `Publish release` button to release the [package on PyPI](https://pypi.org/project/xyzspaces).
- Once released verify that `pip install xyzspaces` does indeed install the latest release.

  
## Release on Anaconda's conda-forge channel

- Go to the [xyzspaces-feedstock](https://github.com/conda-forge/xyzspaces-feedstock) repository.
- Create a new release branch and update `version`, `url`, `sha256` hash of the released tar and dependencies in [meta.yml](https://github.com/conda-forge/xyzspaces-feedstock/blob/master/recipe/meta.yaml)
- Raise a PR for this release branch and merge the changes in master.
- It can take hours for a new release to [appear on Anaconda.org)[https://anaconda.org/conda-forge/xyzspaces].
- Once available verify that `conda install -c conda-forge xyzspaces` does indeed install the latest release.
