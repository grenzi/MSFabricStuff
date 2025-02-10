#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from dotenv import load_dotenv
from src.fabric_refresh_manager import FabricRefreshManager, AccessTokenError, RefreshError

def _parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Refresh a Fabric Semantic model using FabricRefreshManager. \n\n"
        "Example usage:\n"
        "python script.py --workspace-id fa6d505a-3513-4ea5-8489-c2db98f7688d "
        "--semantic-model-id b0af9a40-da55-4e2d-83f7-26148f703469 --tables Sales Customers"
    )
    parser.add_argument(
        "--workspace-id",
        required=True,
        help="Workspace ID (Group ID) for the Power BI dataset. "
        "Example: --workspace-id fa6d505a-3513-4ea5-8489-c2db98f7688d",
    )
    parser.add_argument(
        "--semantic-model-id",
        required=True,
        help="Semantic Model ID (Dataset ID) for the Power BI dataset. "
        "Example: --semantic-model-id b0af9a40-da55-4e2d-83f7-26148f703469",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        help="Optional list of tables to refresh. "
        "Example: --tables Sales Customers Products",
    )
    parser.add_argument(
        "--refresh-type",
        default="Full",
        choices=[
            "Automatic",
            "Calculate",
            "ClearValues",
            "DataOnly",
            "Defragment",
            "Full",
        ],
        help="Type of refresh to perform. Default is 'Full'.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for the refresh operation to complete.",
    )
    return parser.parse_args()

def get_creds_from_keyvault():
    return  None, None, None

def get_creds_from_environment():
    # Retrieve credentials from environment variables
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("WORKSPACE_APPID")
    client_secret = os.getenv("WORKSPACE_SECRET")

    if not tenant_id or not client_id or not client_secret:
        logging.error(
            "Missing environment variables: TENANT_ID, WORKSPACE_APPID, and WORKSPACE_SECRET are required."
        )
        sys.exit(1)

    return tenant_id, client_id, client_secret

def main():
    load_dotenv()
    # Configure logging to include date and time
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    args = _parse_args()

    # Retrieve credentials 
    tenant_id, client_id, client_secret = get_creds_from_environment()
    # tenant_id, client_id, client_secret = get_creds_from_keyvault()

    # Instantiate the FabricRefreshManager and obtain an access token.
    refresh_manager = FabricRefreshManager(tenant_id, client_id, client_secret)
    try:
        refresh_manager.get_access_token()
    except AccessTokenError as e:
        logging.error(f"Error obtaining access token: {e}")
        sys.exit(1)

    # Attempt to request a model refresh.
    try:
        result = refresh_manager.refresh_model(
            workspace_id=args.workspace_id,
            semantic_model_id=args.semantic_model_id,
            refresh_type=args.refresh_type,
            wait_for_completion=args.wait,
            tables=args.tables,
        )
        logging.info(f"Refresh operation result: {result}")
    except RefreshError as e:
        logging.error(f"Error refreshing model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
