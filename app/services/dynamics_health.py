from app.integrations.dynamics.exceptions import DynamicsError
from app.integrations.dynamics.protocols import DynamicsClient

class DynamicsHealthService:

    def __init__(self, client: DynamicsClient):
        self._client = client

    def is_connected(self) -> bool:
        try:
            self._client.ping()
            return True
        except DynamicsError:
            return False
