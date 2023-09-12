from enum import Enum
from typing import Optional, List, Union


class TransferPeerPath(object):
    def __init__(self, peer_type, peer_id):
        """Defines a source or a destination for a transfer

        Args:
            peer_type (str): either VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, FIAT_ACCOUNT, NETWORK_CONNECTION, ONE_TIME_ADDRESS or UNKNOWN_PEER
            peer_id (str): the account/wallet id
        """

        if peer_type not in PEER_TYPES:
            raise Exception("Got invalid transfer peer type: " + peer_type)
        self.type = peer_type
        if peer_id is not None:
            self.id = str(peer_id)


class DestinationTransferPeerPath(TransferPeerPath):
    def __init__(self, peer_type, peer_id=None, one_time_address=None):
        """Defines a destination for a transfer

        Args:
            peer_type (str): either VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, FIAT_ACCOUNT, NETWORK_CONNECTION, ONE_TIME_ADDRESS or UNKNOWN_PEER
            peer_id (str): the account/wallet id
            one_time_address (JSON object): The destination address (and tag) for a non whitelisted address.
        """
        TransferPeerPath.__init__(self, peer_type, peer_id)

        if one_time_address is not None:
            self.oneTimeAddress = one_time_address


TRANSACTION_TRANSFER = "TRANSFER"
TRANSACTION_MINT = "MINT"
TRANSACTION_BURN = "BURN"
TRANSACTION_SUPPLY_TO_COMPOUND = "SUPPLY_TO_COMPOUND"
TRANSACTION_REDEEM_FROM_COMPOUND = "REDEEM_FROM_COMPOUND"
RAW = "RAW"
CONTRACT_CALL = "CONTRACT_CALL"
ONE_TIME_ADDRESS = "ONE_TIME_ADDRESS"
TYPED_MESSAGE = "TYPED_MESSAGE"

TRANSACTION_TYPES = (
    TRANSACTION_TRANSFER,
    TRANSACTION_MINT,
    TRANSACTION_BURN,
    TRANSACTION_SUPPLY_TO_COMPOUND,
    TRANSACTION_REDEEM_FROM_COMPOUND,
    RAW,
    CONTRACT_CALL,
    ONE_TIME_ADDRESS,
    TYPED_MESSAGE
)

TRANSACTION_STATUS_SUBMITTED = "SUBMITTED"
TRANSACTION_STATUS_QUEUED = "QUEUED"
TRANSACTION_STATUS_PENDING_SIGNATURE = "PENDING_SIGNATURE"
TRANSACTION_STATUS_PENDING_AUTHORIZATION = "PENDING_AUTHORIZATION"
TRANSACTION_STATUS_PENDING_3RD_PARTY_MANUAL_APPROVAL = "PENDING_3RD_PARTY_MANUAL_APPROVAL"
TRANSACTION_STATUS_PENDING_3RD_PARTY = "PENDING_3RD_PARTY"
TRANSACTION_STATUS_PENDING = "PENDING"  # Deprecated
TRANSACTION_STATUS_BROADCASTING = "BROADCASTING"
TRANSACTION_STATUS_CONFIRMING = "CONFIRMING"
TRANSACTION_STATUS_CONFIRMED = "CONFIRMED"  # Deprecated
TRANSACTION_STATUS_COMPLETED = "COMPLETED"
TRANSACTION_STATUS_PENDING_AML_SCREENING = "PENDING_AML_SCREENING"
TRANSACTION_STATUS_PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
TRANSACTION_STATUS_CANCELLING = "CANCELLING"
TRANSACTION_STATUS_CANCELLED = "CANCELLED"
TRANSACTION_STATUS_REJECTED = "REJECTED"
TRANSACTION_STATUS_FAILED = "FAILED"
TRANSACTION_STATUS_TIMEOUT = "TIMEOUT"
TRANSACTION_STATUS_BLOCKED = "BLOCKED"

TRANSACTION_STATUS_TYPES = (
    TRANSACTION_STATUS_SUBMITTED,
    TRANSACTION_STATUS_QUEUED,
    TRANSACTION_STATUS_PENDING_SIGNATURE,
    TRANSACTION_STATUS_PENDING_AUTHORIZATION,
    TRANSACTION_STATUS_PENDING_3RD_PARTY_MANUAL_APPROVAL,
    TRANSACTION_STATUS_PENDING_3RD_PARTY,
    TRANSACTION_STATUS_PENDING,
    TRANSACTION_STATUS_BROADCASTING,
    TRANSACTION_STATUS_CONFIRMING,
    TRANSACTION_STATUS_CONFIRMED,
    TRANSACTION_STATUS_COMPLETED,
    TRANSACTION_STATUS_PENDING_AML_SCREENING,
    TRANSACTION_STATUS_PARTIALLY_COMPLETED,
    TRANSACTION_STATUS_CANCELLING,
    TRANSACTION_STATUS_CANCELLED,
    TRANSACTION_STATUS_REJECTED,
    TRANSACTION_STATUS_FAILED,
    TRANSACTION_STATUS_TIMEOUT,
    TRANSACTION_STATUS_BLOCKED
)

VAULT_ACCOUNT = "VAULT_ACCOUNT"
EXCHANGE_ACCOUNT = "EXCHANGE_ACCOUNT"
INTERNAL_WALLET = "INTERNAL_WALLET"
EXTERNAL_WALLET = "EXTERNAL_WALLET"
UNKNOWN_PEER = "UNKNOWN"
FIAT_ACCOUNT = "FIAT_ACCOUNT"
NETWORK_CONNECTION = "NETWORK_CONNECTION"
COMPOUND = "COMPOUND"

PEER_TYPES = (
    VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT, NETWORK_CONNECTION,
    COMPOUND, ONE_TIME_ADDRESS)

MPC_ECDSA_SECP256K1 = "MPC_ECDSA_SECP256K1"
MPC_EDDSA_ED25519 = "MPC_EDDSA_ED25519"

SIGNING_ALGORITHM = (MPC_ECDSA_SECP256K1, MPC_EDDSA_ED25519)

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"

FEE_LEVEL = (HIGH, MEDIUM, LOW)


class TransferTicketTerm(object):
    def __init__(self, network_connection_id, outgoing, asset, amount, note=None, operation=TRANSACTION_TRANSFER):
        """Defines a transfer ticket's term

        Args:
          network_connection_id (str): The Fireblocks network connection on which this term should be fulfilled
          outgoing (bool): True means that the term is from the initiator of the ticket
          asset (str): The asset of term that was agreed on
          amount (str): The amount of the asset that should be transferred
          note (str, optional): Custom note that can be added to the term

        """

        self.networkConnectionId = str(network_connection_id)
        self.outgoing = bool(outgoing)
        self.asset = str(asset)
        self.amount = str(amount)
        if note:
            self.note = str(note)
        self.operation = operation


class UnsignedMessage(object):
    def __init__(self, content, bip44addressIndex=None, bip44change=None, derivationPath=None):
        """Defines message to be signed by raw transaction

        Args:
          content (str): The message to be signed in hex format encoding
          bip44addressIndex (number, optional):  BIP44 address_index path level
          bip44change (number, optional): BIP44 change path level
          derivationPath (list of numbers, optional): Should be passed only if asset and source were not specified
        """

        self.content = content

        if bip44addressIndex:
            self.bip44addressIndex = bip44addressIndex

        if bip44change:
            self.bip44change = bip44change

        if derivationPath:
            self.derivationPath = derivationPath


class RawMessage(object):
    def __init__(self, messages, algorithm=None):
        """Defines raw message

        Args:
          messages (list of UnsignedMessage):
          algorithm (str, optional):
        """

        self.messages = messages
        if algorithm:
            self.algorithm = algorithm


class TransactionDestination(object):
    def __init__(self, amount, destination):
        """Defines destinations for multiple outputs transaction

        Args:
          amount (double): The amount to transfer
          destination (DestinationTransferPeerPath): The transfer destination
        """

        self.amount = str(amount)
        self.destination = destination.__dict__


class FireblocksApiException(Exception):
    """Exception raised for Fireblocks sdk errors

    Attributes:
        message: explanation of the error
        error_code: error code of the error
    """

    def __init__(self, message="Fireblocks SDK error", error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class PagedVaultAccountsRequestFilters(object):
    """ Optional filters to apply for request

    Args
        name_prefix (string, optional): Vault account name prefix
        name_suffix (string, optional): Vault account name suffix
        min_amount_threshold (number, optional):  The minimum amount for asset to have in order to be included in the results
        asset_id (string, optional): The asset symbol
        order_by (ASC/DESC, optional): Order of results by vault creation time (default: DESC)
        limit (number, optional): Results page size
        before (string, optional): cursor string received from previous request
        after (string, optional): cursor string received from previous request

    Constraints
        - You should only insert 'name_prefix' or 'name_suffix' (or none of them), but not both
        - You should only insert 'before' or 'after' (or none of them), but not both
        - For default and max 'limit' values please see: https://docs.fireblocks.com/api/swagger-ui/#/
    """

    def __init__(self, name_prefix=None, name_suffix=None, min_amount_threshold=None, asset_id=None, order_by=None,
                 limit=None, before=None,
                 after=None):
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix
        self.min_amount_threshold = min_amount_threshold
        self.asset_id = asset_id
        self.order_by = order_by
        self.limit = limit
        self.before = before
        self.after = after


class GetAssetWalletsFilters(object):
    """ Optional filters to apply for request

    Args
        total_amount_larger_than (number, optional):  The minimum amount for asset to have in order to be included in the results
        asset_id (string, optional): The asset symbol
        order_by (ASC/DESC, optional): Order of results by vault creation time (default: DESC)
        limit (number, optional): Results page size
        before (string, optional): cursor string received from previous request
        after (string, optional): cursor string received from previous request

    Constraints
        - You should only insert 'before' or 'after' (or none of them), but not both
    """

    def __init__(self, total_amount_larger_than=None, asset_id=None, order_by=None, limit=None, before=None,
                 after=None):
        self.total_amount_larger_than = total_amount_larger_than
        self.asset_id = asset_id
        self.order_by = order_by
        self.limit = limit
        self.before = before
        self.after = after


class GetOwnedNftsSortValues(str, Enum):
    OWNERSHIP_LAST_UPDATE_TIME = "ownershipLastUpdateTime"
    TOKEN_NAME = "name"
    COLLECTION_NAME = "collection.name"
    BLOCKCHAIN_DESCRIPTOR = "blockchainDescriptor"


class GetNftsSortValues(str, Enum):
    TOKEN_NAME = "name"
    COLLECTION_NAME = "collection.name"
    BLOCKCHAIN_DESCRIPTOR = "blockchainDescriptor"


class NFTOwnershipStatusValues(str, Enum):
    LISTED = "LISTED"
    ARCHIVED = "ARCHIVED"


class GetOwnedCollectionsSortValue(str, Enum):
    COLLECTION_NAME = "name"


class OrderValues(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class TimePeriod(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"


class IssueTokenRequest:
    symbol: str
    name: str
    blockchain_id: str
    eth_contract_address: Optional[str]
    issuer_address: Optional[str]
    decimals: int

    def serialize(self) -> dict:
        obj = {
            'symbol': self.symbol,
            'name': self.name,
            'blockchainId': self.blockchain_id,
            'decimals': self.decimals,
        }

        if self.eth_contract_address:
            obj.update({'ethContractAddress': self.eth_contract_address})

        if self.issuer_address:
            obj.update({'issuerAddress': self.issuer_address})

        return obj


class PolicyTransactionType(str, Enum):
    ANY = "*"
    CONTRACT_CALL = "CONTRACT_CALL"
    RAW = "RAW"
    TRANSFER = "TRANSFER"
    APPROVE = "APPROVE"
    MINT = "MINT"
    BURN = "BURN"
    SUPPLY = "SUPPLY"
    REDEEM = "REDEEM"
    STAKE = "STAKE"
    TYPED_MESSAGE = "TYPED_MESSAGE"

class PolicySrcOrDestType(str, Enum):
    EXCHANGE = "EXCHANGE"
    UNMANAGED = "UNMANAGED"
    VAULT = "VAULT"
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    COMPOUND = "COMPOUND"
    FIAT_ACCOUNT = "FIAT_ACCOUNT"
    ONE_TIME_ADDRESS = "ONE_TIME_ADDRESS"
    ANY = "*"

class PolicyType(str, Enum):
    TRANSFER = "TRANSFER"

class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    TWO_TIER = "2-TIER"

class PolicyDestAddressType(str, Enum):
    ANY = "*"
    WHITELISTED = "WHITELISTED"
    ONE_TIME = "ONE_TIME"

class PolicyAmountScope(str, Enum):
    SINGLE_TX = "SINGLE_TX"
    TIMEFRAME = "TIMEFRAME"

class PolicySrcOrDestSubType(str, Enum):
    ANY = "*"
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"
    CONTRACT = "CONTRACT"
    EXCHANGETEST = "EXCHANGETEST"

class Wildcard(str, Enum):
    WILDCARD = "*"

class AuthorizationLogic(str, Enum):
    AND = "AND"
    OR = "OR"

class AuthorizationGroup:
    def __init__(self, users: Optional[List[str]] = None, usersGroups: Optional[List[str]] = None, th: int = 0):
        if users:
            self.users = users
        if usersGroups:
            self.usersGroups = usersGroups
        self.th = th

class PolicyAuthorizationGroups:
    def __init__(self, logic: AuthorizationLogic, allowOperatorAsAuthorizer: Optional[bool] = None, groups: List[AuthorizationGroup] = []):
        self.logic = logic
        if allowOperatorAsAuthorizer:
            self.allowOperatorAsAuthorizer = allowOperatorAsAuthorizer
        self.groups = groups

class Operators:
    def __init__(self, wildcard: Optional[Wildcard] = None, users: Optional[List[str]] = None, usersGroups: Optional[List[str]] = None, services: Optional[List[str]] = None):
        if wildcard:
            self.wildcard = wildcard
        if users:
            self.users = users
        if usersGroups:
            self.usersGroups = usersGroups
        if services:
            self.services = services

class DesignatedSigners:
    def __init__(self, users: Optional[List[str]] = None, usersGroups: Optional[List[str]] = None):
        if users:
            self.users = users
        if usersGroups:
            self.usersGroups = usersGroups

class SrcDst:
    def __init__(self, ids: Optional[List[List[Union[str, PolicySrcOrDestType, PolicySrcOrDestSubType]]]] = None):
        if ids:
            self.ids = ids

class AmountAggregation:
    def __init__(self, operators: str, srcTransferPeers: str, dstTransferPeers: str):
        self.operators = operators
        self.srcTransferPeers = srcTransferPeers
        self.dstTransferPeers = dstTransferPeers

class DerivationPath:
    def __init__(self, path: List[int]):
        self.path = path

class RawMessageSigning:
    def __init__(self, derivationPath: DerivationPath, algorithm: str):
        self.derivationPath = derivationPath
        self.algorithm = algorithm

class PolicyRule:
    def __init__(self,
                 type: PolicyType,
                 action: PolicyAction,
                 asset: str,
                 amountCurrency: str,
                 amountScope: PolicyAmountScope,
                 amount: Union[int, str],
                 periodSec: int,
                 externalDescriptor: str,
                 operator: Optional[str] = None,
                 operators: Optional[Operators] = None,
                 transactionType: Optional[PolicyTransactionType] = None,
                 operatorServices: Optional[List[str]] = None,
                 designatedSigner: Optional[str] = None,
                 designatedSigners: Optional[DesignatedSigners] = None,
                 srcType: Optional[PolicySrcOrDestType] = None,
                 srcSubType: Optional[PolicySrcOrDestSubType] = None,
                 srcId: Optional[str] = None,
                 src: Optional[SrcDst] = None,
                 dstType: Optional[PolicySrcOrDestType] = None,
                 dstSubType: Optional[PolicySrcOrDestSubType] = None,
                 dstId: Optional[str] = None,
                 dst: Optional[SrcDst] = None,
                 dstAddressType: Optional[PolicyDestAddressType] = None,
                 authorizers: Optional[List[str]] = None,
                 authorizersCount: Optional[int] = None,
                 authorizationGroups: Optional[PolicyAuthorizationGroups] = None,
                 amountAggregation: Optional[AmountAggregation] = None,
                 rawMessageSigning: Optional[RawMessageSigning] = None,
                 applyForApprove: Optional[bool] = None,
                 applyForTypedMessage: Optional[bool] = None):
        self.type = type
        self.action = action
        self.asset = asset
        self.amountCurrency = amountCurrency
        self.amountScope = amountScope
        self.amount = amount
        self.periodSec = periodSec
        self.externalDescriptor = externalDescriptor
        if operator:
            self.operator = operator
        if operators:
            self.operators = operators
        if transactionType:
            self.transactionType = transactionType
        if operatorServices:
           self.operatorServices = operatorServices
        if designatedSigner:
            self.designatedSigner = designatedSigner
        if designatedSigners:
            self.designatedSigners = designatedSigners
        if srcType:
            self.srcType = srcType
        if srcSubType:
            self.srcSubType = srcSubType
        if srcId:
            self.srcId = srcId
        if src:
            self.src = src
        if dstType:
            self.dstType = dstType
        if dstSubType:
            self.dstSubType = dstSubType
        if dstId:
            self.dstId = dstId
        if dst:
            self.dst = dst
        if dstAddressType:
            self.dstAddressType = dstAddressType
        if authorizers:
            self.authorizers = authorizers
        if authorizersCount:
            self.authorizersCount = authorizersCount
        if authorizationGroups:
            self.authorizationGroups = authorizationGroups
        if amountAggregation:
            self.amountAggregation = amountAggregation
        if rawMessageSigning:
            self.rawMessageSigning = rawMessageSigning
        if applyForApprove:
            self.applyForApprove = applyForApprove
        if applyForTypedMessage:
            self.applyForTypedMessage = applyForTypedMessage

    def to_dict(self):
        rule_dict = {
            "type": self.type,
            "action": self.action,
            "asset": self.asset,
            "amountCurrency": self.amountCurrency,
            "amountScope": self.amountScope,
            "amount": self.amount,
            "periodSec": self.periodSec,
            "externalDescriptor": self.externalDescriptor
        }

        if hasattr(self, "operator"):
            rule_dict["operator"] = self.operator
        if hasattr(self, "operators"):
            rule_dict["operators"] = self.operators.__dict__
        if hasattr(self, "transactionType"):
            rule_dict["transactionType"] = self.transactionType
        if hasattr(self, "operatorServices"):
            rule_dict["operatorServices"] = self.operatorServices
        if hasattr(self, "designatedSigner"):
            rule_dict["designatedSigner"] = self.designatedSigner
        if hasattr(self, "designatedSigners"):
            rule_dict["designatedSigners"] = self.designatedSigners.__dict__
        if hasattr(self, "srcType"):
            rule_dict["srcType"] = self.srcType
        if hasattr(self, "srcSubType"):
            rule_dict["srcSubType"] = self.srcSubType
        if hasattr(self, "srcId"):
            rule_dict["srcId"] = self.srcId
        if hasattr(self, "src"):
            rule_dict["src"] = self.src.__dict__
        if hasattr(self, "dstType"):
            rule_dict["dstType"] = self.dstType
        if hasattr(self, "dstSubType"):
            rule_dict["dstSubType"] = self.dstSubType
        if hasattr(self, "dstId"):
            rule_dict["dstId"] = self.dstId
        if hasattr(self, "dst"):
            rule_dict["dst"] = self.dst.__dict__
        if hasattr(self, "dstAddressType"):
            rule_dict["dstAddressType"] = self.dstAddressType
        if hasattr(self, "authorizers"):
            rule_dict["authorizers"] = self.authorizers
        if hasattr(self, "authorizersCount"):
            rule_dict["authorizersCount"] = self.authorizersCount
        if hasattr(self, "authorizationGroups"):
            rule_dict["authorizationGroups"] = {
                "logic": self.authorizationGroups.logic,
                "allowOperatorAsAuthorizer": self.authorizationGroups.allowOperatorAsAuthorizer,
                "groups": [group.__dict__ for group in self.authorizationGroups.groups]
            }
        if hasattr(self, "amountAggregation"):
            rule_dict["amountAggregation"] = self.amountAggregation.__dict__
        if hasattr(self, "rawMessageSigning"):
            rule_dict["rawMessageSigning"] = {
                "derivationPath": self.rawMessageSigning.derivationPath.__dict__,
                "algorithm": self.rawMessageSigning.algorithm
            }
        if hasattr(self, "applyForApprove"):
            rule_dict["applyForApprove"] = self.applyForApprove
        if hasattr(self, "applyForTypedMessage"):
            rule_dict["applyForTypedMessage"] = self.applyForTypedMessage

        return rule_dict
