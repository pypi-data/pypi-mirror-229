# datafest-archive

<div align="center">

[![Build status](https://github.com/ckids-datafirst/archive/workflows/build/badge.svg?branch=master&event=push)](https://github.com/ckids-datafirst/archive/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/datafest-archive.svg)](https://pypi.org/project/datafest-archive/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ckids-datafirst/archive/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ckids-datafirst/archive/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ckids-datafirst/archive/releases)
[![License](https://img.shields.io/github/license/ckids-datafirst/archive)](https://github.com/ckids-datafirst/archive/blob/master/LICENSE)
![Coverage Report](assets/images/coverage.svg)

</div>

DataFestArchive is a Python package designed to generate the DataFestArchive website from past versions of DataFest

## Installation

```bash
pip install datafest-archive
```

## Usage

DataFestArchive is a Python package designed to generate the DataFestArchive website from past versions of DataFest

**Usage**:

```console
$ datafest-archive [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `project-call`: Reads the spreadsheet and imports the data...
- `website`: Create pages of projects and people...

## `datafest-archive main`

## `datafest-archive project-call`

Reads the spreadsheet and imports the data into the database (sqlite3).

**Usage**:

```console
$ datafest-archive project-call [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `import-data`

### `datafest-archive project-call import-data`

**Usage**:

```console
$ datafest-archive project-call import-data [OPTIONS] SPREADSHEET_PATH DATABASE_FILE
```

**Arguments**:

- `SPREADSHEET_PATH`: [required]
- `DATABASE_FILE`: [required]

**Options**:

- `--help`: Show this message and exit.

## `datafest-archive website`

Create pages of projects and people (students and advisors) from the database (sqlite3) using wowchemy-hugo-academic.

**Usage**:

```console
$ datafest-archive website [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `create`

### `datafest-archive website create`

**Usage**:

```console
$ datafest-archive website create [OPTIONS] PATH WEBSITE_OUTPUT_DIRECTORY
```

**Arguments**:

- `PATH`: [required]
- `WEBSITE_OUTPUT_DIRECTORY`: [required]

**Options**:

- `--help`: Show this message and exit.

`datafest-archive` is a command line tool that can be used to generate the DataFestArchive website from past versions of DataFest.

## Development documentation

Refer to [README-dev.md](README-dev.md) for development documentation.

## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/ckids-datafirst/archive/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

We use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.

### List of labels and corresponding titles

|               **Label**               |  **Title in Releases**  |
| :-----------------------------------: | :---------------------: |
|       `enhancement`, `feature`        |       🚀 Features       |
| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |
|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |
|              `breaking`               |   💥 Breaking Changes   |
|            `documentation`            |    📝 Documentation     |
|            `dependencies`             | ⬆️ Dependencies updates |

You can update it in [`release-drafter.yml`](https://github.com/ckids-datafirst/archive/blob/master/.github/release-drafter.yml).

GitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them.

## 🛡 License

[![License](https://img.shields.io/github/license/ckids-datafirst/archive)](https://github.com/ckids-datafirst/archive/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ckids-datafirst/archive/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{datafest-archive,
  author = {ckids-datafirst},
  title = {DataFestArchive is a Python package designed to generate the DataFestArchive website from past versions of DataFest},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ckids-datafirst/archive}}
}
```

## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
