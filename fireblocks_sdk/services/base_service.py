from fireblocks_sdk.connectors.rest import RestConnector


class BaseService:
    def __init__(self, connector: RestConnector) -> None:
        self.connector = connector
