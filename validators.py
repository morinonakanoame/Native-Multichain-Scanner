from eth_utils import (
    is_checksum_address,
    is_address,
    is_hex_address
)

from solders.pubkey import Pubkey
from pytoniq_core import Address, AddressError

from typing import Optional

def valid_string_eth(
    data: str
    ) -> Optional[bool]:
    if not isinstance(data, str):
        return False
    if not is_hex_address(data):
        return False
    if not is_address(data):
        return False
    if not is_checksum_address(data):
        return False
    
    return True

def valid_string_bnb(
    data: str
    ) -> Optional[bool]:
    if not isinstance(data, str):
        return False
    if not is_hex_address(data):
        return False
    if not is_address(data):
        return False
    if not is_checksum_address(data):
        return False
    
    return True

def valid_string_sol(
    data: str
    ) -> Optional[bool]:
    try:
        if not Pubkey.from_string(data):
            return False
    except (TypeError, ValueError):
        return False    
    return True

def valid_string_ton(
    data: str
    ) -> Optional[bool]:
    if not isinstance(data, str):
        return False
    try:
        if not Address(data):
            raise AddressError(
                "Address parsing returned an empty result"
            )
    except (AddressError, TypeError, ValueError):
        return False
    return True
