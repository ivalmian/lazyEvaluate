import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lazyevaluate", 
    version="0.1.0",
    author="Ilya Valmianski",
    author_email="ivalmian@gmail.com",
    description="A micro library for lazy evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivalmian/lazyEvaluate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)