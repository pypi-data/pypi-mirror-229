import argparse
import sys
import subprocess
import requests
import pip
import os
import tarfile
import lzma
from pip._internal.operations.freeze import freeze

def get_installed_packages():
    # Get a list of installed packages
    return {package.split('==')[0]: package for package in freeze(local_only=True)}

def get_package_from_repo(package_name, auto_confirm=False, version=None, target=None):
    # Fetch and print package dependencies
    dependencies = get_dependencies_from_pypi(package_name, version)
    if dependencies:
        print(f"Package '{package_name}' has the following dependencies:")
        for dependency in dependencies:
            print(f"- {dependency}")

    if not auto_confirm:
        confirmation = input(f"Install package {package_name}? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Installation canceled.")
            return

    print(f"Installing packages: {package_name}")
    pip_args = [sys.executable, '-m', 'pip', 'install', '--upgrade', '--upgrade-strategy', 'only-if-needed']
    if version:
        pip_args.extend([f"{package_name}=={version}"])
    else:
        pip_args.extend([package_name])

    if target:
        pip_args.extend(['--target', target])

    subprocess.check_call(pip_args)

def update_system_packages():
    installed_packages = get_installed_packages()

    print("Updating all installed packages...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--upgrade-strategy', 'only-if-needed'] + list(installed_packages.keys()))

def get_dependencies_from_pypi(package_name, version=None):
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(pypi_url)
    if response.status_code == 200:
        data = response.json()
        if version:
            releases = data.get("releases", {})
            if version in releases:
                dependencies = releases[version][0].get("requires_dist", [])
            else:
                print(f"Version {version} not found for package '{package_name}'.")
                return []
        else:
            dependencies = data.get("info", {}).get("requires_dist", [])
        return dependencies
    return []

def bootstrap_local_package(package_path, auto_confirm=False):
    if not os.path.exists(package_path):
        print(f"Local package '{package_path}' not found.")
        return

    if not auto_confirm:
        confirmation = input(f"Install local package '{package_path}'? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Installation canceled.")
            return

    print(f"Installing local package: {package_path}")
    with lzma.open(package_path, 'rb') as compressed_file:
        with tarfile.open(fileobj=compressed_file, mode='r:xz') as tar:
            tar.extractall(path='.')
    package_name = os.path.basename(package_path).replace('.tar.xz', '')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])

def main():
    parser = argparse.ArgumentParser(
        prog='apkg',
        description='aurumOS Package Manager'
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    get_pypi_parser = subparsers.add_parser("get-pypi", help="Fetch and install packages from a repository")
    get_pypi_parser.add_argument("package_names", nargs='+', help="Names of the packages to install")
    get_pypi_parser.add_argument("-y", "--yes", action="store_true", help="Automatically accept installation")
    get_pypi_parser.add_argument("-v", "--version", help="Specify the version to install")
    get_pypi_parser.add_argument("-t", "--target", help="Specify the installation destination directory")

    update_parser = subparsers.add_parser("update", help="Update all installed packages")

    bootstrap_parser = subparsers.add_parser("bootstrap", help="Install a local package")
    bootstrap_parser.add_argument("package_path", help="Path to the local package")
    bootstrap_parser.add_argument("-y", "--yes", action="store_true", help="Automatically accept installation")

    args = parser.parse_args()

    if args.command == "get-pypi":
        for package_name in args.package_names:
            get_package_from_repo(package_name, auto_confirm=args.yes, version=args.version, target=args.target)
    elif args.command == "update":
        update_system_packages()
    elif args.command == "bootstrap":
        bootstrap_local_package(args.package_path, auto_confirm=args.yes)
    else:
        print("Invalid command. Use 'apkg --help' for usage information.")

if __name__ == "__main__":
    main()

