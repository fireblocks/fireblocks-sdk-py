import logging
from time import sleep

from fireblocks_sdk import FireblocksSDK, TransferPeerPath, TRANSACTION_STATUS_CONFIRMED, TRANSACTION_STATUS_CANCELLED, TRANSACTION_STATUS_REJECTED, TRANSACTION_STATUS_FAILED, VAULT_ACCOUNT, TRANSACTION_MINT, TRANSACTION_BURN

logging.basicConfig(level=logging.INFO, format="%(asctime)s::%(levelname)s::%(message)s")

private_key = open('api-client.key', 'r').read()
client = FireblocksSDK(private_key, "e4b761cc-3e31-4413-b7f5-feccf281454e", "https://api.csd.fireblocks.io")




def wait_for_transaction_confirmation(txid):
    tx = client.get_transaction_by_id(txid)
    while tx['status'] not in (TRANSACTION_STATUS_CONFIRMED, TRANSACTION_STATUS_CANCELLED, TRANSACTION_STATUS_REJECTED, TRANSACTION_STATUS_FAILED):
        logging.info(f"Transaction still in status {tx['status']}")
        sleep(5)
        tx = client.get_transaction_by_id(txid)

    logging.info(f"Transaction status is now {tx['status']}")
        
def mint_to_vault(vault_account, secondary_vault_account):
    mint_tx_result = client.create_transaction(
        asset_id="TTTT",
        amount=50,
        source=TransferPeerPath(VAULT_ACCOUNT, vault_account["id"]),
        destination=TransferPeerPath(VAULT_ACCOUNT, secondary_vault_account["id"]),
        tx_type=TRANSACTION_MINT
    )

    logging.info(f"Mint tx creation result: {mint_tx_result}")
    assert mint_tx_result["status"] == "SUBMITTED", mint_tx_result
    wait_for_transaction_confirmation(mint_tx_result["id"])

def transfer_from_secondary(vault_account, secondary_vault_account):
    tx_result = client.create_transaction(
        asset_id="TTTT",
        amount=50,
        source=TransferPeerPath(VAULT_ACCOUNT, secondary_vault_account["id"]),
        destination=TransferPeerPath(VAULT_ACCOUNT, vault_account["id"]),
    )

    logging.info(f"Transfer tx creation result: {tx_result}")
    assert tx_result["status"] == "SUBMITTED", tx_result
    wait_for_transaction_confirmation(tx_result["id"])
        
def burn_from_vault(vault_account):
    burn_tx_result = client.create_transaction(
        asset_id="TTTT",
        amount=50,
        source=TransferPeerPath(VAULT_ACCOUNT, vault_account["id"]),
        tx_type=TRANSACTION_BURN
    )

    logging.info(f"Burn tx creation result: {burn_tx_result}")
    assert burn_tx_result["status"] == "SUBMITTED", burn_tx_result
    wait_for_transaction_confirmation(burn_tx_result["id"])

def get_balances(vault_account, secondary_vault_account):
    main_balance = client.get_vault_account_asset(vault_account["id"], "TTTT")
    logging.info(f"Main balance: {main_balance}")
    secondary_balance = client.get_vault_account_asset(secondary_vault_account["id"], "TTTT")
    logging.info(f"Secondary balance: {secondary_balance}")

def main():
    vault_account = client.get_vault_account("0")
    secondary_vault_account = client.get_vault_account("1")

    get_balances(vault_account, secondary_vault_account)    

    mint_to_vault(vault_account, secondary_vault_account)

    get_balances(vault_account, secondary_vault_account)

    transfer_from_secondary(vault_account, secondary_vault_account)

    get_balances(vault_account, secondary_vault_account)

    burn_from_vault(vault_account)

    get_balances(vault_account, secondary_vault_account)


main()