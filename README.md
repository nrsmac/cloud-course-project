# s3-files-api
![badge](https://github.com/nrsmac/s3-files-api/actions/workflows/build-test-publish.yaml/badge.svg)

## Quick start

```bash
pip install s3-files-api
```

```python
from files_api import ...
```

## Developing/Contributing

### System requirements

You will need the following installed on your machine to develop on this codebase

- `make` AKA `cmake`, e.g. `sudo apt-get update -y; sudo apt-get install cmake -y`
- Python 3.7+, ideally using `pyenv` to easily change between Python versions
- `git`

###

```bash
# clone the repo
git clone https://github.com/<your github username>/s3-files-api.git

# install the dev dependencies
make install

# run the tests
make test
```
