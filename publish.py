#!/usr/bin/env python3
"""
Build and publish script for compassheadinglib.
Replaces the upload functionality from setup.py.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f'\033[1m{description}\033[0m' if description else f'\033[1mRunning: {cmd}\033[0m')
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def get_version():
    """Get version from __version__.py file."""
    version_file = Path("compassheadinglib/__version__.py")
    if not version_file.exists():
        print("Error: __version__.py file not found")
        sys.exit(1)
    
    version_dict = {}
    with open(version_file) as f:
        exec(f.read(), version_dict)
    
    return version_dict.get('__version__', 'unknown')

def clean_build():
    """Clean previous builds."""
    dirs_to_clean = ['dist', 'build', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing {path}")
                path.unlink()

def run_tests():
    """Run tests with pytest."""
    run_command("python -m pytest", "Running tests...")
    print("\n\033[1mAll tests passed!\033[0m")

def build_package():
    """Build the package."""
    run_command("python -m build", "Building Source and Wheel distributions...")

def upload_to_testpypi():
    """Upload to TestPyPI."""
    run_command("python -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI...")
    print("\n\033[1mPackage uploaded to TestPyPI!\033[0m")
    print("Install with: pip install --index-url https://test.pypi.org/simple/ compassheadinglib")

def upload_to_pypi():
    """Upload to PyPI."""
    run_command("python -m twine upload dist/*", "Uploading to PyPI...")
    print("\n\033[1mPackage uploaded to PyPI!\033[0m")
    print("Install with: pip install compassheadinglib")

def tag_and_push():
    """Create git tag and push."""
    version = get_version()
    run_command(f"git tag v{version}", f"Creating git tag v{version}...")
    run_command("git push --tags", "Pushing git tags...")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python publish.py test-run       - Run tests only")
        print("  python publish.py build          - Clean and build package")
        print("  python publish.py test           - Run tests, build and upload to TestPyPI")
        print("  python publish.py publish        - Run tests, build and upload to PyPI")
        print("  python publish.py full           - Run tests, build, upload to PyPI, and tag")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Check if required tools are installed
    required_tools = ['build', 'twine']
    if command in ['test-run', 'test', 'publish', 'full']:
        required_tools.append('pytest')
        
    for tool in required_tools:
        try:
            subprocess.run([sys.executable, '-m', tool, '--help'], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            if tool == 'pytest':
                print(f"Error: {tool} is not installed. Install with: pip install pytest")
            else:
                print(f"Error: {tool} is not installed. Install with: pip install {tool}")
            sys.exit(1)

    if command == 'test-run':
        run_tests()
        
    elif command == 'build':
        clean_build()
        build_package()
        print("\n\033[1mBuild complete!\033[0m")
        
    elif command == 'test':
        run_tests()
        clean_build()
        build_package()
        upload_to_testpypi()
        
    elif command == 'publish':
        run_tests()
        clean_build()
        build_package()
        upload_to_pypi()
        
    elif command == 'full':
        run_tests()
        clean_build()
        build_package()
        upload_to_pypi()
        tag_and_push()
        print("\n\033[1mFull publish complete!\033[0m")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()