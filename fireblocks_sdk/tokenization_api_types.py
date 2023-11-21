from .api_types import convert_class_to_dict

from enum import Enum
from typing import Optional, List, Union, Dict

class Parameter:
    def __init__(
        self,
        name: str,
        type: str,
        internalType: str,
        description: Optional[str] = None,
        components: Optional[List['Parameter']] = None
    ):
        self.name = name
        self.type = type
        self.internalType = internalType
        self.description = description
        self.components = components

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class ParameterWithValue(Parameter):
    def __init__(
        self,
        name: str,
        type: str,
        internalType: str,
        value: Union[str, int, float, bool],
        description: Optional[str] = None,
        components: Optional[List['Parameter']] = None
    ):
        super().__init__(name, type, internalType, description, components)
        self.value = value

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class EVMTokenCreateParams:
    def __init__(
        self,
        contractId: str,
        constructorParams: Optional[List[ParameterWithValue]] = None
    ):
        self.contractId = contractId
        self.constructorParams = constructorParams

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class StellarRippleCreateParams:
    def __init__(
        self,
        issuerAddress: Optional[str] = None
    ):
        self.issuerAddress = issuerAddress

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class CreateTokenRequest:
    def __init__(
        self,
        symbol: str,
        name: str,
        blockchainId: str,
        vaultAccountId: str,
        createParams: Union[EVMTokenCreateParams, StellarRippleCreateParams]
    ):
        self.symbol = symbol
        self.name = name
        self.blockchainId = blockchainId
        self.vaultAccountId = vaultAccountId
        self.createParams = createParams

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class ContractDeployRequest:
    def __init__(
        self,
        asset_id: str,
        vault_account_id: str,
        constructorParameters: Optional[List[ParameterWithValue]] = None
    ):
        self.asset_id = asset_id
        self.vault_account_id = vault_account_id
        self.constructorParameters = constructorParameters

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class AbiFunction:
    def __init__(
        self,
        name: str,
        type: str,
        stateMutability: str,
        inputs: List[Parameter],
        outputs: Optional[List[Parameter]] = None,
        description: Optional[str] = None,
        returns: Optional[Dict[str, str]] = None
    ):
        self.name = name
        self.type = type
        self.stateMutability = stateMutability
        self.inputs = inputs
        self.outputs = outputs
        self.description = description
        self.returns = returns

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class ContractInitializationPhase(str, Enum):
    ON_DEPLOYMENT = "ON_DEPLOYMENT"
    POST_DEPLOYMENT = "POST_DEPLOYMENT"

class ContractTemplateType(str, Enum):
	FUNGIBLE_TOKEN = "FUNGIBLE_TOKEN"
	NON_FUNGIBLE_TOKEN = "NON_FUNGIBLE_TOKEN"
	NON_TOKEN = "NON_TOKEN"
	UUPS_PROXY = "UUPS_PROXY"

class ContractUploadRequest:
    def __init__(
        self,
        name: str,
        description: str,
        longDescription: str,
        bytecode: str,
        sourcecode: str,
        initializationPhase: ContractInitializationPhase,
        abi: Optional[List[AbiFunction]] = None,
        compilerOutputMetadata: Optional[object] = None,
        docs: Optional[object] = None,
        attributes: Optional[Dict[str, str]] = None,
        type: Optional[ContractTemplateType] = None,
        inputFieldsMetadata: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.longDescription = longDescription
        self.bytecode = bytecode
        self.sourcecode = sourcecode
        self.initializationPhase = initializationPhase
        self.abi = abi
        self.compilerOutputMetadata = compilerOutputMetadata
        self.docs = docs
        self.attributes = attributes
        self.type = type
        self.inputFieldsMetadata = inputFieldsMetadata

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class ReadCallFunction:
    def __init__(
        self,
        abiFunction: AbiFunction,
    ):
        self.abiFunction = abiFunction

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)

class WriteCallFunction:
    def __init__(
        self,
        vaultAccountId: str,
        abiFunction: AbiFunction,
        amount: Optional[str] = None,
        feeLevel: Optional[str] = None,
        note: Optional[str] = None,
    ):
        self.vaultAccountId = vaultAccountId
        self.abiFunction = abiFunction
        self.amount = amount
        self.feeLevel = feeLevel
        self.note = note

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)
