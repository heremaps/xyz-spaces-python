# 2. Use modern project tooling

Date: 2020-09-26

## Status

Accepted

## Context

This project started when Python 3.8 was the latest version. Therefore we want to make use of an existing, modern software-engineering toolset that helps both, developers produce a feature-rich, high-quality package more quickly, as well as users get more value out of this package for their individual use cases.

## Decision(s)

- This project supports Python 3.x only, starting with 3.6 now but perhaps 3.7 in the near future.
- The code base makes use of type annotations wherever useful and possible without making the code too complicated.
- It follows a test driven development style, and aims at a high test coverage of a minimum 90% of all lines.
- It makes use of external services for checking code quality.
- It uses established services for hosting the project's code base, documentation and releases.
- It uses an established service to execute/test the code online.
- It documents all source code (except for the testsuite) with docstrings for moduls, classes and methods/functions.
- It declares the signatures of all callables with all params inside the docstrings.
- It adopts a coding style as defined by PEP8 and/or Black.
- It makes it easy to build a changelog automatically.
- It contains enough examples for new users to obtain a quick understanding of the features of this package.
- It contains a prosaic documentation explaining additional context and possible use-cases for this package.
- It tests changes to the code inside a CI/CD environment before they are accepted.

## Consequences

Positive effects to be expected:

- The code base can make use of modern Python features.
- It allowes to find errors earlier because of a mix of tests (dynamic at runtime and static due to type-checking).
- It is possible to automatically generate an API reference for the code including type information.
- It follows established coding conventions as they matured within the Python community.
- Maintaining the code becomes easier for existing developers.
- Contributing to the code becomes easier for new developers.

Negative effects that might need attention at some point:

- A testsuite trying to cover most of the code might slow down CI/CD, especially when run for multiple Python versions.
- Care is needed for tests running concurently (for different Python versions, say) to not interfere with each other, e.g. because the operate on the same XYZ space.
