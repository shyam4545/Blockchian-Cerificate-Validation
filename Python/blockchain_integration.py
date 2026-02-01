import os
import json
import hashlib
import requests
from web3 import Web3
from dotenv import load_dotenv
import logging

load_dotenv()

class BlockchainIntegration:
    def __init__(self):
        self.setup_logging()
        self.setup_web3()
        self.setup_ipfs()
        self.load_contract()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def setup_web3(self):
        """Initialize Web3 connection"""
        self.rpc_url = os.getenv('RPC_URL', 'http://127.0.0.1:7545')
        self.private_key = os.getenv('PRIVATE_KEY')
        
        if not self.private_key:
            raise ValueError("PRIVATE_KEY not found in environment variables")
        
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.web3.is_connected():
            raise ConnectionError("Cannot connect to Ethereum network")
        
        self.account = self.web3.eth.account.from_key(self.private_key)
        self.logger.info(f"Connected to blockchain. Account: {self.account.address}")
    
    def setup_ipfs(self):
        """Setup IPFS configuration"""
        self.pinata_api_key = os.getenv('PINATA_API_KEY')
        self.pinata_secret = os.getenv('PINATA_SECRET')
        
        if not all([self.pinata_api_key, self.pinata_secret]):
            self.logger.warning("Pinata credentials not found. IPFS upload will be disabled.")
    
    def load_contract(self):
        """Load the deployed contract"""
        contract_address = os.getenv('CONTRACT_ADDRESS')
        
        if not contract_address:
            raise ValueError("CONTRACT_ADDRESS not found in environment variables")
        
        # Load contract ABI from truffle build
        try:
            with open('build/contracts/DataWipingCertificate.json', 'r') as f:
                contract_json = json.load(f)
                self.contract_abi = contract_json['abi']
        except FileNotFoundError:
            # Fallback ABI if truffle build not available
            self.contract_abi = [
                {
                    "inputs": [
                        {"name": "_certificateId", "type": "string"},
                        {"name": "_devicePath", "type": "string"},
                        {"name": "_deviceModel", "type": "string"},
                        {"name": "_deviceSerial", "type": "string"},
                        {"name": "_wipeMethod", "type": "string"},
                        {"name": "_timestamp", "type": "string"},
                        {"name": "_systemHostname", "type": "string"},
                        {"name": "_toolVersion", "type": "string"},
                        {"name": "_logHash", "type": "string"},
                        {"name": "_ipfsHash", "type": "string"}
                    ],
                    "name": "issueCertificate",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "_certificateId", "type": "string"}],
                    "name": "verifyCertificate",
                    "outputs": [
                        {"name": "exists", "type": "bool"},
                        {"name": "isValid", "type": "bool"},
                        {"name": "deviceSerial", "type": "string"},
                        {"name": "wipeMethod", "type": "string"},
                        {"name": "timestamp", "type": "string"},
                        {"name": "ipfsHash", "type": "string"},
                        {"name": "issuer", "type": "address"},
                        {"name": "createdAt", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "_certificateId", "type": "string"}],
                    "name": "getCertificateDetails",
                    "outputs": [
                        {
                            "components": [
                                {"name": "certificateId", "type": "string"},
                                {"name": "devicePath", "type": "string"},
                                {"name": "deviceModel", "type": "string"},
                                {"name": "deviceSerial", "type": "string"},
                                {"name": "wipeMethod", "type": "string"},
                                {"name": "timestamp", "type": "string"},
                                {"name": "systemHostname", "type": "string"},
                                {"name": "toolVersion", "type": "string"},
                                {"name": "logHash", "type": "string"},
                                {"name": "ipfsHash", "type": "string"},
                                {"name": "issuer", "type": "address"},
                                {"name": "createdAt", "type": "uint256"},
                                {"name": "isValid", "type": "bool"}
                            ],
                            "name": "",
                            "type": "tuple"
                        }
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
        
        self.contract = self.web3.eth.contract(
            address=contract_address,
            abi=self.contract_abi
        )
        self.logger.info(f"Contract loaded at: {contract_address}")
    
    def upload_to_ipfs(self, file_path, metadata=None):
        """Upload file to IPFS using Pinata"""
        if not all([self.pinata_api_key, self.pinata_secret]):
            self.logger.error("Pinata credentials not configured")
            return None
        
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            'pinata_api_key': self.pinata_api_key,
            'pinata_secret_api_key': self.pinata_secret
        }
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'application/pdf')}
                
                data = {}
                if metadata:
                    data['pinataMetadata'] = json.dumps(metadata)
                    data['pinataOptions'] = json.dumps({'cidVersion': 1})
                
                response = requests.post(url, files=files, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['IpfsHash']
                self.logger.info(f"File uploaded to IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                self.logger.error(f"IPFS upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"IPFS upload error: {e}")
            return None
    
    def calculate_data_hash(self, data):
        """Calculate SHA-256 hash of the data"""
        if isinstance(data, dict):
            data_string = json.dumps(data, sort_keys=True)
        else:
            data_string = str(data)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def estimate_gas_cost(self, function_call):
        """Estimate gas cost for transaction"""
        try:
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            gas_price = self.web3.eth.gas_price
            cost_wei = gas_estimate * gas_price
            cost_eth = self.web3.from_wei(cost_wei, 'ether')
            
            self.logger.info(f"Estimated gas: {gas_estimate}, Cost: {cost_eth} ETH")
            return gas_estimate, cost_eth
        except Exception as e:
            self.logger.error(f"Gas estimation failed: {e}")
            return None, None
    
    def issue_certificate(self, wipe_data, ipfs_hash):
        """Issue certificate on blockchain"""
        try:
            certificate_id = wipe_data.get('certificate_id', '')
            device_details = wipe_data.get('device_details', {})
            system_info = wipe_data.get('system_info', {})
            verification = wipe_data.get('verification', {})
            
            # Prepare function call
            function_call = self.contract.functions.issueCertificate(
                certificate_id,
                device_details.get('path', ''),
                device_details.get('model', ''),
                device_details.get('serial', ''),
                wipe_data.get('wipe_mode', ''),
                wipe_data.get('timestamp_utc', ''),
                system_info.get('hostname', ''),
                wipe_data.get('tool_version', ''),
                verification.get('log_hash_sha256', ''),
                ipfs_hash or ''
            )
            
            # Estimate gas
            gas_estimate, cost_eth = self.estimate_gas_cost(function_call)
            if not gas_estimate:
                raise Exception("Cannot estimate gas cost")
            
            # Check balance
            balance = self.web3.eth.get_balance(self.account.address)
            balance_eth = self.web3.from_wei(balance, 'ether')
            
            if balance_eth < cost_eth:
                raise Exception(f"Insufficient balance. Need {cost_eth} ETH, have {balance_eth} ETH")
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate + 50000,  # Add buffer
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            self.logger.info(f"Certificate issuance transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                self.logger.info(f"Certificate issued successfully. Block: {receipt.blockNumber}")
                return receipt
            else:
                raise Exception("Transaction failed")
                
        except Exception as e:
            self.logger.error(f"Certificate issuance failed: {e}")
            raise
    
    def verify_certificate(self, certificate_id):
        """Verify certificate on blockchain"""
        try:
            result = self.contract.functions.verifyCertificate(certificate_id).call()
            
            return {
                'exists': result[0],
                'is_valid': result[1],
                'device_serial': result[2],
                'wipe_method': result[3],
                'timestamp': result[4],
                'ipfs_hash': result[5],
                'issuer': result[6],
                'created_at': result[7]
            }
        except Exception as e:
            self.logger.error(f"Certificate verification failed: {e}")
            return None
    
    def get_certificate_details(self, certificate_id):
        """Get full certificate details from blockchain"""
        try:
            result = self.contract.functions.getCertificateDetails(certificate_id).call()
            
            return {
                'certificate_id': result[0],
                'device_path': result[1],
                'device_model': result[2],
                'device_serial': result[3],
                'wipe_method': result[4],
                'timestamp': result[5],
                'system_hostname': result[6],
                'tool_version': result[7],
                'log_hash': result[8],
                'ipfs_hash': result[9],
                'issuer': result[10],
                'created_at': result[11],
                'is_valid': result[12]
            }
        except Exception as e:
            self.logger.error(f"Failed to get certificate details: {e}")
            return None