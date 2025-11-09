from web3 import Web3
import json
import os

class BlockchainManager:
    def __init__(self):
        # Connect to Ganache
        ganache_url = os.getenv('GANACHE_URL', 'http://localhost:8545')
        self.w3 = Web3(Web3.HTTPProvider(ganache_url))
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ganache")
        
        print(f"✓ Connected to Ganache at {ganache_url}")
        
        # Load contract
        with open('contracts/FileSharing_ABI.json', 'r') as f:
            contract_abi = json.load(f)
        
        with open('config.json', 'r') as f:
            config = json.load(f)
            contract_address = config['contract_address']
        
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
        
        # Default account for transactions
        self.default_account = self.w3.eth.accounts[0]
        print(f"✓ Using account: {self.default_account}")
    
    def register_user(self, bcid, public_key, user_address=None):
        """Register user on blockchain"""
        if user_address is None:
            user_address = self.default_account
        
        tx_hash = self.contract.functions.registerUser(
            bcid,
            public_key
        ).transact({
            'from': user_address,
            'gas': 300000
        })
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex()
    
    def share_file(self, cid, encrypted_key, access_policy, from_address=None):
        """Store file metadata on blockchain"""
        if from_address is None:
            from_address = self.default_account
        
        tx_hash = self.contract.functions.shareFile(
            cid,
            encrypted_key,
            access_policy
        ).transact({
            'from': from_address,
            'gas': 500000
        })
        
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex()
    
    def get_file_metadata(self, cid):
        """Retrieve file metadata from blockchain"""
        try:
            metadata = self.contract.functions.getFileMetadata(cid).call()
            return {
                'owner': metadata[0],
                'encryptedKey': metadata[1],
                'accessPolicy': metadata[2],
                'timestamp': metadata[3]
            }
        except Exception as e:
            raise Exception(f"File not found: {str(e)}")
    
    def get_user_info(self, address):
        """Get user information from blockchain"""
        try:
            user = self.contract.functions.users(address).call()
            return {
                'bcid': user[0],
                'publicKey': user[1],
                'isRegistered': user[2],
                'timestamp': user[3]
            }
        except Exception as e:
            return None
