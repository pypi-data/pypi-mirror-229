# Function Cacher

[![Documentation Status](https://readthedocs.org/projects/function-cacher/badge/?version=latest)](https://function-cacher.readthedocs.io/en/latest/?badge=latest)

## Overview
This repository contains the source code of the Function Cacher project. Please refer to https://function-cacher.readthedocs.io/en/latest/index.html for documentation.

The Function Cacher project provides a parameter-based cacher which caches return values of cached functions to disk. 

## Installation

You may use `pip` to install this package:

`pip install functionCacher`

The package is located here: https://pypi.org/project/functionCacher/

## Basic Usage

```python
from functionCacher.Cacher import Cacher
cacher_instance = Cacher()

@cacher_instance.cache
def myfunc(arg1, arg2):
	return [arg1, arg2]

myfunc(1,2) # cache miss
myfunc(1,2) # cache hit
myfunc(2,3) # cache miss
