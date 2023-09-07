# Language Database (langdb)
Hackable database powering Large Language Models (LLMs)

## Build

Put pypi credentials in `~/.pypirc`. The relevant section should look like this
```
[distutils]
  index-servers =
    testpypi

[pypi]
  username = __token__
  password = pypi-...

[testpypi]
  username = __token__
  password = pypi-...
```

```
python -m build
```

Upload to test index:
```
twine upload --repository testpypi dist/*
```

Upload to prod index:
```
python -m build
twine upload dist/*
```
