from enum import StrEnum, auto, Enum
from typing import Optional, List, Union


def snake_to_camel(snake_case: str):
    words = snake_case.split('_')
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def convert_class_to_dict(class_dict: dict):
    output_dict = {}
    for key, value in class_dict.items():
        if isinstance(value, list):
            output_dict[snake_to_camel(key)] = [item.to_dict() if hasattr(item, 'to_dict') else item for item
                                                in value]
        elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            output_dict[snake_to_camel(key)] = value.to_dict()
        elif value is not None:
            output_dict[snake_to_camel(key)] = value
    return output_dict


class TransferPeerPath:
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


class TransferTicketTerm:
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


class UnsignedMessage:
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


class RawMessage:
    def __init__(self, messages, algorithm=None):
        """Defines raw message

        Args:
          messages (list of UnsignedMessage):
          algorithm (str, optional):
        """

        self.messages = messages
        if algorithm:
            self.algorithm = algorithm


class TransactionDestination:
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


class PagedVaultAccountsRequestFilters:
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


class PagedExchangeAccountRequestFilters:
    """ Optional filters to apply for request

    Args

        limit (number, optional): Results page size
        before (string, optional): cursor string received from previous request
        after (string, optional): cursor string received from previous request

    Constraints
        - You should only insert 'before' or 'after' (or none of them), but not both
        - For default and max 'limit' values please see: https://docs.fireblocks.com/api/swagger-ui/#/
    """

    def __init__(self, limit=None, before=None, after=None):
        self.limit = limit
        self.before = before
        self.after = after


class GetAssetWalletsFilters:
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


class GetSmartTransferFilters:
    """ Optional filters to apply for request
    Args
        query (string, optional):  Search query string - either ticketId, asset or network name
        statuses (DRAFT/PENDING_APPROVAL/OPEN/IN_SETTLEMENT/FULFILLED/EXPIRED/CANCELED, optional): array of ticket statuses
        network_id (string, optional): networkId used in ticket
        created_by_me (bool, optional): created by me flag
        expires_after (string, optional): Lower bound of search range
        expires_before (string, optional): Upper bound of search range
        ticket_type (ASYNC/ATOMIC, optional): type of ticket
        external_ref_id (string, optional): external ref id
        after (string, optional): cursor string received from previous request
        limit (number, optional): Results page size

    Constraints
        - You should only insert 'before' or 'after' (or none of them), but not both
    """

    def __init__(self, query: Optional[str] = None, statuses: Optional[str] = None, network_id: Optional[str] = None,
                 created_by_me: Optional[bool] = None, expires_after: Optional[str] = None,
                 expires_before: Optional[str] = None, ticket_type: Optional[str] = None,
                 external_ref_id: Optional[str] = None, after: Optional[str] = None, limit: Optional[str] = None):
        self.query = query
        self.statuses = statuses
        self.network_id = network_id
        self.created_by_me = created_by_me
        self.expires_after = expires_after
        self.expires_before = expires_before
        self.ticket_type = ticket_type
        self.external_ref_id = external_ref_id
        self.limit = limit
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


class NFTOwnershipStatusUpdatedPayload:
    def __init__(self, asset_id: str, status: NFTOwnershipStatusValues):
        self.asset_id = asset_id
        self.status = status

    def serialize(self) -> dict:
        return {
            'assetId': self.asset_id,
            'status': self.status,
        }


class GetOwnedCollectionsSortValue(str, Enum):
    COLLECTION_NAME = "name"


class GetOwnedAssetsSortValues(str, Enum):
    ASSET_NAME = "name"


class NFTsWalletTypeValues(str, Enum):
    VAULT_ACCOUNT = "VAULT_ACCOUNT"
    END_USER_WALLET = "END_USER_WALLET"

class SpamTokenOwnershipValues(StrEnum):
    true = auto()
    false = auto()
    all = auto()

class TokenOwnershipSpamUpdatePayload:
    def __init__(self, asset_id: str, spam: bool):
        self.asset_id = asset_id
        self.spam = spam

    def serialize(self) -> dict:
        return {
            'assetId': self.asset_id,
            'spam': self.spam,
        }

class OrderValues(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class TimePeriod(str, Enum):
    DAY = "DAY"
    WEEK = "WEEK"

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

class Role(str, Enum):
    ADMIN = "ADMIN"
    SIGNER = "SIGNER"
    EDITOR = "EDITOR"
    APPROVER = "APPROVER"
    VIEWER = "VIEWER"
    NON_SIGNING_ADMIN = "NON_SIGNING_ADMIN"
    AUDITOR = "AUDITOR"
    NCW_ADMIN = "NCW_ADMIN"
    NCW_SIGNER = "NCW_SIGNER"


class AuthorizationGroup:
    def __init__(self, users: Optional[List[str]] = None, users_groups: Optional[List[str]] = None, th: int = 0):
        if users:
            self.users = users
        if users_groups:
            self.users_groups = users_groups
        self.th = th

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class PolicyAuthorizationGroups:
    def __init__(self, logic: AuthorizationLogic, allow_operator_as_authorizer: Optional[bool] = None,
                 groups: List[AuthorizationGroup] = []):
        self.logic = logic
        if allow_operator_as_authorizer:
            self.allow_operator_as_authorizer = allow_operator_as_authorizer
        self.groups = groups

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class Operators:
    def __init__(self, wildcard: Optional[Wildcard] = None, users: Optional[List[str]] = None,
                 users_groups: Optional[List[str]] = None, services: Optional[List[str]] = None):
        if wildcard:
            self.wildcard = wildcard
        if users:
            self.users = users
        if users_groups:
            self.users_groups = users_groups
        if services:
            self.services = services

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class DesignatedSigners:
    def __init__(self, users: Optional[List[str]] = None, users_groups: Optional[List[str]] = None):
        if users:
            self.users = users
        if users_groups:
            self.users_groups = users_groups

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class SrcDst:
    def __init__(self, ids: Optional[List[List[Union[str, PolicySrcOrDestType, PolicySrcOrDestSubType]]]] = None):
        if ids:
            self.ids = ids

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class AmountAggregation:
    def __init__(self, operators: str, src_transfer_peers: str, dst_transfer_peers: str):
        self.operators = operators
        self.src_transfer_peers = src_transfer_peers
        self.dst_transfer_peers = dst_transfer_peers

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class DerivationPath:
    def __init__(self, path: List[int]):
        self.path = path

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class RawMessageSigning:
    def __init__(self, derivation_path: DerivationPath, algorithm: str):
        self.derivation_path = derivation_path
        self.algorithm = algorithm

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class PolicyRule:
    def __init__(self,
                 type: PolicyType,
                 action: PolicyAction,
                 asset: str,
                 amount_currency: str,
                 amount_scope: PolicyAmountScope,
                 amount: Union[int, str],
                 period_sec: int,
                 external_descriptor: Optional[str] = None,
                 operator: Optional[str] = None,
                 operators: Optional[Operators] = None,
                 transaction_type: Optional[PolicyTransactionType] = None,
                 operator_services: Optional[List[str]] = None,
                 designated_signer: Optional[str] = None,
                 designated_signers: Optional[DesignatedSigners] = None,
                 src_type: Optional[PolicySrcOrDestType] = None,
                 src_sub_type: Optional[PolicySrcOrDestSubType] = None,
                 src_id: Optional[str] = None,
                 src: Optional[SrcDst] = None,
                 dst_type: Optional[PolicySrcOrDestType] = None,
                 dst_sub_type: Optional[PolicySrcOrDestSubType] = None,
                 dst_id: Optional[str] = None,
                 dst: Optional[SrcDst] = None,
                 dst_address_type: Optional[PolicyDestAddressType] = None,
                 authorizers: Optional[List[str]] = None,
                 authorizers_count: Optional[int] = None,
                 authorization_groups: Optional[PolicyAuthorizationGroups] = None,
                 amount_aggregation: Optional[AmountAggregation] = None,
                 raw_message_signing: Optional[RawMessageSigning] = None,
                 apply_for_approve: Optional[bool] = None,
                 apply_for_typed_message: Optional[bool] = None):
        self.type = type
        self.action = action
        self.asset = asset
        self.amount_currency = amount_currency
        self.amount_scope = amount_scope
        self.amount = amount
        self.period_sec = period_sec
        if external_descriptor:
            self.external_descriptor = external_descriptor
        if operator:
            self.operator = operator
        if operators:
            self.operators = operators
        if transaction_type:
            self.transaction_type = transaction_type
        if operator_services:
            self.operator_services = operator_services
        if designated_signer:
            self.designated_signer = designated_signer
        if designated_signers:
            self.designated_signers = designated_signers
        if src_type:
            self.src_type = src_type
        if src_sub_type:
            self.src_sub_type = src_sub_type
        if src_id:
            self.src_id = src_id
        if src:
            self.src = src
        if dst_type:
            self.dst_type = dst_type
        if dst_sub_type:
            self.dst_sub_type = dst_sub_type
        if dst_id:
            self.dst_id = dst_id
        if dst:
            self.dst = dst
        if dst_address_type:
            self.dst_address_type = dst_address_type
        if authorizers:
            self.authorizers = authorizers
        if authorizers_count:
            self.authorizers_count = authorizers_count
        if authorization_groups:
            self.authorization_groups = authorization_groups
        if amount_aggregation:
            self.amount_aggregation = amount_aggregation
        if raw_message_signing:
            self.raw_message_signing = raw_message_signing
        if apply_for_approve:
            self.apply_for_approve = apply_for_approve
        if apply_for_typed_message:
            self.apply_for_typed_message = apply_for_typed_message

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class StakeRequestDto:
    def __init__(self,
                 vault_account_id: str,
                 provider_id: str,
                 stake_amount: str,
                 tx_note: str = None,
                 fee: str = None,
                 fee_level: str = None):
        self.vault_account_id = vault_account_id
        self.provider_id = provider_id
        self.stake_amount = stake_amount
        self.tx_note = tx_note
        self.fee = fee
        self.fee_level = fee_level

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class UnstakeRequestDto:
    def __init__(self, id: str, fee: str = None, fee_level: str = None, tx_note: str = None):
        self.id = id
        self.fee = fee
        self.fee_level = fee_level
        self.tx_note = tx_note

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)


class WithdrawRequestDto:
    def __init__(self, id: str, fee: str = None, fee_level: str = None, tx_note: str = None):
        self.id = id
        self.fee = fee
        self.fee_level = fee_level
        self.tx_note = tx_note

    def to_dict(self):
        return convert_class_to_dict(self.__dict__)
