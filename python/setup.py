#!/usr/bin/env python3
"""
Dynamic setup.py that reads version from centralized VERSION file.
This allows setuptools to read the version dynamically during build.
"""

from pathlib import Path
from setuptools import setup

def get_version():
    """Read version from centralized VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.1.0"  # fallback

if __name__ == "__main__":
    setup(
        version=get_version(),
    )