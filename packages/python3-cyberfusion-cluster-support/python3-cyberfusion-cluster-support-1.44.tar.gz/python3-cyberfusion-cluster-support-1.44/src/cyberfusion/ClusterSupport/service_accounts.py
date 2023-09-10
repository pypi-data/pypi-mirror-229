"""Helper classes for scripts for cluster support packages."""

from cyberfusion.ClusterSupport._interfaces import APIObjectInterface

ENDPOINT_SERVICE_ACCOUNTS = "service-accounts"


class ServiceAccount(APIObjectInterface):
    """Represents object."""

    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.id = obj["id"]
        self.name = obj["name"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

    def create(
        self,
        *,
        name: str,
    ) -> None:
        """Create object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS}"
        data = {"name": name}

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

        self.support.service_accounts.append(self)

    def delete(self) -> None:
        """Delete object."""
        url = f"/api/v1/{ENDPOINT_SERVICE_ACCOUNTS}/{self.id}"

        self.support.request.DELETE(url)
        self.support.request.execute()

        self.support.service_accounts.remove(self)
