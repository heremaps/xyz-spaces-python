Documentation for the release process of xyzspaces.

## To release on PyPI

- Increment `__version__` in [file](xyzspaces/__version__.py).
- Create a CHANGELOG by running `make build_changelog` This will read the proclamation changes from the `changes` directory and will automatically update `CHANGELOG.md`. Verify the changes and manually update the `CHANGELOG.md` if required and then commit the changes.
- Create a new release by clicking on this [link](https://github.com/heremaps/xyz-spaces-python/releases/new).
  update tag version and release description and click on `Publish release` this will release package on PyPI.
  
  
## To release on Anaconda's conda-forge channel

- Go to [xyzspaces-feedstock](https://github.com/conda-forge/xyzspaces-feedstock)
- Create a new release branch and update `version`, `url`, `sha256` hash of released tar and dependencies in [meta.yml](https://github.com/conda-forge/xyzspaces-feedstock/blob/master/recipe/meta.yaml)
  raise the PR for this and merge the changes in master.
- It takes some time for a new release to appear on the conda-forge channel post changes are merged in to master branch.  
