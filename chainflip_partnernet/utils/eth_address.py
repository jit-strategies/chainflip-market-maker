from eth_account import Account
import secrets


def get_new_address() -> str:
    acct = Account.from_key("0x" + secrets.token_hex(32))
    return acct.address
