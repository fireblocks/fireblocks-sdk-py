from typing import List

from fireblocks_sdk.api_types import FireblocksApiException, TransferPeerPath, TransferTicketTerm
from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.transfer_tickets.create_transfer_ticket_response import CreateTransferTicketResponse
from fireblocks_sdk.services.transfer_tickets.term_response import TermResponse
from fireblocks_sdk.services.transfer_tickets.transfer_ticket_response import TransferTicketResponse


class TransferTicketsService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(TransferTicketResponse)
    def get_transfer_tickets(self) -> List[TransferTicketResponse]:
        """Gets all transfer transfer_tickets of your tenant"""

        return self.connector.get("/v1/transfer_tickets").content

    @response_deserializer(CreateTransferTicketResponse)
    def create_transfer_ticket(self, terms, external_ticket_id=None, description=None,
                               idempotency_key=None) -> CreateTransferTicketResponse:
        """Creates a new transfer ticket

        Args:
            terms (list of TransferTicketTerm objects): The list of TransferTicketTerm
            external_ticket_id (str, optional): The ID for of the transfer ticket on customer's platform
            description (str, optional): A description for the new ticket
            idempotency_key (str, optional)
        """

        body = {}

        if external_ticket_id:
            body["externalTicketId"] = external_ticket_id

        if description:
            body["description"] = description

        if any([not isinstance(x, TransferTicketTerm) for x in terms]):
            raise FireblocksApiException(
                "Expected Tranfer Assist ticket's term of type TranferTicketTerm")

        body['terms'] = [term.__dict__ for term in terms]

        return self.connector.post(f"/v1/transfer_tickets", body, idempotency_key).content

    @response_deserializer(TransferTicketResponse)
    def get_transfer_ticket_by_id(self, ticket_id) -> TransferTicketResponse:
        """Retrieve a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket.
        """

        return self.connector.get(f"/v1/transfer_tickets/{ticket_id}").content

    @response_deserializer(TermResponse)
    def get_transfer_ticket_term(self, ticket_id, term_id) -> TermResponse:
        """Retrieve a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket
            term_id (str): The ID of the term within the transfer ticket
        """

        return self.connector.get(f"/v1/transfer_tickets/{ticket_id}/{term_id}").content

    def cancel_transfer_ticket(self, ticket_id, idempotency_key=None):
        """Cancel a transfer ticket

        Args:
            ticket_id (str): The ID of the transfer ticket to cancel
            idempotency_key (str, optional)
        """

        return self.connector.post(f"/v1/transfer_tickets/{ticket_id}/cancel", idempotency_key=idempotency_key)

    def execute_transfer_ticket_term(self, ticket_id, term_id, source: TransferPeerPath = None, idempotency_key=None):
        """Initiate a transfer ticket transaction

        Args:
            ticket_id (str): The ID of the transfer ticket
            term_id (str): The ID of the term within the transfer ticket
            source (TransferPeerPath): JSON object of the source of the transaction. The network connection's vault account by default
        """

        body = {}

        if source:
            if not isinstance(source, TransferPeerPath):
                raise FireblocksApiException(
                    "Expected ticket term source Of type TransferPeerPath, but got type: " + type(source))
            body["source"] = source.__dict__

        return self.connector.post(f"/v1/transfer_tickets/{ticket_id}/{term_id}/transfer", body, idempotency_key)
