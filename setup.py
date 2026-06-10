#!/usr/bin/env python3
"""Script de configuration"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="egc-suite",
    version="1.0.0",
    author="ManBoyx",
    author_email="manboyxv4@gmail.com",
    description="EGC Suite - Applications optimisées pour Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ManBoyx/E.G.C",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=[
        'PyQt5>=5.15,<5.16',
        'PyQtWebEngine>=5.15,<5.16',
        'Pillow>=10.0',
        'numpy>=1.26',
        'sounddevice>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'egc-antivirus=src.antivirus.scanner:main',
            'egc-photo-editor=src.photo.editor:main',
            'egc-browser=src.browser.navigator:main',
            'egc-audio-amplifier=src.audio.amplifier:main',

        ],
    },
)
