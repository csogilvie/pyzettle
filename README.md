# pyzettle
This repository provides functions for accessing and working with the zettle api.

## Respository structure
This repo has been set up as a package that can be pip installed using the code below. 

```python
pip install git+ssh://git@github.com/1st-Sedgley-Scout-Group/pyzettle
``` 
You can install a specific release version of the package by adding '@<git_release_tag>` on the end like below for v1.0,0

```python
# specifying the release you would like
pip install git+ssh://git@github.com/1st-Sedgley-Scout-Group/pyzettle@v1.0.0
``` 

You can check which release you have installed using `pip list` and checking the version of `pyzettle`.

Once installed you will have a packaged called `pyzettle` in your environment. You can then import the classes with the below code:
```python
import pyzettle as pz
```
