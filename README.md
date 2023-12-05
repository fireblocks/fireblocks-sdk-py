# The Official Python SDK for Fireblocks API
[![PyPI version](https://badge.fury.io/py/fireblocks-sdk.svg)](https://badge.fury.io/py/fireblocks-sdk)

## About
This repository contains the official Python SDK for Fireblocks API.
For the complete API reference, go to the [API reference](https://developers.fireblocks.com/).

## Usage
### Before You Begin
Make sure you have the credentials for Fireblocks API Services. Otherwise, please contact Fireblocks support for further instructions on how to obtain your API credentials.

### Requirements
Python 3.6 or newer.

### Installation
`pip3 install fireblocks-sdk`

#### Importing Fireblocks SDK
```python
from fireblocks_sdk import FireblocksSDK

fireblocks = FireblocksSDK(private_key, api_key)
```

You can also pass additional arguments:
```python
fireblocks = FireblocksSDK(private_key, api_key, api_base_url="https://api.fireblocks.io", timeout=2.0, anonymous_platform=True)
```

#### Using Fireblocks Tokenization endpoints
```python
from fireblocks_sdk import FireblocksSDK, FireblocksTokenization, \
                           ContractUploadRequest

fireblocks = FireblocksSDK(private_key, api_key)

# Get linked tokens
tokens=fireblocks.get_linked_tokens()

# Upload a private contract
contractTemplateRequest=ContractUploadRequest(
    name='New Contract Template',
    description='description',
    longDescription='long description',
    bytecode='0x12345',
    sourcecode= 'sourcecode',
    initializationPhase='ON_DEPLOYMENT',
    abi=[]
)
template=fireblocks.upload_contract_template(contractTemplateRequest)
print(template['id'])
```
