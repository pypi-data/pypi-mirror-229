from setuptools import setup, find_packages

VERSION = '0.0.5'
DESCRIPTION = 'Library created to generate structured data from tangelo'

# Setting up
setup(
    name="tangelokit",
    version=VERSION,
    author="Arnold Blandon",
    author_email="arnold.blandon1@gmail.com",
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
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
