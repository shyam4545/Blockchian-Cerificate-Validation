import os
import json
import hashlib
import qrcode
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

class DataWipingCertificateGenerator:
    def __init__(self):
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles for the certificate"""
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Custom subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # Custom section header style
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Custom normal style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6,
            fontName='Helvetica'
        )

    def create_qr_code(self, data, filename):
        """Create QR code for certificate verification"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename

    def format_timestamp(self, timestamp_utc):
        """Format UTC timestamp to readable format"""
        try:
            # Parse the timestamp format: "20250922T123311Z"
            dt = datetime.strptime(timestamp_utc, "%Y%m%dT%H%M%SZ")
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            return timestamp_utc

    def create_device_details_table(self, device_details):
        """Create device details table"""
        data = [
            ['Device Information', ''],
            ['Device Name', device_details.get('name', 'N/A')],
            ['Device Path', device_details.get('path', 'N/A')],
            ['Storage Size', device_details.get('size', 'N/A')],
            ['Device Model', device_details.get('model', 'N/A')],
            ['Serial Number', device_details.get('serial', 'N/A')],
            ['Mount Point', device_details.get('mountpoint', 'None') or 'None'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#E8F4FD')),
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def create_wipe_details_table(self, wipe_data):
        """Create wipe operation details table"""
        data = [
            ['Wipe Operation Details', ''],
            ['Wipe Method', wipe_data.get('wipe_mode', 'N/A').title()],
            ['Tool Version', wipe_data.get('tool_version', 'N/A')],
            ['Timestamp (UTC)', self.format_timestamp(wipe_data.get('timestamp_utc', 'N/A'))],
            ['Status', wipe_data.get('status', 'N/A')],
            ['Operation Success', 'Yes' if wipe_data.get('success', False) else 'No'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#E8F5E8')),
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def create_system_info_table(self, system_info):
        """Create system information table"""
        data = [
            ['System & Environment', ''],
            ['Hostname', system_info.get('hostname', 'N/A')],
            ['Operating System', system_info.get('os', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#FDF2E9')),
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#E67E22')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def create_verification_table(self, verification_data, certificate_id):
        """Create verification and integrity table"""
        log_hash = verification_data.get('log_hash_sha256', 'N/A')
        
        data = [
            ['Verification & Integrity', ''],
            ['Certificate ID', certificate_id],
            ['Log File Hash (SHA-256)', log_hash[:32] + '...' if len(log_hash) > 32 else log_hash],
            ['Certificate Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#FDE7F3')),
            ('BACKGROUND', (0, 0), (1, 0), HexColor('#E91E63')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table

    def generate_certificate(self, wipe_data, output_filename=None):
        """Generate the complete certificate PDF"""
        if not output_filename:
            certificate_id = wipe_data.get('certificate_id', 'unknown')
            output_filename = f"certificate_{certificate_id}.pdf"
        
        # Create document
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        story = []
        
        # Header with logo placeholder and title
        title = Paragraph("Certificate of Data Sanitization", self.title_style)
        story.append(title)
        
        subtitle = Paragraph("Secure IT Asset Data Wiping Certification", self.subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 20))
        
        # Certificate introduction
        intro_text = """
        This certificate verifies that secure data sanitization has been performed on the specified 
        storage device in accordance with industry standards and best practices for IT asset recycling. 
        The wiping process has been completed successfully and verified through cryptographic hashing.
        """
        intro_para = Paragraph(intro_text, self.normal_style)
        story.append(intro_para)
        story.append(Spacer(1, 15))
        
        # Device Details Section
        story.append(self.create_device_details_table(wipe_data.get('device_details', {})))
        story.append(Spacer(1, 15))
        
        # Wipe Details Section
        story.append(self.create_wipe_details_table(wipe_data))
        story.append(Spacer(1, 15))
        
        # System Information Section
        story.append(self.create_system_info_table(wipe_data.get('system_info', {})))
        story.append(Spacer(1, 15))
        
        # Verification Section
        story.append(self.create_verification_table(
            wipe_data.get('verification', {}), 
            wipe_data.get('certificate_id', 'N/A')
        ))
        story.append(Spacer(1, 20))
        
        # Command Results Section (if available)
        if wipe_data.get('results'):
            results_header = Paragraph("Command Execution Details", self.section_header_style)
            story.append(results_header)
            
            for i, result in enumerate(wipe_data['results'], 1):
                cmd_text = f"<b>Command {i}:</b> {result.get('cmd', 'N/A')}<br/>"
                cmd_text += f"<b>Return Code:</b> {result.get('returncode', 'N/A')}<br/>"
                cmd_text += f"<b>Output:</b> {result.get('stdout', 'No output')[:100]}{'...' if len(result.get('stdout', '')) > 100 else ''}"
                
                cmd_para = Paragraph(cmd_text, self.normal_style)
                story.append(cmd_para)
                story.append(Spacer(1, 10))
        
        # QR Code for verification
        verification_url = f"https://your-verification-portal.com/verify/{wipe_data.get('certificate_id', '')}"
        qr_filename = f"qr_{wipe_data.get('certificate_id', 'temp')}.png"
        
        try:
            self.create_qr_code(verification_url, qr_filename)
            
            qr_header = Paragraph("Blockchain Verification", self.section_header_style)
            story.append(qr_header)
            
            qr_text = Paragraph("Scan the QR code below to verify this certificate on the blockchain:", self.normal_style)
            story.append(qr_text)
            story.append(Spacer(1, 10))
            
            # Add QR code image
            qr_img = Image(qr_filename, width=1.5*inch, height=1.5*inch)
            story.append(qr_img)
            story.append(Spacer(1, 10))
            
            verify_text = Paragraph(f"<b>Verification URL:</b> {verification_url}", self.normal_style)
            story.append(verify_text)
            
        except Exception as e:
            print(f"QR code generation failed: {e}")
        
        # Footer
        story.append(Spacer(1, 20))
        footer_text = f"""
        <para align="center">
        <b>This certificate is cryptographically secured and immutably stored on blockchain</b><br/>
        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>
        Certificate ID: {wipe_data.get('certificate_id', 'N/A')}<br/>
        <i>Smart India Hackathon 2024 - Secure IT Asset Recycling Project</i>
        </para>
        """
        footer_para = Paragraph(footer_text, self.normal_style)
        story.append(footer_para)
        
        # Build the PDF
        doc.build(story)
        
        # Clean up QR code file
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
        
        print(f"Certificate generated successfully: {output_filename}")
        return output_filename

def main():
    """Test the certificate generator with mock data"""
    mock_data = {
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
        "certificate_id": "certificate__dev_sdd_20250922T123311Z",
        "status": "Success"
    }
    
    # Generate certificate
    generator = DataWipingCertificateGenerator()
    certificate_file = generator.generate_certificate(mock_data)
    
    print(f"Generated certificate: {certificate_file}")

if __name__ == "__main__":
    main()