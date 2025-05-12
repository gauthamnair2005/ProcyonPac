import requests
import tarfile
import os
import sys
import json
from pathlib import Path
from io import BytesIO
import configparser

# Constants
BASE_DIR = Path(__file__).parent.resolve()
REPO_CONFIG_PATH = BASE_DIR / "repo.config"
INSTALLED_PACKAGES_FILE = BASE_DIR / "installed_packages.json"
INSTALL_DIR = BASE_DIR / "apps"  # Changed to 'apps' directory in current path
PACKAGES_JSON_FILE = "packages.json"

class ProcyonPac:
    def __init__(self):
        self.repos = self.load_repositories()
        self.packages = self.load_packages()
        self.installed_packages = self.load_installed_packages()

    def load_repositories(self):
        repos = {}
        if REPO_CONFIG_PATH.exists():
            config = configparser.ConfigParser()
            config.read(REPO_CONFIG_PATH)
            for section in config.sections():
                json_url = config.get(section, "json_url", fallback=None)
                package_url = config.get(section, "package_url", fallback=None)
                repo_name = config.get(section, "repo_name", fallback=None)
                if json_url and package_url:
                    repos[section] = {"json_url": json_url, "package_url": package_url}
        else:
            print("List of repositories not found.\nPlease fix this by obtaining repo.config from ProcyonPac GitHub repository (https://github.com/gauthamnair2005/ProcyonPac)")
        return repos

    def load_packages(self):
        all_packages = {}
        for repo_name, repo_info in self.repos.items():
            json_url = repo_info["json_url"]
            print(f"Loading repository... [{repo_name}]")
            try:
                response = requests.get(json_url)
                if response.status_code == 200:
                    repo_packages = response.json()
                    print(f" ↳ Successfully loaded repository [{repo_name}]")
                    all_packages.update(repo_packages)
                else:
                    print(f" ↳ Failed to load repository [{repo_name}]\n  ↳ Status: {response.status_code}")
            except Exception as e:
                print(f" ↳ Error loading list of packages available from the repository.\n  ↳ These could be the reason(s):")
                print(f"     1. Network Issue")
                print(f"     2. Repo server is down")
                print(f"     3. Incorrect repo configuration in repo.config")
        return all_packages

    def load_installed_packages(self):
        if INSTALLED_PACKAGES_FILE.exists():
            with open(INSTALLED_PACKAGES_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_installed_packages(self):
        with open(INSTALLED_PACKAGES_FILE, 'w') as f:
            json.dump(self.installed_packages, f, indent=4)

    def get_package_version(self, pkg_name):
        return self.packages.get(pkg_name, {}).get("version", None)

    def get_package_dependencies(self, pkg_name):
        deps = self.packages.get(pkg_name, {}).get("dependencies", [])
        return deps if isinstance(deps, list) else [deps]

    def download_and_extract_package(self, pkg_name, repo_url):
        archive_url = f"{repo_url}/app/{pkg_name}.tar.gz"
        print(f"Downloading {pkg_name}...")
        try:
            response = requests.get(archive_url, stream=True)
            if response.status_code == 200:
                install_path = INSTALL_DIR / pkg_name
                install_path.mkdir(parents=True, exist_ok=True)
                with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
                    tar.extractall(path=install_path, filter='data')
                print(f"Installed {pkg_name} to {install_path}")
            else:
                print(f" ↳ Failed to download package: {pkg_name}.tar.gz")
        except Exception as e:
            print(f" ↳ Error downloading {pkg_name}: {e}")

    def download_docs(self, pkg_name, repo_url):
        docs_url = f"{repo_url}/app-docs/{pkg_name}.tar.gz"
        print(f"Downloading {pkg_name} documentation...")
        try:
            response = requests.get(docs_url, stream=True)
            if response.status_code == 200:
                docs_path = INSTALL_DIR / f"{pkg_name}-docs"
                docs_path.mkdir(parents=True, exist_ok=True)
                with tarfile.open(fileobj=BytesIO(response.content), mode="r:gz") as tar:
                    tar.extractall(path=docs_path, filter='data')
                print(f"Downloaded documentation for {pkg_name} to {docs_path}")
            else:
                print(f" ↳ Failed to download documentation for {pkg_name}")
        except Exception as e:
            print(f" ↳ Error downloading docs for {pkg_name}: {e}")

    def install(self, pkg_name):
        if pkg_name not in self.packages:
            print(f"Package {pkg_name} not found in repository.")
            return
        
        confirm = input(f"{pkg_name} found! Do you want to install it? (y/n) ")
        if confirm.lower() == 'n':
            print(f"Installation aborted!")
            return
        

        version = self.get_package_version(pkg_name)
        dependencies = self.get_package_dependencies(pkg_name)

        # Resolve dependencies recursively
        for dep in dependencies:
            if dep not in self.packages:
                print(f" ↳ Dependency {dep} for {pkg_name} is missing in repository.")
                return
            print(f"Installing dependency: {dep} v{self.get_package_version(dep)}")
            self.install(dep)

        # Skip if already installed
        if pkg_name in self.installed_packages:
            installed_version = self.installed_packages[pkg_name]
            if installed_version == version:
                print(f"{pkg_name} is already installed (v{version})")
                return
            else:
                print(f"Updating {pkg_name} from v{installed_version} to v{version}")

        available_repos = []
        for repo_name, repo_info in self.repos.items():
            if pkg_name in self.packages:
                available_repos.append((repo_name, repo_info["package_url"]))

        if len(available_repos) == 1:
            selected_repo = available_repos[0]
            print(f"Installing {pkg_name} from {selected_repo[0]}...")
            self.download_and_extract_package(pkg_name, selected_repo[1])
            self.download_docs(pkg_name, selected_repo[1])
            self.installed_packages[pkg_name] = version
            self.save_installed_packages()

        elif len(available_repos) > 1:
            print(f"Package {pkg_name} is available in multiple repositories:")
            for i, (repo_name, _) in enumerate(available_repos, 1):
                print(f"{i}. {repo_name}")
            print(f"{len(available_repos) + 1}. Cancel installation")
            choice = int(input("Enter your choice: ")) - 1
            if 0 <= choice < len(available_repos):
                selected_repo = available_repos[choice]
                print(f"Installing {pkg_name} from {selected_repo[0]}...")
                self.download_and_extract_package(pkg_name, selected_repo[1])
                self.download_docs(pkg_name, selected_repo[1])
                self.installed_packages[pkg_name] = version
                self.save_installed_packages()
            else:
                print("Installation aborted.")
        else:
            print("No repository contains this package.")

    def uninstall(self, pkg_name):
        if pkg_name not in self.installed_packages:
            print(f"{pkg_name} is not installed.")
            return
        install_path = INSTALL_DIR / pkg_name
        if install_path.exists():
            for item in install_path.iterdir():
                item.unlink()
            install_path.rmdir()
        docs_path = INSTALL_DIR / f"{pkg_name}-docs"
        if docs_path.exists():
            for item in docs_path.iterdir():
                item.unlink()
            docs_path.rmdir()
        del self.installed_packages[pkg_name]
        self.save_installed_packages()
        print(f"Uninstalled {pkg_name}")

    def update_all(self):
        for pkg in list(self.installed_packages):
            self.install(pkg)

if __name__ == "__main__":
    pac = ProcyonPac()

    if len(sys.argv) < 2:
        print("Usage: ppac.py <install|uninstall|update> [package_name]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install" and len(sys.argv) == 3:
        pac.install(sys.argv[2])
    elif command == "uninstall" and len(sys.argv) == 3:
        pac.uninstall(sys.argv[2])
    elif command == "update":
        pac.update_all()
    else:
        print("Invalid command or arguments.")
