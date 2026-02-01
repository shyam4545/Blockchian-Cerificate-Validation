import os
import json
import logging
from datetime import datetime
from certificate_generator import DataWipingCertificateGenerator
from blockchain_integration import BlockchainIntegration

class DataWipingCertificationSystem:
    def __init__(self):
        self.setup_logging()
        self.generator = DataWipingCertificateGenerator()
        self.blockchain = BlockchainIntegration()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('certificate_system.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def process_wipe_data(self, wipe_data):
        """
        Main function to process wipe data and generate blockchain certificate
        
        Args:
            wipe_data (dict): The wipe operation data from your existing system
            
        Returns:
            dict: Result containing certificate details, transaction hash, IPFS hash, etc.
        """
        try:
            self.logger.info("=== Starting Data Wiping Certification Process ===")
            
            # Validate input data
            if not self.validate_wipe_data(wipe_data):
                raise ValueError("Invalid wipe data provided")
            
            certificate_id = wipe_data.get('certificate_id')
            self.logger.info(f"Processing certificate: {certificate_id}")
            
            # Step 1: Generate professional PDF certificate
            self.logger.info("Generating PDF certificate...")
            pdf_filename = self.generator.generate_certificate(wipe_data)
            
            # Step 2: Upload to IPFS
            self.logger.info("Uploading certificate to IPFS...")
            metadata = {
                'name': f'Data Wiping Certificate - {certificate_id}',
                'description': f'Secure data sanitization certificate for device {wipe_data.get("device_details", {}).get("serial", "unknown")}',
                'certificateId': certificate_id,
                'deviceSerial': wipe_data.get('device_details', {}).get('serial', ''),
                'timestamp': wipe_data.get('timestamp_utc', ''),
                'wipeMethod': wipe_data.get('wipe_mode', ''),
                'toolVersion': wipe_data.get('tool_version', ''),
                'attributes': [
                    {'trait_type': 'Device Type', 'value': wipe_data.get('device_details', {}).get('model', 'Unknown')},
                    {'trait_type': 'Storage Size', 'value': wipe_data.get('device_details', {}).get('size', 'Unknown')},
                    {'trait_type': 'Wipe Method', 'value': wipe_data.get('wipe_mode', 'Unknown')},
                    {'trait_type': 'Status', 'value': wipe_data.get('status', 'Unknown')}
                ]
            }
            
            ipfs_hash = self.blockchain.upload_to_ipfs(pdf_filename, metadata)
            
            if not ipfs_hash:
                self.logger.warning("IPFS upload failed, proceeding without IPFS hash")
                ipfs_hash = ""
            
            # Step 3: Issue certificate on blockchain
            self.logger.info("⛓️ Issuing certificate on blockchain...")
            receipt = self.blockchain.issue_certificate(wipe_data, ipfs_hash)
            
            # Step 4: Clean up temporary files
            if os.path.exists(pdf_filename):
                os.remove(pdf_filename)
                self.logger.info(f"Cleaned up temporary file: {pdf_filename}")
            
            # Step 5: Prepare result
            result = {
                'success': True,
                'certificate_id': certificate_id,
                'transaction_hash': receipt['transactionHash'].hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'ipfs_hash': ipfs_hash,
                'ipfs_url': f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}' if ipfs_hash else None,
                'blockchain_explorer_url': f'https://etherscan.io/tx/{receipt["transactionHash"].hex()}',
                'verification_url': f'https://your-portal.com/verify/{certificate_id}',
                'issued_at': datetime.now().isoformat(),
                'issuer_address': self.blockchain.account.address
            }
            
            self.logger.info("Certificate issuance completed successfully!")
            self.logger.info(f"Certificate ID: {certificate_id}")
            self.logger.info(f"Transaction Hash: {result['transaction_hash']}")
            self.logger.info(f"IPFS Hash: {ipfs_hash}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Certificate processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'certificate_id': wipe_data.get('certificate_id', 'unknown')
            }

    def validate_wipe_data(self, wipe_data):
        """Validate the wipe data structure"""
        required_fields = [
            'certificate_id',
            'device_details',
            'timestamp_utc',
            'success',
            'status'
        ]
        
        for field in required_fields:
            if field not in wipe_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate device details
        device_details = wipe_data.get('device_details', {})
        if not device_details.get('serial'):
            self.logger.error("Device serial number is required")
            return False
        
        # Validate success status
        if not wipe_data.get('success'):
            self.logger.error("Cannot issue certificate for failed wipe operation")
            return False
        
        return True

    def verify_certificate(self, certificate_id):
        """Verify a certificate on the blockchain"""
        try:
            self.logger.info(f"Verifying certificate: {certificate_id}")
            
            verification_result = self.blockchain.verify_certificate(certificate_id)
            
            if verification_result and verification_result['exists']:
                self.logger.info("Certificate verified successfully")
                return {
                    'valid': True,
                    'certificate_id': certificate_id,
                    'verification_result': verification_result,
                    'verified_at': datetime.now().isoformat()
                }
            else:
                self.logger.warning("Certificate not found or invalid")
                return {
                    'valid': False,
                    'certificate_id': certificate_id,
                    'error': 'Certificate not found on blockchain',
                    'verified_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Certificate verification failed: {e}")
            return {
                'valid': False,
                'certificate_id': certificate_id,
                'error': str(e),
                'verified_at': datetime.now().isoformat()
            }

    def get_certificate_details(self, certificate_id):
        """Get detailed certificate information from blockchain"""
        try:
            details = self.blockchain.get_certificate_details(certificate_id)
            
            if details:
                # Enhance with IPFS URL
                if details['ipfs_hash']:
                    details['ipfs_url'] = f'https://gateway.pinata.cloud/ipfs/{details["ipfs_hash"]}'
                
                return {
                    'success': True,
                    'certificate_details': details,
                    'retrieved_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Certificate not found',
                    'certificate_id': certificate_id
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get certificate details: {e}")
            return {
                'success': False,
                'error': str(e),
                'certificate_id': certificate_id
            }

def main():
    """Test the system with your mock data"""
    
    # Your mock data
    mock_wipe_data = {
        "device_details": {
            "name": "sdd",
            "path": "/dev/sdd",
            "size": "1T",
            "mountpoint": None,
            "model": "Virtual Disk",
            "serial": "600224803b424b662e8a9489c86b51f6"
        },
        "wipe_mode": "quick",
        "timestamp_utc": "20250922T123311Z",
        "success": True,
        "system_info": {
            "hostname": "DESKTOP-U6PP1DL",
            "os": "Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39"
        },
        "tool_version": "1.2.0",
        "results": [
            {
                "cmd": "shred -n 1 -z /dev/sdd",
                "returncode": 0,
                "stdout": "[SIMULATED] shred -n 1 -z /dev/sdd",
                "stderr": ""
            }
        ],
        "log_file": "/home/charon/DESTROYER2/DESTROYER/backend/logs/wipe__dev_sdd_20250922T123311Z.log",
        "verification": {
            "log_hash_sha256": "e8147f68425378d399a79985cbe7756b90e73a723b7e8c92af57e5f6fb2092f1"
        },
        "certificate_id": "certificate__dev_sdd_20250922T123311Z_run2",
        "status": "Success"
    }
    
    # Initialize the certification system
    cert_system = DataWipingCertificationSystem()
    
    print("Smart India Hackathon - Data Wiping Certification System")
    print("=" * 60)
    
    # Process the wipe data
    result = cert_system.process_wipe_data(mock_wipe_data)
    
    if result['success']:
        print("\nCERTIFICATE ISSUED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Certificate ID: {result['certificate_id']}")
        print(f"Transaction Hash: {result['transaction_hash']}")
        print(f"Block Number: {result['block_number']}")
        print(f"Gas Used: {result['gas_used']}")
        if result['ipfs_hash']:
            print(f"IPFS Hash: {result['ipfs_hash']}")
            print(f"Certificate URL: {result['ipfs_url']}")
        print(f"Verification URL: {result['verification_url']}")
        print("=" * 60)
        
        # Test verification
        print("\n🔍 Testing certificate verification...")
        verification = cert_system.verify_certificate(result['certificate_id'])
        
        if verification['valid']:
            print("Certificate verification: VALID")
            print(f"Device Serial: {verification['verification_result']['device_serial']}")
            print(f"Wipe Method: {verification['verification_result']['wipe_method']}")
            print(f"Timestamp: {verification['verification_result']['timestamp']}")
        else:
            print("Certificate verification: INVALID")
            print(f"Error: {verification.get('error', 'Unknown error')}")
    
    else:
        print(f"\nCERTIFICATE ISSUANCE FAILED!")
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()