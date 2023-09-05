from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'Build stracture data'

with open("README.md", "r", encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

# Setting up
setup(
    name="tangelokit",
    version=VERSION,
    author="Arnold Blandon",
    author_email="arnold.blandon1@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "jsonschema==4.0.0",
    ],
    keywords=['python', 'tangelo', 'kit', 'data'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
