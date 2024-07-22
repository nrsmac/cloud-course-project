"""
Script that uses the auto-generated API SDK to hit our API.

To generate the SDK, see the run.sh script.

To use the SDK, install in a separate virtual environment as the FastAPI app
(sometimes SDKs are written in entirely different languages after all--total
isolation makes sense). Then see the run.sh script for installing it.
"""

from pprint import pprint

import files_api_sdk
from files_api_sdk.rest import ApiException

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = files_api_sdk.Configuration(host="http://localhost:8000")


def main():
    """Test the FastAPI app."""
    # Enter a context with an instance of the API client
    with files_api_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = files_api_sdk.FilesApi(api_client)
        file_path = "file_path_example"  # str |
        file_content = "./pyproject.toml"  # bytearray |

        try:
            # Upload File
            api_response = api_instance.files_upload_file(
                file_path=file_path,
                file_content=file_content,
            )
            print("The response of FilesApi->files_upload_file:\n")
            pprint(api_response)
        except ApiException as err:
            print("Exception when calling FilesApi->files_upload_file: %s\n" % err)


if __name__ == "__main__":
    main()
