"""Polygon Amoy ContentRegistry client using Web3.py."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from web3 import Web3
from web3.exceptions import Web3Exception


class BlockchainError(RuntimeError):
    pass


class ContentRegistryClient:
    def __init__(self, contract_file: str | Path = "data/results/contract.json") -> None:
        rpc = os.getenv("POLYGON_RPC_URL", "https://rpc-amoy.polygon.technology/").strip()
        private_key = os.getenv("PRIVATE_KEY", "").strip()
        if not private_key:
            raise BlockchainError("PRIVATE_KEY is not configured.")
        self.w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))
        if not self.w3.is_connected():
            raise BlockchainError("Could not connect to Polygon Amoy RPC.")
        data = json.loads(Path(contract_file).read_text(encoding="utf-8"))
        address = os.getenv("CONTRACT_ADDRESS", data.get("contract_address", "")).strip()
        if not address:
            raise BlockchainError("CONTRACT_ADDRESS is not configured.")
        self.account = self.w3.eth.account.from_key(private_key)
        self.contract = self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=data["abi"])

    @staticmethod
    def _bytes32(hex_digest: str) -> bytes:
        if len(hex_digest) != 64:
            raise BlockchainError("Fingerprint must be 64 hexadecimal characters.")
        try:
            return bytes.fromhex(hex_digest)
        except ValueError as exc:
            raise BlockchainError("Fingerprint is not valid hexadecimal.") from exc

    def register(self, fingerprint: str) -> str:
        key = self._bytes32(fingerprint)
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = self.contract.functions.registerContent(key).build_transaction({
            "from": self.account.address, "nonce": nonce,
            "chainId": 80002, "gas": 180000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.status != 1:
            raise BlockchainError("Blockchain transaction reverted.")
        return tx_hash.hex()

    def verify(self, fingerprint: str) -> dict[str, Any]:
        record = self.contract.functions.verifyContent(self._bytes32(fingerprint)).call()
        exists, timestamp, submitter = record
        return {"exists": bool(exists), "timestamp": int(timestamp), "submitter": submitter}
