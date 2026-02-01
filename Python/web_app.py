from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from main_certificate_system import DataWipingCertificationSystem
import json

app = Flask(__name__)
cert_system = DataWipingCertificationSystem()

# HTML Template for verification portal
VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Wiping Certificate Verification Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: auto; 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }
        .header h1 { 
            color: #333; 
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .header p { 
            color: #666; 
            font-size: 1.1em;
        }
        .verification-section {
            background: #f8f9ff;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #333;
        }
        input[type="text"] { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover { 
            transform: translateY(-2px);
        }
        .result { 
            margin-top: 30px; 
            padding: 20px; 
            border-radius: 8px;
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb;
        }
        .certificate-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .detail-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .detail-card h3 {
            color: #333;
            margin-bottom: 10px;
        }
        .detail-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .detail-label {
            font-weight: bold;
            color: #555;
        }
        .detail-value {
            color: #333;
            word-break: break-all;
        }
        .links {
            margin-top: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .link-btn {
            padding: 8px 16px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }
        .link-btn:hover {
            background: #218838;
        }
        .smart-india-badge {
            background: linear-gradient(45deg, #ff6b6b, #ffd93d);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-align: center;
            font-weight: bold;
            margin: 20px 0;
        }
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Certificate Verification Portal</h1>
            <p>Secure IT Asset Data Wiping Certification System</p>
            <div class="smart-india-badge">
                🏆 Smart India Hackathon 2024 Project
            </div>
        </div>
        
        <div class="verification-section">
            <h2>Verify Certificate</h2>
            <form id="verifyForm">
                <div class="form-group">
                    <label for="certificateId">Certificate ID:</label>
                    <input type="text" id="certificateId" name="certificateId" 
                           placeholder="Enter certificate ID (e.g., certificate__dev_sdd_20250922T123311Z)" required>
                </div>
                <button type="submit" class="btn">Verify Certificate</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Verifying certificate on blockchain...</p>
            </div>
            
            <div id="result"></div>
        </div>
        
        <div class="verification-section">
            <h2>About This System</h2>
            <p>This verification portal validates data sanitization certificates stored on the Ethereum blockchain. 
            Each certificate represents a completed secure data wiping operation and contains cryptographic proof 
            of the sanitization process.</p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li>Certificates are immutably stored on blockchain</li>
                <li>PDF certificates are stored on IPFS for permanent access</li>
                <li>Cryptographic hashing ensures data integrity</li>
                <li>Smart contracts provide transparent verification</li>
            </ul>
        </div>
    </div>

    <script>
        document.getElementById('verifyForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const certificateId = document.getElementById('certificateId').value;
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            
            // Show loading
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch(`/api/verify/${encodeURIComponent(certificateId)}`);
                const result = await response.json();
                
                loadingDiv.style.display = 'none';
                
                if (result.valid) {
                    resultDiv.innerHTML = `
                        <div class="result success">
                            <h3>✅ Certificate Verified Successfully!</h3>
                            <div class="certificate-details">
                                <div class="detail-card">
                                    <h3>Basic Information</h3>
                                    <div class="detail-item">
                                        <span class="detail-label">Certificate ID:</span>
                                        <span class="detail-value">${certificateId}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Device Serial:</span>
                                        <span class="detail-value">${result.verification_result.device_serial}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Wipe Method:</span>
                                        <span class="detail-value">${result.verification_result.wipe_method}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Timestamp:</span>
                                        <span class="detail-value">${result.verification_result.timestamp}</span>
                                    </div>
                                </div>
                                <div class="detail-card">
                                    <h3>Blockchain Information</h3>
                                    <div class="detail-item">
                                        <span class="detail-label">Issuer Address:</span>
                                        <span class="detail-value">${result.verification_result.issuer}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Block Timestamp:</span>
                                        <span class="detail-value">${new Date(result.verification_result.created_at * 1000).toLocaleString()}</span>
                                    </div>
                                    <div class="detail-item">
                                        <span class="detail-label">Status:</span>
                                        <span class="detail-value">${result.verification_result.is_valid ? 'Active' : 'Revoked'}</span>
                                    </div>
                                </div>
                            </div>
                            ${result.verification_result.ipfs_hash ? `
                                <div class="links">
                                    <a href="https://gateway.pinata.cloud/ipfs/${result.verification_result.ipfs_hash}" 
                                       target="_blank" class="link-btn">📄 View Certificate PDF</a>
                                    <a href="/api/details/${certificateId}" target="_blank" class="link-btn">🔍 Full Details</a>
                                </div>
                            ` : ''}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ Certificate Not Found</h3>
                            <p><strong>Certificate ID:</strong> ${certificateId}</p>
                            <p><strong>Error:</strong> ${result.error || 'This certificate does not exist on the blockchain or is invalid.'}</p>
                            <p><strong>Verified At:</strong> ${result.verified_at}</p>
                            <p>Please check the certificate ID and try again. Make sure you've entered the complete certificate ID exactly as provided.</p>
                        </div>
                    `;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                resultDiv.innerHTML = `
                    <div class="result error">
                        <h3>❌ Verification Error</h3>
                        <p><strong>Error:</strong> ${error.message}</p>
                        <p>Please try again. If the problem persists, contact support.</p>
                    </div>
                `;
            }
        });
        
        // Auto-fill if certificate ID is in URL
        const urlParams = new URLSearchParams(window.location.search);
        const certId = urlParams.get('cert');
        if (certId) {
            document.getElementById('certificateId').value = certId;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(VERIFICATION_TEMPLATE)

@app.route('/verify/<certificate_id>')
def verify_page(certificate_id):
    """Direct verification page with pre-filled certificate ID"""
    template = VERIFICATION_TEMPLATE.replace(
        'placeholder="Enter certificate ID', 
        f'value="{certificate_id}" placeholder="Enter certificate ID'
    )
    return render_template_string(template)

@app.route('/api/verify/<certificate_id>')
def api_verify_certificate(certificate_id):
    """API endpoint to verify certificate"""
    try:
        result = cert_system.verify_certificate(certificate_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'certificate_id': certificate_id
        }), 500

@app.route('/api/details/<certificate_id>')
def api_certificate_details(certificate_id):
    """API endpoint to get full certificate details"""
    try:
        result = cert_system.get_certificate_details(certificate_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'certificate_id': certificate_id
        }), 500

@app.route('/api/issue', methods=['POST'])
def api_issue_certificate():
    """API endpoint to issue new certificate"""
    try:
        wipe_data = request.get_json()
        
        if not wipe_data:
            return jsonify({
                'success': False,
                'error': 'No wipe data provided'
            }), 400
        
        result = cert_system.process_wipe_data(wipe_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🌐 Starting Certificate Verification Portal...")
    print("🌐 Access the portal at: http://localhost:5000")
    print("🌐 API endpoints:")
    print("   - GET  /api/verify/<certificate_id>  : Verify certificate")
    print("   - GET  /api/details/<certificate_id> : Get certificate details") 
    print("   - POST /api/issue                    : Issue new certificate")
    
    app.run(debug=True, host='0.0.0.0', port=5000)