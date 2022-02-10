import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
print(f"\nHERE = {HERE.absolute()}\n")
README = (HERE / "README.md").read_text()
REQUIRES = (HERE / "requirements.txt").read_text().strip().split("\n")
REQUIRES = [lin.strip() for lin in REQUIRES]
VERSION = (HERE / "VERSION").read_text().strip()
# See https://packaging.python.org/en/latest/guides/single-sourcing-package-version/

setuptools.setup(
    name="dynprog",
    packages=setuptools.find_packages(),
    version=VERSION,
    install_requires=REQUIRES,
    author="Erel Segal-Halevi",
    author_email="erelsgl@gmail.com",
    description="Generic function for sequential dynamic programming",
    keywords="optimization, dynamic-programming",
    license="GPL",
    license_files=("LICENSE",),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/erelsgl/dynprog",
    project_urls={
        "Bug Reports": "https://github.com/erelsgl/dynprog/issues",
        "Source Code": "https://github.com/erelsgl/dynprog",
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        # see https://pypi.org/classifiers/
        "Development Status :: 2 - Pre-Alpha",
    ],
)

# Build:
#   Delete old folders: build, dist, *.egg_info
#   Then run:
#        python -m build
#   Or (old version):
#        python setup.py sdist bdist_wheel


# Publish to test PyPI:
#   twine upload --repository testpypi dist/*

# Publish to real PyPI:
#   twine upload --repository pypi dist/*
