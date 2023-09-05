import sys
import time
import requests

from raga.exception import RagaException
from raga.validators.test_session_validation import TestSessionValidator
from raga.utils import HTTPClient
from raga.utils import read_raga_config, get_config_value


class ModelExecutorFactoryException(RagaException):
    pass

class ModelExecutorFactory:
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    ACCESS_KEY = "raga_access_key_id"
    SECRET_KEY = "raga_secret_access_key"

    def __init__(self, project_name: str, u_test=False, host=None, config_data=None, access_key=None, secret_key=None):
        if config_data is None and (access_key is None or secret_key is None or host is None):
            config_data = read_raga_config()
        
        self.api_host = host if host else get_config_value(config_data, 'default', 'api_host')
        self.raga_access_key_id = access_key if access_key else get_config_value(config_data, 'default', self.ACCESS_KEY)
        self.raga_secret_access_key = secret_key if secret_key else get_config_value(config_data, 'default', self.SECRET_KEY)

        self.project_name = TestSessionValidator.validate_project_name(project_name)
        self.http_client = HTTPClient(self.api_host)
        self.model_added = False

        self.token = None
        self.project_id = None
        self.experiment_id = None
        if not u_test:
            self.initialize()

    def initialize(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.token = self.create_token()
                self.project_id = self.get_project_id()
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as exception:
                print(f"Network error occurred: {str(exception)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
            except KeyError as exception:
                print(f"Key error occurred: {str(exception)}")
                sys.exit() # No need to retry if a KeyError occurs
            except ValueError as exception:
                print(f"Value error occurred: {str(exception)}")
                sys.exit() # No need to retry if a ValueError occurs
            except Exception as exception:
                print(f"An unexpected error occurred: {str(exception)}")
                sys.exit()  # No need to retry if an unexpected error occurs

    def create_token(self):
        """
        Creates an authentication token by sending a request to the Raga API.

        Returns:
            str: The authentication token.

        Raises:
            KeyError: If the response data does not contain a valid token.
        """
        res_data = self.http_client.post(
            "api/token",
            {"accessKey": self.raga_access_key_id, "secretKey": self.raga_secret_access_key},
        )
        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")
        token = res_data.get("data", {}).get("token")
        if not token:
            raise KeyError("Invalid response data. Token not found.")
        return token


    def get_project_id(self):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/project",
            params={"name": self.project_name},
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        project_id = res_data.get("data", {}).get("id")

        if not project_id:
            raise KeyError("Invalid response data. project ID not found.")
        return project_id
    

    def get_model_id(self, model_name):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/models",
            params={"modelName": model_name, "projectId":self.project_id},
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        model_id = res_data.get("data", {}).get("id")

        if not model_id:
            raise KeyError("Invalid response data. model ID not found.")
        return model_id
    

    def get_version_by_version(self, model_id, version):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/models/version",
            params={
                "modelId": model_id,
                "projectId":self.project_id,
                "version":version
                },
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        model_id = res_data.get("data", {})

        if not model_id:
            raise KeyError("Invalid response data.")
        return model_id
    
    
    def getModelExecutor(self, model_name="", version=""):
        if not isinstance(model_name, str) or not model_name:
            raise ModelExecutorFactoryException("model_name is required and must be a non-empty string.")
        if not isinstance(version, str) or not version:
            raise ModelExecutorFactoryException("version is required and must be a non-empty string.")
        
        model_id = self.get_model_id(model_name=model_name)
        model_version = self.get_version_by_version(model_id=model_id, version=version)
        self.model_added = True

    if not self.added:
            raise ValueError("add() is not called. Call add() before run().")
        


        
        
