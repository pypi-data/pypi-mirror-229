import setuptools

from obsidian_traverse import __desc__, __version__


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="obsidian-traverse",
    version=__version__,
    py_modules=["obsidian_traverse"],
    author="Layerex",
    author_email="layerex@dismail.de",
    description=__desc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Layerex/obsidian-traverse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "obsidian-traverse = obsidian_traverse:main",
        ],
    },
)
