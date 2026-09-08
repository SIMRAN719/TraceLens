"""Compile and deploy ContentRegistry to Polygon Amoy."""
from __future__ import annotations
import json, os
from pathlib import Path
from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3

load_dotenv()
rpc, key = os.getenv("POLYGON_RPC_URL"), os.getenv("PRIVATE_KEY")
if not rpc or not key:
    raise SystemExit("Set POLYGON_RPC_URL and PRIVATE_KEY in .env")
w3 = Web3(Web3.HTTPProvider(rpc)); assert w3.is_connected(), "RPC connection failed"
source = Path("contracts/ContentRegistry.sol").read_text(encoding="utf-8")
install_solc("0.8.20")
compiled = compile_standard({"language":"Solidity","sources":{"ContentRegistry.sol":{"content":source}},"settings":{"outputSelection":{"*":{"*":["abi","evm.bytecode"]}}}}, solc_version="0.8.20")
artifact = compiled["contracts"]["ContentRegistry.sol"]["ContentRegistry"]
account = w3.eth.account.from_key(key)
contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["evm"]["bytecode"]["object"])
tx = contract.constructor().build_transaction({"from":account.address,"nonce":w3.eth.get_transaction_count(account.address),"chainId":80002,"gas":2500000,"gasPrice":w3.eth.gas_price})
signed = account.sign_transaction(tx); tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
Path("data/results").mkdir(parents=True, exist_ok=True)
Path("data/results/contract.json").write_text(json.dumps({"network":"polygon-amoy","chain_id":80002,"contract_address":receipt.contractAddress,"abi":artifact["abi"]}, indent=2), encoding="utf-8")
print(receipt.contractAddress)
