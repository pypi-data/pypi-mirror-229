from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "Operating System :: MacOS",
    "Operating System :: Microsoft",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
]

setup(
    name="loadsure_api_classes",
    version="0.1",
    description="Api classes to make a data integration",
    long_description=open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    url="",
    author="Juan Valencia",
    author_email="juan.valencia@loadsure.net",
    license="MIT",
    classifiers=classifiers,
    keywords="",
    packages=find_packages(),
)
