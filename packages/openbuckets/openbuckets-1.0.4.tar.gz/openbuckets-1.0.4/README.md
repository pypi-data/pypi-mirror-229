# openbuckets
The [OpenBuckets](https://openbuckets.io) web-based tool is a powerful utility that allows users to quickly locate open buckets in cloud storage systems through a simple query. In addition, it provides a convenient way to search for various file types across these open buckets, making it an essential tool for security professionals, researchers, and anyone interested in discovering exposed data.
This Postman collection aims to showcase the capabilities of [OpenBuckets](https://openbuckets.io) by providing a set of API requests that demonstrate how to leverage its features. By following this collection, you'll learn how to utilize [OpenBuckets](https://openbuckets.io) to identify open buckets and search for specific file types within them.

## Requirements.

Python 3.7+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install openbuckets
```
(you may need to run `pip` with root permission: `sudo pip install openbuckets`)

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import time
import openbuckets
from openbuckets.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.openbuckets.io
# See configuration.py for a list of all supported configuration parameters.
configuration = openbuckets.Configuration(
    host = "https://api.openbuckets.io"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (auth-scheme): bearerAuth
configuration = openbuckets.Configuration(
    access_token = os.environ["OPENBUCKETS_API_KEY"]
)


# Enter a context with an instance of the API client
with openbuckets.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openbuckets.BucketsApi(api_client)
    keywords = 'abg' # str | the search keywords to filter bucket names (e.g., \"abg\") (optional)
    type = 'aws' # str | the type of bucket to filter (e.g., aws,dos,azure,gcp) (optional)
    exact = 0 # float | whether to perform an exact match for the keywords (0 for false, 1 for true) (optional)
    start = 0 # float | starting index for pagination (optional)
    limit = 1000 # float | number of search results to return per page (optional)
    order = 'fileCount' # str | the sorting field for the search results (e.g., \"fileCount\" for sorting by file count) (optional)
    direction = 'asc' # str | the sorting direction for the search results (e.g., \"asc\" for ascending) (optional)

    try:
        # Search Buckets
        api_response = api_instance.search_buckets(keywords=keywords, type=type, exact=exact, start=start, limit=limit, order=order, direction=direction)
        print("The response of BucketsApi->search_buckets:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling BucketsApi->search_buckets: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://api.openbuckets.io*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*BucketsApi* | [**search_buckets**](docs/BucketsApi.md#search_buckets) | **GET** /api/v2/buckets | Search Buckets
*FilesApi* | [**search_files**](docs/FilesApi.md#search_files) | **GET** /api/v2/files | Search Files


## Documentation For Models

 - [Bucket](docs/Bucket.md)
 - [BucketSearchResults](docs/BucketSearchResults.md)
 - [BucketSearchResultsBucketsInner](docs/BucketSearchResultsBucketsInner.md)
 - [BucketSearchResultsMeta](docs/BucketSearchResultsMeta.md)
 - [BucketSearchResultsQuery](docs/BucketSearchResultsQuery.md)
 - [File](docs/File.md)
 - [FileSearchResults](docs/FileSearchResults.md)
 - [FileSearchResultsFilesInner](docs/FileSearchResultsFilesInner.md)
 - [FileSearchResultsMeta](docs/FileSearchResultsMeta.md)
 - [FileSearchResultsQuery](docs/FileSearchResultsQuery.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="bearerAuth"></a>
### bearerAuth

- **Type**: Bearer authentication (auth-scheme)

### Tests

Execute `pytest` to run the tests.


## Author

support@openbuckets.io


