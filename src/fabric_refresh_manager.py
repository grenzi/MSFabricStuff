import logging
import time
import msal
import requests


class FabricRefreshException(Exception):
    """Base exception for Fabric Refresh operations."""

    pass


class AccessTokenError(FabricRefreshException):
    """Exception raised when obtaining the access token fails."""

    pass


class RefreshError(FabricRefreshException):
    """Exception raised when the refresh request fails."""

    pass


class FabricRefreshManager:
    """
    Manager to handle access token acquisition and dataset refresh operations.
    """

    POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize the FabricRefreshManager with credentials.
        """
        self.tenant_id = tenant_id
        self.client_id = (
            client_id.split("@")[0].replace("app:", "")
            if client_id.startswith("app:")
            else client_id
        )
        self.client_secret = client_secret
        self.access_token = None
        self._msal_app = None

    @property
    def msal_app(self):
        """Lazy initialization of MSAL application"""
        if not self._msal_app:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            self._msal_app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret,
            )
        return self._msal_app

    def get_access_token(self) -> str:
        """
        Obtain an access token using MSAL ConfidentialClientApplication.
        Raises:
            AccessTokenError: If token acquisition fails.
        """
        result = self.msal_app.acquire_token_for_client(scopes=[self.POWERBI_SCOPE])
        if "access_token" in result:
            self.access_token = result["access_token"]
            return self.access_token
        else:
            raise AccessTokenError(
                f"Could not obtain access token. Error: {result.get('error_description', 'Unknown error')}"
            )

    def _handle_api_error(self, response: requests.Response, operation: str):
        """Handle API errors and refresh token if needed"""
        if response.status_code == 401:  # Unauthorized - token might be expired
            logging.info("Access token expired, attempting to refresh...")
            self.get_access_token()
            # Return True to indicate retry is needed
            return True
        elif response.status_code != 200:
            raise RefreshError(
                f"Failed to {operation}: {response.status_code} - {response.text}"
            )
        return False

    def get_model_refresh_status(
        self, workspace_id: str, semantic_model_id: str, refresh_request_id: str
    ) -> str:
        """
        Retrieve the current status of the refresh operation.
        """
        max_retries = 2
        for attempt in range(max_retries):
            url = (
                f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/"
                f"{semantic_model_id}/refreshes?$top=3"
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }

            try:
                response = requests.get(url, headers=headers)
                if self._handle_api_error(response, "get refresh status"):
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise RefreshError("Max retries exceeded for token refresh")

                body = response.json()
                for r in body.get("value", []):
                    if r.get("requestId") == refresh_request_id:
                        return r.get("status")
                return "Error Finding Request"

            except requests.exceptions.RequestException as e:
                raise RefreshError(f"Network error while getting refresh status: {e}")

    def refresh_model(
        self,
        workspace_id: str,
        semantic_model_id: str,
        refresh_type: str = "Full",
        wait_for_completion: bool = False,
        tables: list = None,
    ) -> str:
        """
        Request a model refresh for a dataset.
        Raises:
            RefreshError: If the refresh request fails.
        """
        END_STATUSES = ["Failed", "Completed"]
        valid_refresh_types = [
            "Automatic",
            "Calculate",
            "ClearValues",
            "DataOnly",
            "Defragment",
            "Full",
        ]

        if refresh_type not in valid_refresh_types:
            raise RefreshError(f"Invalid refresh type: {refresh_type}")

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{semantic_model_id}/refreshes"
        body = {"type": refresh_type}
        if tables:
            body["objects"] = [{"table": t} for t in tables]

        max_retries = 2
        for attempt in range(max_retries):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }

            try:
                response = requests.post(url, headers=headers, json=body)
                if response.status_code == 401 and attempt < max_retries - 1:
                    logging.info("Access token expired, refreshing...")
                    self.get_access_token()
                    continue

                if response.status_code != 202:
                    raise RefreshError(
                        f"Failed to request model refresh: {response.status_code} - {response.text}"
                    )

                refresh_request_id = response.headers.get("RequestId")
                logging.info(
                    f"Model refresh requested successfully: {refresh_request_id}"
                )

                if wait_for_completion:
                    while True:
                        try:
                            status = self.get_model_refresh_status(
                                workspace_id, semantic_model_id, refresh_request_id
                            )
                            if status in END_STATUSES:
                                logging.info(f"Refresh completed with status: {status}")
                                return status
                            logging.info(
                                f"Current status: {status}. Waiting for completion..."
                            )
                            time.sleep(60)
                        except AccessTokenError:
                            logging.info(
                                "Token expired during status check, refreshing..."
                            )
                            self.get_access_token()
                else:
                    return refresh_request_id

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Request failed, retrying: {e}")
                    continue
                raise RefreshError(f"Network error during refresh request: {e}")

        raise RefreshError("Max retries exceeded for refresh request")
