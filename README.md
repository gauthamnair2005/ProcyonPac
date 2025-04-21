# 🌌 ProcyonPac

**ProcyonPac** is a lightweight, universal package manager designed to fetch and install packages and documentation from decentralized repositories like ProcyonHub. It's great for modular software projects, educational tools, and building flexible ecosystems.

---

## ✨ Features

- Package installation with dependency resolution
- Automatic documentation fetching
- Configurable repositories via a simple config file
- Clean uninstallation of packages and docs
- Minimalistic design, works cross-platform
- No third-party dependencies — pure Python

---

## 📁 Folder Structure

Installed packages along with their documentations go into the `apps` folder. Installed packages are tracked using a JSON file. A simple `.ini`-style config file handles repository settings.

---

## ⚙️ Installing

Just clone the repository, ensure you have Python 3.6 or higher, and run the `ppac.py` script from your terminal to install packages.

---

## 🚀 Usage

To install a package, run the install command with the package name. ProcyonPac will fetch all required packages and docs from the specified repo.

To uninstall, use the uninstall command. It removes the package folder and documentation, and updates the installed package list.

Use the help command for an overview of available operations.

---

## 🔧 Configuration

Configuration is handled via a `repo.config` file. Each repository section includes two URLs:

- `json_url` – where the `packages.json` is located
- `package_url` – base URL used to download package and documentation archives

This lets you fetch metadata and content from different locations if needed.

---

## 📦 Package Format

Each package is described in the repository’s `packages.json`. It includes the version, list of dependencies, and the name of the documentation archive. Packages and documentation are expected to be `.tar.gz` files hosted under predictable paths based on the package name.

---

## 📌 Requirements

- Python 3.6+
- No additional Python packages are required — it uses built-in libraries

---

## 🌟 Roadmap / Future Plans

- Semantic version support and conflict resolution
- Package search and browse capabilities
- Post-install scripts and package hooks
- Optional graphical interface
- Package verification and security features

---

## 💻 Contributing

Open to contributions! Whether it's feature suggestions, bug fixes, or documentation, feel free to fork and submit a PR.

---

## 📄 License

Licensed under the GNU GPL v3. Check the `LICENSE` file for details.

---

## 👨‍💻 Developed by Gautham Nair
