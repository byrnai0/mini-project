from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

def deploy_contract():
    print("\n=== Deploying Smart Contract ===\n")
    
    # Install Solidity compiler
    print("1. Installing Solidity compiler...")
    install_solc('0.8.0')
    print("   ✓ Solidity 0.8.0 installed")
    
    # Connect to Ganache
    print("\n2. Connecting to Ganache...")
    ganache_url = os.getenv('GANACHE_URL', 'http://localhost:8545')
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not w3.is_connected():
        print("   ✗ Failed to connect to Ganache")
        return False
    
    print(f"   ✓ Connected to Ganache at {ganache_url}")
    
    # Get default account
    default_account = w3.eth.accounts[0]
    print(f"   ✓ Using account: {default_account}")
    print(f"   ✓ Balance: {w3.from_wei(w3.eth.get_balance(default_account), 'ether')} ETH")
    
    # Read Solidity contract
    print("\n3. Reading smart contract...")
    with open('contracts/FileSharing.sol', 'r') as file:
        contract_source_code = file.read()
    print("   ✓ Contract source loaded")
    
    # Compile the contract
    print("\n4. Compiling contract...")
    try:
        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {"FileSharing.sol": {"content": contract_source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                },
            },
            solc_version="0.8.0",
        )
        print("   ✓ Contract compiled successfully")
    except Exception as e:
        print(f"   ✗ Compilation failed: {e}")
        return False
    
    # Get bytecode and ABI
    bytecode = compiled_sol['contracts']['FileSharing.sol']['FileSharing']['evm']['bytecode']['object']
    abi = compiled_sol['contracts']['FileSharing.sol']['FileSharing']['abi']
    
    # Save ABI
    os.makedirs('contracts', exist_ok=True)
    with open('contracts/FileSharing_ABI.json', 'w') as f:
        json.dump(abi, f, indent=2)
    print("   ✓ ABI saved to contracts/FileSharing_ABI.json")
    
    # Deploy contract
    print("\n5. Deploying contract...")
    FileSharing = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build transaction
    tx_hash = FileSharing.constructor().transact({
        'from': default_account,
        'gas': 3000000
    })
    
    print(f"   ✓ Transaction sent: {tx_hash.hex()}")
    print("   ⏳ Waiting for transaction receipt...")
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    
    print(f"   ✓ Contract deployed successfully!")
    print(f"   📍 Contract Address: {contract_address}")
    print(f"   ⛽ Gas Used: {tx_receipt.gasUsed}")
    
    # Save contract configuration
    config = {
        'contract_address': contract_address,
        'deployer_address': default_account,
        'deployment_tx': tx_hash.hex(),
        'network': 'ganache-local',
        'deployed_at': str(tx_receipt.blockNumber)
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("   ✓ Configuration saved to config.json")
    
    print("\n✅ Deployment Complete!\n")
    return True

if __name__ == '__main__':
    success = deploy_contract()
    exit(0 if success else 1)
