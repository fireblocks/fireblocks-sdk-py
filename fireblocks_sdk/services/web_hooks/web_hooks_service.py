from fireblocks_sdk.connectors.rest import RestConnector
from fireblocks_sdk.services.base_service import BaseService


class WebHooksService(BaseService):
    def __init__(self, connector: RestConnector) -> None:
        super().__init__(connector)

    def resend_webhooks(self):
        """Resend failed webhooks of your tenant"""

        return self.connector.post("/v1/webhooks/resend")

    def resend_transaction_webhooks_by_id(self, tx_id: str, resend_created: bool, resend_status_updated: bool):
        """Resend webhooks of transaction

        Args:
            tx_id (str): The transaction for which the message is sent.
            resend_created (boolean): If true, a webhook will be sent for the creation of the transaction.
            resend_status_updated (boolean): If true, a webhook will be sent for the status of the transaction.
        """
        body = {
            "resendCreated": resend_created,
            "resendStatusUpdated": resend_status_updated
        }

        return self.connector.post(f"/v1/webhooks/resend/{tx_id}", body)
