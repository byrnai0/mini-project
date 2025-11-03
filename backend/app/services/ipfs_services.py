import ipfshttpclient
from app.config import Config

class IPFSService:
    def __init__(self):
        try:
            self.client = ipfshttpclient.connect(Config.IPFS_HOST)
        except Exception as e:
            print(f"IPFS connection failed: {e}")
            self.client = None
    
    def upload_file(self, file_data: bytes, filename: str) -> str:
        """
        Upload file to IPFS
        Returns: CID (Content Identifier)
        """
        if not self.client:
            raise Exception("IPFS client not connected")
        
        try:
            result = self.client.add_bytes(file_data)
            cid = result
            print(f"File uploaded to IPFS: {cid}")
            return cid
        except Exception as e:
            raise Exception(f"IPFS upload failed: {str(e)}")
    
    def get_file(self, cid: str) -> bytes:
        """
        Retrieve file from IPFS by CID
        """
        if not self.client:
            raise Exception("IPFS client not connected")
        
        try:
            file_data = self.client.cat(cid)
            return file_data
        except Exception as e:
            raise Exception(f"IPFS retrieval failed: {str(e)}")
    
    def pin_file(self, cid: str) -> bool:
        """
        Pin file to ensure it stays in IPFS
        """
        try:
            self.client.pin.add(cid)
            return True
        except Exception as e:
            print(f"Pinning failed: {e}")
            return False
    
    def unpin_file(self, cid: str) -> bool:
        """
        Unpin file from IPFS
        """
        try:
            self.client.pin.rm(cid)
            return True
        except Exception as e:
            print(f"Unpinning failed: {e}")
            return False