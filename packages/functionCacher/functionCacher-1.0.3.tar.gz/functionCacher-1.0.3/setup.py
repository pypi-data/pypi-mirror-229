import setuptools

setuptools.setup(
    name="functionCacher",
    version="1.0.3",
    author="Philipp Friese",
    author_email="philipp@friese.one",
    description="Cache function results to disk",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/philipp.friese/function-cacher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10"
    ],
    install_requires=[
        "autopep8",
        "pandas",
        "pyzstd",
        "numpy",
        "Deprecated",
    ]
)