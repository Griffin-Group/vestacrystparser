# Contributing guidelines

As an in-progress project, **vestacrystparser** welcomes contributions.
In particular, because VESTA's UI is extensive, we always need new methods in
`vestacrystparser.parser.VestaFile` to fill out the API.
Additionally, any new discoveries on VESTA's file format should be added to
`docs/source/file_format.md`.
Extensions to `vestacrystparser.convert` to allow reading other file formats
are also wanted.

If you spot an issue or have a feature request, open a report using
[GitHub Issues](https://github.com/Griffin-Group/vestacrystparser/issues).

Contributions are managed through
[GitHub](https://github.com/Griffin-Group/vestacrystparser).
To make a contribution, create your own branch or fork of the repository, make
your changes, then make a
[pull request](https://github.com/Griffin-Group/vestacrystparser/pulls).
There, a code maintainer shall review your request and, if appropriate, merge
it into the repository.
(No guarantees are given for the timeliness of code reviews or maintenance,
as this is a project managed in spare time.)

By contributing code to this repository, you agree to license all contributions
under the license attached to this repository.

If developing code, you will likely want the `[dev]` optional dependencies.

Any new functions, methods, and classes need to contain docstrings.
Docstrings should follow the
[Google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
style guidelines.
Docstrings may include reStructuredText and
[Sphinx](https://www.sphinx-doc.org/en/master/index.html) directives.

Code should follow [PEP8](https://peps.python.org/pep-0008/) guidelines.
`autopep8` (with default arguments) can be used to ensure consistency.

All new functions must include tests, ideally with full (or at least high) code
coverage.
Tests are included under `tests/` and use the `pytest` framework.
Additionally, the test suite must pass before any pull requests will be
accepted.

(N.B. To test `vestacrystparser.export`, which requires VESTA to be installed,
call `pytest --vesta`. This module is independent of the other modules, so 
further testing should not be required if it is not modified.
However, it is also environment dependent, so maybe you'll find a new bug.)
