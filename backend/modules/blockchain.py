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
        """
        Get file metadata from blockchain
        Returns: dict with file info or None
        """
        try:
            # Call view function - no transaction needed
            result = self.contract.functions.getFileMetadata(cid).call()
            
            # Unpack the tuple returned by Solidity
            # Returns: (owner, cid, accessPolicy, timestamp, isActive)
            if result and result[0] != '0x0000000000000000000000000000000000000000':
                return {
                    'owner': result[0],
                    'cid': result[1],
                    'access_policy': result[2],
                    'timestamp': result[3],
                    'is_active': result[4]
                }
            return None
            
        except Exception as e:
            print(f"Error getting file metadata: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def check_file_access(self, cid, user_address):
        """
        Check if user has access to file
        Returns: bool
        """
        try:
            # Check if file exists first
            metadata = self.get_file_metadata(cid)
            if not metadata:
                print(f"File {cid} not found on blockchain")
                return False
            
            # Check if user is owner
            if metadata['owner'].lower() == user_address.lower():
                print(f"User {user_address} is the owner")
                return True
            
            # For now, just check if file is active
            # In production, you'd check access policy here
            return metadata['is_active']
            
        except Exception as e:
            print(f"Error checking file access: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


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
