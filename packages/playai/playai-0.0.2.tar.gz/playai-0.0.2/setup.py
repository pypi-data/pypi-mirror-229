from setuptools import setup, find_packages
from pathlib import Path


VERSION = '0.0.2' 
DESCRIPTION = 'My first Python package'
LONG_DESCRIPTION = (Path(__file__).parent / "README.md").read_text()

# Setting up
setup(
        name="playai", 
        version=VERSION,
        author="Valentin Lopez",
        author_email="<valentinlopezandres@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)