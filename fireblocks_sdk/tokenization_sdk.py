from .sdk import FireblocksSDK
from .tokenization_api_types import \
    CreateTokenRequest, \
    ContractUploadRequest, \
    ContractDeployRequest, \
    ReadCallFunction, \
    WriteCallFunction

class FbTokenizationSDK:
    def __init__(self, sdk: FireblocksSDK):
        self.sdk = sdk
        self._tokenization_url = "/v1/tokenization/tokens"
        self._contract_registry_url = "/v1/contract-registry/contracts"
        self._contract_service_url = "/v1/contract-service/contract"

    def get_linked_tokens(self, limit: int = 100, offset: int = 0):
        request_filter = {"limit": limit, "offset": offset}
        return self.sdk._get_request(f"{self._tokenization_url}", query_params=request_filter)

    def issue_new_token(self, request: CreateTokenRequest):
        return self.sdk._post_request(self._tokenization_url, request.to_dict())

    def get_linked_token(self, assetId: str):
        return self.sdk._get_request(f"{self._tokenization_url}/{assetId}")

    def link_token(self, assetId: str):
        return self.sdk._put_request(f"{self._tokenization_url}/{assetId}/link", {})

    def unlink_token(self, assetId: str):
        return self.sdk._delete_request(f"{self._tokenization_url}/{assetId}")
    
    def get_contract_templates(self, limit: int = 100, offset: int = 0):
        request_filter = {
            "limit": limit,
            "offset": offset
        }
        return self.sdk._get_request(self._contract_registry_url, query_params=request_filter)

    def upload_contract_template(self, request: ContractUploadRequest):
        return self.sdk._post_request(self._contract_registry_url, request.to_dict())

    def get_contract_template(self, contractId: str):
        return self.sdk._get_request(f"{self._contract_registry_url}/{contractId}")

    def get_contract_template_constructor(self, contractId: str, with_docs: bool=False):
        return self.sdk._get_request(f"{self._contract_registry_url}/{contractId}/constructor?withDocs=${with_docs}")

    def delete_contract_template(self, contractId: str):
        return self.sdk._delete_request(f"{self._contract_registry_url}/{contractId}")

    def deploy_contract(self, contractId: str, request: ContractDeployRequest):
        return self.sdk._post_request(f"{self._contract_registry_url}/{contractId}/deploy", request.to_dict())
    
    def get_contracts_by_filter(self, templateId: str, blockchainId: str = None):
        return self.sdk._get_request(f"{self._contract_service_url}?templateId={templateId}&blockchainId={blockchainId}")
    
    def get_contract_by_address(self, blockchainId: str, contractAddress: str):
        return self.sdk._get_request(f"{self._contract_service_url}/{blockchainId}/{contractAddress}")
    
    def get_contract_abi(self, blockchainId: str, contractAddress: str):
        return self.sdk._get_request(f"{self._contract_service_url}/{blockchainId}/{contractAddress}/abi")
    
    def read_contract_call_function(self, blockchainId: str, contractAddress: str, request: ReadCallFunction):
        return self.sdk._post_request(f"{self._contract_service_url}/{blockchainId}/{contractAddress}/function/read", request.to_dict())

    def write_contract_call_function(self, blockchainId: str, contractAddress: str, request: WriteCallFunction):
        return self.sdk._post_request(f"{self._contract_service_url}/{blockchainId}/{contractAddress}/function/write", request.to_dict())