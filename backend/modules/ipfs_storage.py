# modules/ipfs_storage.py
import ipfshttpclient
import os

class IPFSManager:
    def __init__(self):
        # Get IPFS connection details
        ipfs_host = os.getenv('IPFS_HOST', 'localhost')
        ipfs_port = int(os.getenv('IPFS_PORT', '5001'))
        
        try:
            # Connect to IPFS - fix the connection string format
            if ipfs_host == 'ipfs':  # Docker service name
                # When running in Docker, use service name
                connection_string = f'/dns/{ipfs_host}/tcp/{ipfs_port}/http'
            else:
                # When running locally
                connection_string = f'/ip4/127.0.0.1/tcp/{ipfs_port}/http'
            
            print(f"Connecting to IPFS: {connection_string}")
            self.client = ipfshttpclient.connect(connection_string)
            
            # Test connection
            version = self.client.version()
            print(f"✓ Connected to IPFS at {ipfs_host}:{ipfs_port}")
            print(f"✓ IPFS Version: {version['Version']}")
            
        except Exception as e:
            raise Exception(f"Failed to connect to IPFS: {str(e)}")
    
    def upload(self, data):
        """
        Upload data to IPFS
        Args:
            data: bytes - The data to upload
        Returns:
            str - CID (Content Identifier)
        """
        try:
            result = self.client.add_bytes(data)
            print(f"✓ Uploaded to IPFS: {result}")
            return result
        except Exception as e:
            raise Exception(f"Failed to upload to IPFS: {str(e)}")
    
    def download(self, cid):
        """
        Download data from IPFS using CID
        Args:
            cid: str - Content Identifier
        Returns:
            bytes - The downloaded data
        """
        try:
            data = self.client.cat(cid)
            print(f"✓ Downloaded from IPFS: {cid}")
            return data
        except Exception as e:
            raise Exception(f"Failed to download from IPFS: {str(e)}")
    
    def pin(self, cid):
        """Pin CID to ensure persistence"""
        try:
            self.client.pin.add(cid)
            print(f"✓ Pinned CID: {cid}")
        except Exception as e:
            print(f"Warning: Failed to pin {cid}: {str(e)}")
    
    def unpin(self, cid):
        """Unpin CID"""
        try:
            self.client.pin.rm(cid)
            print(f"✓ Unpinned CID: {cid}")
        except Exception as e:
            print(f"Warning: Failed to unpin {cid}: {str(e)}")
    
    def get_file_info(self, cid):
        """Get information about a file"""
        try:
            stat = self.client.object.stat(cid)
            return {
                'cid': cid,
                'size': stat['CumulativeSize'],
                'num_links': stat['NumLinks']
            }
        except Exception as e:
            raise Exception(f"Failed to get file info: {str(e)}")
