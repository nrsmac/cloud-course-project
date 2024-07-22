# s3-files-api
![badge](https://github.com/nrsmac/s3-files-api/actions/workflows/build-test-publish.yaml/badge.svg)

A project to demonstrate building high-quality APIs and SDKs with FastAPI.


Features:
- OpenAPI schema generation and diffing
- Automatic Python SDK generation


### System requirements

You will need the following installed on your machine to develop on this codebase

- `make` AKA `cmake`, e.g. `sudo apt-get update -y; sudo apt-get install cmake -y`
- Python 3.11, ideally using `pyenv` to easily change between Python versions
- `git`

### Development

```bash
# clone the repo

git clone https://github.com/nrsmac/s3_files_api.git

# Create a virtual env
python3.11 -m venv venv
source venv/bin/activate

# install the dev dependencies
make install

# Generate the SDK
make generate-client-library

# run the tests
make test
```
