from typing import List, Union

from fireblocks_sdk.common.wrappers import response_deserializer
from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.entities.op_success_response import OperationSuccessResponse
from fireblocks_sdk.services.base_service import BaseService
from fireblocks_sdk.services.fiat.fiat_account_response import FiatAccountResponse


class FiatService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    @response_deserializer(FiatAccountResponse)
    def get_fiat_accounts(self) -> List[FiatAccountResponse]:
        """Gets all fiat accounts for your tenant"""

        return self.connector.get("/v1/fiat_accounts").content

    @response_deserializer(FiatAccountResponse)
    def get_fiat_account_by_id(self, account_id: str) -> FiatAccountResponse:
        """Gets a single fiat account by ID

        Args:
            account_id (string): The fiat account ID
        """

        return self.connector.get(f"/v1/fiat_accounts/{account_id}").content

    @response_deserializer(OperationSuccessResponse)
    def redeem_to_linked_dda(self, account_id: str, amount: float,
                             idempotency_key: Union[str, None] = None) -> OperationSuccessResponse:
        """Redeem from a fiat account to a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (double): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "amount": amount,
        }

        return self.connector.post(
            f"/v1/fiat_accounts/{account_id}/redeem_to_linked_dda", body, idempotency_key).content

    @response_deserializer(OperationSuccessResponse)
    def deposit_from_linked_dda(self, account_id: str, amount: float,
                                idempotency_key: Union[str, None] = None) -> OperationSuccessResponse:
        """Deposit to a fiat account from a linked DDA

        Args:
            account_id (string): The fiat account ID in Fireblocks
            amount (float): The amount to transfer
            idempotency_key (str, optional)
        """
        body = {
            "amount": amount,
        }

        return self.connector.post(
            f"/v1/fiat_accounts/{account_id}/deposit_from_linked_dda", body, idempotency_key).content
