<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br>s5commander
</h1>
<h3>◦ S5commander: Unleash the Power of <a href="https://github.com/peak/s5cmd" target="_blank">s5cmd</a> directly in Python</h3>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style&logo=Python&logoColor=white" alt="Python" />
</p>
<img src="https://img.shields.io/github/languages/top/clementpoiret/s5commander?style&color=5D6D7E" alt="GitHub top language" />
<img src="https://img.shields.io/github/languages/code-size/clementpoiret/s5commander?style&color=5D6D7E" alt="GitHub code size in bytes" />
<img src="https://img.shields.io/github/commit-activity/m/clementpoiret/s5commander?style&color=5D6D7E" alt="GitHub commit activity" />
<img src="https://img.shields.io/github/license/clementpoiret/s5commander?style&color=5D6D7E" alt="GitHub license" />
</div>

---

## 📒 Table of Contents
- [📒 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [⚙️ Features](#-features)
- [📂 Project Structure](#project-structure)
- [🧩 Modules](#modules)
- [🚀 Getting Started](#-getting-started)
- [🗺 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

---


## 📍 Overview

The s5commander project is a Python library that allows users to interact with S3 buckets using the awesome s5cmd command-line tool.
To quote its description, [`s5cmd`](https://github.com/peak/s5cmd) is a very fast S3 and local filesystem execution tool.
It comes with support for a multitude of operations including tab completion and wildcard support for files, which can be very handy for your object storage workflow while working with large number of files.

> In short, s5cmd offers a very fast speed. For uploads, s5cmd is 32x faster than s3cmd and 12x faster than aws-cli. For downloads, s5cmd can saturate a 40Gbps link (~4.3 GB/s), whereas s3cmd and aws-cli can only reach 85 MB/s and 375 MB/s respectively.

The goal of this library is to offer a wrapper around this software.
It offers functionality for performing various operations like listing, copying, and removing files, creating and removing buckets, checking disk usage, reading files, and utilizing data pipes.

This project simplifies management and manipulation of S3 data using `s5cmd` inside a Python project, making it easier for users to work with S3 buckets and improve their productivity.

---

## ⚙️ Features

| Feature                | Description                           |
| ---------------------- | ------------------------------------- |
| **⚙️ Architecture**     | The codebase follows a modular and object-oriented design. It provides a wrapper for the s5cmd command-line tool and uses classes and functions to handle different actions related to S3 bucket management and file operations. |
| **📖 Documentation**   | The documentation will come later... |
| **🔗 Dependencies**    | The codebase depends on the s5cmd command-line tool, which is an external dependency for interacting with the AWS S3 service. It relies on necessary AWS credentials and configuration provided by the user. |
| **🧩 Modularity**      | The codebase is organized into separate modules: `commander.py` contains classes and functions related to S3 bucket operations and file management. It allows components to be reused or extended for different S3 operations. |
| **✔️ Testing**          | Tests will also come later :) |
| **⚡️ Performance**     | The performance of the codebase is directly dependent on the underlying s5cmd tool and AWS S3 service. As the codebase primarily acts as a wrapper, its own performance impact is limited. |
| **🔐 Security**        | The codebase relies on AWS credentials for accessing and interacting with S3 buckets, ensuring proper authentication and authorization. Proper handling and protection of these credentials is crucial for maintaining security.|
| **🔀 Version Control** | The codebase is hosted on GitHub and follows a standard Git version control workflow. Commits are tracked, and the repository can be cloned, branched, and versions can be audited using Git tools and techniques. |
| **🔌 Integrations**    | The codebase is designed to interact with cloud providers using an S3 protocol, including other providers than AWS services. |

---


## 📂 Project Structure




---

## 🧩 Modules

<details closed><summary>S5commander</summary>

| File                                                                                            | Summary                                                                                                                                                                                                                                                                                                        |
| ---                                                                                             | ---                                                                                                                                                                                                                                                                                                            |
| [commander.py](https://github.com/clementpoiret/s5commander/blob/main/s5commander/commander.py) | The code provides a wrapper for the s5cmd command-line tool, allowing users to interact with an S3 bucket. It supports functionalities like listing files, copying files, removing files, moving files, creating/removing buckets, selecting buckets, checking disk usage, reading files, and using data pipe. |

</details>

---

## 🚀 Getting Started

### ✔️ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
> - `s5cmd`

### 📦 Installation

1. Clone the s5commander repository:
```sh
git clone https://github.com/clementpoiret/s5commander
```

2. Change to the project directory:
```sh
cd s5commander
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🎮 Using s5commander

```python
```

### 🧪 Running Tests
```sh
pytest
```

---


## 🗺 Roadmap

> - [X] `list buckets and objects`
> - [ ] `copy objects`
> - [ ] `remove objects`
> - [ ] `move/rename objects`
> - [ ] `make bucket`
> - [ ] `remove bucket`
> - [ ] `run SQL queries on objects`
> - [ ] `show object size usage`
> - [ ] `print remote object content`
> - [ ] `stream to remote from stdin`
> - [ ] `run commands in batch`
> - [ ] `sync objects`

---

## 🤝 Contributing

Contributions are always welcome! Please follow these steps:
1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.
2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.
3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).
```sh
git checkout -b new-feature-branch
```
4. Make changes to the project's codebase.
5. Commit your changes to your local branch with a clear commit message that explains the changes you've made.
```sh
git commit -m 'Implemented new feature.'
```
6. Push your changes to your forked repository on GitHub using the following command
```sh
git push origin new-feature-branch
```
7. Create a new pull request to the original project repository. In the pull request, describe the changes you've made and why they're necessary.
The project maintainers will review your changes and provide feedback or merge them into the main branch.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for additional info.

---
