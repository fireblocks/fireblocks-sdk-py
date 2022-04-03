
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

        if one_time_address != None:
            self.oneTimeAddress = one_time_address


TRANSACTION_TRANSFER = "TRANSFER"
TRANSACTION_MINT = "MINT"
TRANSACTION_BURN = "BURN"
TRANSACTION_SUPPLY_TO_COMPOUND = "SUPPLY_TO_COMPOUND"
TRANSACTION_REDEEM_FROM_COMPOUND = "REDEEM_FROM_COMPOUND"
RAW = "RAW"
CONTRACT_CALL = "CONTRACT_CALL"
ONE_TIME_ADDRESS = "ONE_TIME_ADDRESS"

TRANSACTION_TYPES = (TRANSACTION_TRANSFER, TRANSACTION_MINT, TRANSACTION_BURN, TRANSACTION_SUPPLY_TO_COMPOUND, TRANSACTION_REDEEM_FROM_COMPOUND, RAW, CONTRACT_CALL, ONE_TIME_ADDRESS)

TRANSACTION_STATUS_SUBMITTED = "SUBMITTED"
TRANSACTION_STATUS_QUEUED = "QUEUED"
TRANSACTION_STATUS_PENDING_SIGNATURE= "PENDING_SIGNATURE"
TRANSACTION_STATUS_PENDING_AUTHORIZATION = "PENDING_AUTHORIZATION"
TRANSACTION_STATUS_PENDING_3RD_PARTY_MANUAL_APPROVAL = "PENDING_3RD_PARTY_MANUAL_APPROVAL"
TRANSACTION_STATUS_PENDING_3RD_PARTY = "PENDING_3RD_PARTY"
TRANSACTION_STATUS_PENDING = "PENDING" # Deprecated
TRANSACTION_STATUS_BROADCASTING = "BROADCASTING"
TRANSACTION_STATUS_CONFIRMING = "CONFIRMING"
TRANSACTION_STATUS_CONFIRMED = "CONFIRMED" # Deprecated
TRANSACTION_STATUS_COMPLETED = "COMPLETED"
TRANSACTION_STATUS_PENDING_AML_SCREENING = "PENDING_AML_SCREENING"
TRANSACTION_STATUS_PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
TRANSACTION_STATUS_CANCELLING = "CANCELLING"
TRANSACTION_STATUS_CANCELLED = "CANCELLED"
TRANSACTION_STATUS_REJECTED = "REJECTED"
TRANSACTION_STATUS_FAILED = "FAILED"
TRANSACTION_STATUS_TIMEOUT = "TIMEOUT"
TRANSACTION_STATUS_BLOCKED = "BLOCKED"

TRANSACTION_STATUS_TYPES = (TRANSACTION_STATUS_SUBMITTED,
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

PEER_TYPES = (VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT, NETWORK_CONNECTION, COMPOUND, ONE_TIME_ADDRESS)

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
    def __init__(self, messages, algorithm):
        """Defines raw message

        Args:
          messages (list of UnsignedMessage):
          algorithm (str):
        """

        self.messages = messages
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
    def __init__(self, name_prefix=None, name_suffix=None, min_amount_threshold=None, asset_id=None, order_by=None, limit=None, before=None, after=None):
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix
        self.min_amount_threshold = min_amount_threshold
        self.asset_id = asset_id
        self.order_by = order_by
        self.limit = limit
        self.before = before
        self.after = after
