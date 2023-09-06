import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()
''
setuptools.setup(
    name = "arauco",
    version = "1.2",
    author = "Pedro Toledo",
    author_email = "ptoledor@msn.com",
    description = "Simple and useful functions for data analysis",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ptoledor/pypi-arauco",
    license="MIT",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = setuptools.find_packages(),
    install_requires=['pandas', 'numpy'], 
    python_requires = ">=3.6",
)
