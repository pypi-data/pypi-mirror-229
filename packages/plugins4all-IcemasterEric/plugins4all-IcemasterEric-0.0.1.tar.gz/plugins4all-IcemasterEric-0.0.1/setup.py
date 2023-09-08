import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plugins4all-IcemasterEric",
    version="0.0.1",
    author="Eric Li",
    author_email="icemastereric@gmail.com",
    description="Bringing chatgpt plugins to local llms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Icemaster-Eric/plugins4all",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)