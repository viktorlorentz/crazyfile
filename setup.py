from setuptools import setup, find_packages

setup(
    name="crazyfile",
    version="0.1.0",
    description="Crazy-compress large lists in YAML using numpy and gzip",
    author="Viktor Lorentz",
    packages=find_packages(),
    install_requires=[
        "ruamel.yaml>=0.17.21",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "crazyfile=crazyfile.crazyfile:main",
        ],
    },
)
