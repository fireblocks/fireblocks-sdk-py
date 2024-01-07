from abc import ABC
from enum import Enum
from typing import Optional, List, Union, Dict

from .api_types import convert_class_to_dict


class BaseDictClass(ABC):
    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class Parameter(BaseDictClass):
    def __init__(
            self,
            name: str,
            type: str,
            internal_type: str,
            description: Optional[str] = None,
            components: Optional[List['Parameter']] = None
    ):
        self.name = name
        self.type = type
        self.internal_type = internal_type
        self.description = description
        self.components = components


class ParameterWithValue(Parameter):
    def __init__(
            self,
            name: str,
            type: str,
            internal_type: str,
            value: Union[str, int, float, bool],
            function_value: 'LeanAbiFunction',
            description: Optional[str] = None,
            components: Optional[List['Parameter']] = None
    ):
        super().__init__(name, type, internal_type, description, components)
        self.function_value = function_value
        self.value = value


class LeanAbiFunction(BaseDictClass):
    def __init__(self, inputs: List[ParameterWithValue], name: Optional[str] = ""):
        self.inputs = inputs
        self.name = name


class EVMTokenCreateParams(BaseDictClass):
    def __init__(self, contract_id: str, constructor_params: Optional[List[ParameterWithValue]] = None):
        self.contract_id = contract_id
        self.constructor_params = constructor_params


class StellarRippleCreateParams(BaseDictClass):
    def __init__(self, issuer_address: Optional[str] = None):
        self.issuer_address = issuer_address


class CreateTokenRequest(BaseDictClass):
    def __init__(
            self,
            symbol: str,
            name: str,
            blockchain_id: str,
            vault_account_id: str,
            create_params: Union[EVMTokenCreateParams, StellarRippleCreateParams]
    ):
        self.symbol = symbol
        self.name = name
        self.blockchain_id = blockchain_id
        self.vault_account_id = vault_account_id
        self.create_params = create_params


class ContractDeployRequest(BaseDictClass):
    def __init__(
            self,
            asset_id: str,
            vault_account_id: str,
            constructor_parameters: Optional[List[ParameterWithValue]] = None
    ):
        self.asset_id = asset_id
        self.vault_account_id = vault_account_id
        self.constructor_parameters = constructor_parameters


class AbiFunction(BaseDictClass):
    def __init__(
            self,
            name: str,
            type: str,
            state_mutability: str,
            inputs: List[Parameter],
            outputs: Optional[List[Parameter]] = None,
            description: Optional[str] = None,
            returns: Optional[Dict[str, str]] = None
    ):
        self.name = name
        self.type = type
        self.state_mutability = state_mutability
        self.inputs = inputs
        self.outputs = outputs
        self.description = description
        self.returns = returns


class ContractInitializationPhase(str, Enum):
    ON_DEPLOYMENT = "ON_DEPLOYMENT"
    POST_DEPLOYMENT = "POST_DEPLOYMENT"


class ContractTemplateType(str, Enum):
    FUNGIBLE_TOKEN = "FUNGIBLE_TOKEN"
    NON_FUNGIBLE_TOKEN = "NON_FUNGIBLE_TOKEN"
    NON_TOKEN = "NON_TOKEN"
    UUPS_PROXY = "UUPS_PROXY"


class InputFieldMetadataTypes(str, Enum):
    EncodedFunctionCallFieldType = "encodedFunctionCall",
    DeployedContractAddressFieldType = "deployedContractAddress",
    SupportedAssetAddressFieldType = "supportedAssetAddress",


class EncodedFunctionCallFieldMetadata:
    def __init__(self, template_id: str, function_signature: str):
        self.template_id = template_id
        self.function_signature = function_signature


class DeployedContractAddressFieldMetadata:
    def __init__(self, template_id: str):
        self.template_id = template_id


class FieldMetadata(BaseDictClass):
    def __init__(self, type: InputFieldMetadataTypes,
                 info: Union[EncodedFunctionCallFieldMetadata, DeployedContractAddressFieldMetadata]):
        self.type = type
        self.info = info


class ContractUploadRequest(BaseDictClass):
    def __init__(
            self,
            name: str,
            description: str,
            long_description: str,
            bytecode: str,
            sourcecode: str,
            initialization_phase: ContractInitializationPhase,
            abi: Optional[List[AbiFunction]] = None,
            compiler_output_metadata: Optional[object] = None,
            docs: Optional[object] = None,
            attributes: Optional[Dict[str, str]] = None,
            type: Optional[ContractTemplateType] = None,
            input_fields_metadata: Optional[Dict[str, FieldMetadata]] = None,
    ):
        self.name = name
        self.description = description
        self.long_description = long_description
        self.bytecode = bytecode
        self.sourcecode = sourcecode
        self.initialization_phase = initialization_phase
        self.abi = abi
        self.compiler_output_metadata = compiler_output_metadata
        self.docs = docs
        self.attributes = attributes
        self.type = type
        self.input_fields_metadata = input_fields_metadata


class ReadCallFunction(BaseDictClass):
    def __init__(self, abi_function: AbiFunction):
        self.abiFunction = abi_function


class WriteCallFunction(BaseDictClass):
    def __init__(
            self,
            vault_account_id: str,
            abi_function: AbiFunction,
            amount: Optional[str] = None,
            fee_level: Optional[str] = None,
            note: Optional[str] = None,
    ):
        self.vault_account_id = vault_account_id
        self.abi_function = abi_function
        self.amount = amount
        self.fee_level = fee_level
        self.note = note
