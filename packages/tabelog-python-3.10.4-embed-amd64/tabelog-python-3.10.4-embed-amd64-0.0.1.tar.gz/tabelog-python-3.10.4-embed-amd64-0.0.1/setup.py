import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tabelog-python-3.10.4-embed-amd64", # Replace with your own username
    version="0.0.1",
    author="Tabelog",
    author_email="527506183@qq.com",
    description="The python 3.10.4 version std-modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tabelog-lg/tabelog",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10.4',
)