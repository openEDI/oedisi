---
title: Contributing
description: How to contribute to OEDI-SI — code, components, and documentation.
---

# Contributing

Contributions are welcome across the OEDI-SI project. This page covers where to contribute,
how to set up a development environment, and the checks your change should pass.

## Where to contribute

| Repository | What lives there |
| --- | --- |
| [`oedisi`](https://github.com/openEDI/oedisi) | The framework, `oedisi.types` data models, and the `oedisi` CLI. |
| [`oedisi-components`](https://github.com/openEDI/oedisi-components) | Reusable HELICS components (feeders, estimators, recorders, …). |
| [`oedisi-frontend-app`](https://github.com/openEDI/oedisi-frontend-app) | The web UI and its FastAPI backend. |

## Development setup

Clone the repository you want to work on and install it with its development dependencies:

```bash
git clone https://github.com/openEDI/oedisi.git
cd oedisi
pip install -e ".[test]"      # framework + dev tools (pytest, ruff, black, mypy, …)
pre-commit install            # run formatters/linters on each commit
```

The frontend app uses `npm install` plus `uv --directory server sync`; see the
[install guide](install.md).

## Run the checks

Before opening a pull request, make sure the tests and quality gates pass:

```bash
pytest                 # unit + integration tests
ruff check .           # lint
black --check .        # formatting
mypy src               # type checking
```

The `oedisi` repository also has an end-to-end script at `tests/runtests.sh`.

## Contributing a component or algorithm

New simulation blocks are the most common contribution:

- Follow **[Build a component](intermediate/build-a-component.md)** for the required files,
  the `component_definition.json` contract, and the HELICS federate pattern.
- The algorithm interface (static/dynamic inputs, publications, endpoints) is described in
  [`ALGORITHM_DEVELOPERS.md`](https://github.com/openEDI/oedisi/blob/main/ALGORITHM_DEVELOPERS.md).
- Register it so it appears in the UI — see
  **[Register it in the UI](intermediate/register-in-ui.md)**.

## Contributing to the docs

These docs are a [MyST](https://mystmd.org) (Jupyter Book) project in `docs/`.

- Edit the Markdown and notebook files directly, then preview with `myst start`.
- The CLI, API, data-type, and component-catalog pages are **generated** — don't edit them
  by hand. After changing the CLI or the `oedisi` API, regenerate them:
  ```bash
  python docs/tools/generate.py
  ```
- Build the static site with `myst build --html` (see [Deployment](advanced/deployment.md)).

## Pull requests & issues

- Open pull requests against the `main` branch of the relevant repository.
- Keep changes focused, and include tests where it makes sense.
- Report bugs and request features on the issue tracker, e.g.
  <https://github.com/openEDI/oedisi/issues>.

## License

By contributing, you agree that your contributions are licensed under the project's
**BSD 3-Clause License** (see [Cite & license](cite.md)).
