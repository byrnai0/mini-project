// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileSharing {
    // User structure
    struct User {
        string bcid;           // Blockchain ID
        string publicKey;      // User's public key
        bool isRegistered;
        uint256 timestamp;
    }
    
    // File metadata structure
    struct FileMetadata {
        string cid;            // IPFS Content ID
        string owner;          // File owner's BCID
        string encryptedKey;   // ABE encrypted key
        string accessPolicy;   // Attribute policy (JSON)
        uint256 timestamp;
        bool isActive;
    }
    
    // Mappings
    mapping(address => User) public users;
    mapping(string => FileMetadata) public files;
    
    // Events
    event UserRegistered(address indexed userAddress, string bcid, uint256 timestamp);
    event FileShared(string indexed cid, string owner, uint256 timestamp);
    event FileAccessed(string indexed cid, address indexed accessor, uint256 timestamp);
    
    // Register new user
    function registerUser(string memory _bcid, string memory _publicKey) public {
        require(!users[msg.sender].isRegistered, "User already registered");
        
        users[msg.sender] = User({
            bcid: _bcid,
            publicKey: _publicKey,
            isRegistered: true,
            timestamp: block.timestamp
        });
        
        emit UserRegistered(msg.sender, _bcid, block.timestamp);
    }
    
    // Store file metadata
    function shareFile(
        string memory _cid,
        string memory _encryptedKey,
        string memory _accessPolicy
    ) public {
        require(users[msg.sender].isRegistered, "User not registered");
        require(bytes(files[_cid].cid).length == 0, "File already exists");
        
        files[_cid] = FileMetadata({
            cid: _cid,
            owner: users[msg.sender].bcid,
            encryptedKey: _encryptedKey,
            accessPolicy: _accessPolicy,
            timestamp: block.timestamp,
            isActive: true
        });
        
        emit FileShared(_cid, users[msg.sender].bcid, block.timestamp);
    }
    
    // Get file metadata
    function getFileMetadata(string memory _cid) public view returns (
        string memory owner,
        string memory encryptedKey,
        string memory accessPolicy,
        uint256 timestamp
    ) {
        require(files[_cid].isActive, "File not found or inactive");
        
        FileMetadata memory file = files[_cid];
        return (file.owner, file.encryptedKey, file.accessPolicy, file.timestamp);
    }
    
    // Log file access (for audit trail)
    function logFileAccess(string memory _cid) public {
        require(files[_cid].isActive, "File not found");
        emit FileAccessed(_cid, msg.sender, block.timestamp);
    }
    
    // Check if user is registered
    function isUserRegistered(address _user) public view returns (bool) {
        return users[_user].isRegistered;
    }
    
    // Get user BCID
    function getUserBCID(address _user) public view returns (string memory) {
        require(users[_user].isRegistered, "User not registered");
        return users[_user].bcid;
    }
}
