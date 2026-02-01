// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract DataWipingCertificate {
    struct Certificate {
        string certificateId;
        string devicePath;
        string deviceModel;
        string deviceSerial;
        string wipeMethod;
        string timestamp;
        string systemHostname;
        string toolVersion;
        string logHash;
        string ipfsHash;
        address issuer;
        uint256 createdAt;
        bool isValid;
    }
    
    mapping(string => Certificate) public certificates;
    mapping(address => bool) public authorizedIssuers;
    string[] public certificateIds;
    
    address public owner;
    uint256 public totalCertificates;
    
    event CertificateIssued(
        string indexed certificateId,
        string deviceSerial,
        string ipfsHash,
        address indexed issuer,
        uint256 timestamp
    );
    
    event CertificateRevoked(
        string indexed certificateId,
        address indexed revoker,
        uint256 timestamp
    );
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedIssuers[msg.sender] || msg.sender == owner, "Not authorized to issue certificates");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
    }
    
    function issueCertificate(
        string memory _certificateId,
        string memory _devicePath,
        string memory _deviceModel,
        string memory _deviceSerial,
        string memory _wipeMethod,
        string memory _timestamp,
        string memory _systemHostname,
        string memory _toolVersion,
        string memory _logHash,
        string memory _ipfsHash
    ) public onlyAuthorized {
        require(bytes(_certificateId).length > 0, "Certificate ID cannot be empty");
        require(certificates[_certificateId].createdAt == 0, "Certificate already exists");
        
        certificates[_certificateId] = Certificate({
            certificateId: _certificateId,
            devicePath: _devicePath,
            deviceModel: _deviceModel,
            deviceSerial: _deviceSerial,
            wipeMethod: _wipeMethod,
            timestamp: _timestamp,
            systemHostname: _systemHostname,
            toolVersion: _toolVersion,
            logHash: _logHash,
            ipfsHash: _ipfsHash,
            issuer: msg.sender,
            createdAt: block.timestamp,
            isValid: true
        });
        
        certificateIds.push(_certificateId);
        totalCertificates++;
        
        emit CertificateIssued(_certificateId, _deviceSerial, _ipfsHash, msg.sender, block.timestamp);
    }
    
    function verifyCertificate(string memory _certificateId) public view returns (
        bool exists,
        bool isValid,
        string memory deviceSerial,
        string memory wipeMethod,
        string memory timestamp,
        string memory ipfsHash,
        address issuer,
        uint256 createdAt
    ) {
        Certificate memory cert = certificates[_certificateId];
        
        exists = cert.createdAt > 0;
        isValid = cert.isValid;
        deviceSerial = cert.deviceSerial;
        wipeMethod = cert.wipeMethod;
        timestamp = cert.timestamp;
        ipfsHash = cert.ipfsHash;
        issuer = cert.issuer;
        createdAt = cert.createdAt;
    }
    
    function getCertificateDetails(string memory _certificateId) public view returns (Certificate memory) {
        require(certificates[_certificateId].createdAt > 0, "Certificate does not exist");
        return certificates[_certificateId];
    }
    
    function revokeCertificate(string memory _certificateId) public onlyAuthorized {
        require(certificates[_certificateId].createdAt > 0, "Certificate does not exist");
        require(certificates[_certificateId].isValid, "Certificate already revoked");
        
        certificates[_certificateId].isValid = false;
        
        emit CertificateRevoked(_certificateId, msg.sender, block.timestamp);
    }
    
    function authorizeIssuer(address _issuer) public onlyOwner {
        authorizedIssuers[_issuer] = true;
    }
    
    function revokeIssuer(address _issuer) public onlyOwner {
        require(_issuer != owner, "Cannot revoke owner");
        authorizedIssuers[_issuer] = false;
    }
    
    function getAllCertificates() public view returns (string[] memory) {
        return certificateIds;
    }
    
    function getCertificatesByIssuer(address _issuer) public view returns (string[] memory) {
        uint256 count = 0;
        
        // Count certificates by issuer
        for (uint256 i = 0; i < certificateIds.length; i++) {
            if (certificates[certificateIds[i]].issuer == _issuer) {
                count++;
            }
        }
        
        // Create result array
        string[] memory result = new string[](count);
        uint256 index = 0;
        
        for (uint256 i = 0; i < certificateIds.length; i++) {
            if (certificates[certificateIds[i]].issuer == _issuer) {
                result[index] = certificateIds[i];
                index++;
            }
        }
        
        return result;
    }
}