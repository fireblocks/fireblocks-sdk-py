
class TransferPeerPath(object):
    def __init__(self, peer_type, peer_id):
        """Defines a source or a destination for a transfer

        Args:
            peer_type (str): either VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, FIAT_ACCOUNT, NETWORK_CONNECTION or UNKNOWN_PEER
            peer_id (str): the account/wallet id
        """

        if peer_type not in PEER_TYPES:
            raise Exception("Got invalid transfer peer type: " + peer_type)
        self.type = peer_type
        self.id = str(peer_id)

class DestinationTransferPeerPath(TransferPeerPath):
    def __init__(self, peer_type, peer_id, one_time_address=None):
        """Defines a destination for a transfer

        Args:
            peer_type (str): either VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, FIAT_ACCOUNT, NETWORK_CONNECTION or UNKNOWN_PEER
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

TRANSACTION_TYPES = (TRANSACTION_TRANSFER, TRANSACTION_MINT, TRANSACTION_BURN, TRANSACTION_SUPPLY_TO_COMPOUND, TRANSACTION_REDEEM_FROM_COMPOUND)

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
TRANSACTION_STATUS_PENDING_AML_CHECKUP = "PENDING_AML_CHECKUP"
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
TRANSACTION_STATUS_PENDING_AML_CHECKUP,
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

PEER_TYPES = (VAULT_ACCOUNT, EXCHANGE_ACCOUNT, INTERNAL_WALLET, EXTERNAL_WALLET, UNKNOWN_PEER, FIAT_ACCOUNT, NETWORK_CONNECTION, COMPOUND)

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


class FireblocksApiException(Exception): pass
