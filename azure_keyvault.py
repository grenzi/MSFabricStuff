# %% imports and definitions
import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

VAULT_URL = "https://<<KEYVAULT_URL>>.vault.azure.net/"
JSON_SECRETS_FILE = "secrets_in_json_format.json"
SECRET_KEYS_OUTPUT_FILE = "secret_listing_keys_only.txt"


def get_secret_client(vault_url: str) -> SecretClient:
    credential = DefaultAzureCredential()
    return SecretClient(vault_url=vault_url, credential=credential)


def add_secrets(client: SecretClient, secrets: dict) -> None:
    for key, value in secrets.items():
        print(f"Setting secret {key} in vault")
        client.set_secret(key, value)


def load_dict_to_vault(vault_url: str, secrets: dict) -> None:
    client = get_secret_client(vault_url)
    add_secrets(client, secrets)


def load_secrets_to_vault(vault_url: str, env_path: str) -> None:
    client = get_secret_client(vault_url)
    with open(env_path, "r") as f:
        secrets = json.load(f)
        add_secrets(client, secrets)


def dump_secret_names_to_file(vault_url: str, output_file: str) -> None:
    client = get_secret_client(vault_url)
    with open(output_file, "w") as f:
        for secret_property in client.list_properties_of_secrets():
            f.write(secret_property.name + "\n")


# %% main handler - do what you want here
if __name__ == "__main__":
    my_dict = {
        "key1": "value1",
    }
    load_dict_to_vault(VAULT_URL, my_dict)
    load_secrets_to_vault(VAULT_URL, JSON_SECRETS_FILE)
    dump_secret_names_to_file(VAULT_URL, SECRET_KEYS_OUTPUT_FILE)
