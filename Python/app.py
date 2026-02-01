import streamlit as st
from datetime import datetime
from main_certificate_system import DataWipingCertificationSystem
import hashlib
import json

# --- Page Configuration ---
st.set_page_config(page_title="DESTROYER Certification", layout="wide")


def calculate_sha256(file_object):
    sha256_hash = hashlib.sha256()
    file_object.seek(0) # File ko shuruaat se padhna sunishchit karein
    for byte_block in iter(lambda: file_object.read(4096), b""):
        sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@st.cache_resource
def get_cert_system():
    return DataWipingCertificationSystem()

cert_system = get_cert_system()

# --- UI SETUP ---
st.sidebar.image("logo.png", width=100) 
st.sidebar.title("DESTROYER Portal")
page = st.sidebar.radio(
    "Select Your Panel", 
    ["Admin Panel (Issue Certificate)", "User Panel (Verify Certificate)"]
)
st.title("🛡️ Secure Data Wiping Certification Portal")
st.markdown("Blockchain aur IPFS par aadharit ek tamper-proof certification system.")

# ======================================================================================
# ADMIN PANEL (Updated with Tabs)
# ======================================================================================
if page == "Admin Panel (Issue Certificate)":
    st.header("Admin Panel: Issue a New Certificate")
    
    tab1, tab2 = st.tabs(["Manual Generation (Form)", "Automatic Generation (from JSON)"])

    # ------------- TAB 1: MANUAL WORKFLOW -------------
    with tab1:
        st.info("Yahan device ki details bharein aur data wipe ki log file upload karein.")
        with st.form("issue_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Device Information")
                device_serial = st.text_input("Device Serial Number*", "SERIAL123456", key="manual_serial")
                device_model = st.text_input("Device Model*", "Samsung SSD 970 EVO", key="manual_model")
            with col2:
                st.subheader("Wiping Operation Details")
                wipe_method = st.selectbox("Wipe Method*", ["quick", "dod_5220_22_m", "full_wipe"], key="manual_wipe")
                uploaded_log_file = st.file_uploader("Upload Wipe Log File*", type=['txt', 'log'], key="manual_log")

            submitted = st.form_submit_button("Generate & Issue Certificate")

        if submitted:
            if not all([device_serial, device_model, wipe_method, uploaded_log_file]):
                st.error("Please fill all mandatory fields (*) and upload the log file.")
            else:
                log_hash = calculate_sha256(uploaded_log_file)
                st.info(f"Calculated Unique Log Hash: {log_hash}")
                certificate_id = f"cert_{device_serial}_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
                wipe_data = {
                    "device_details": { "serial": device_serial, "model": device_model },
                    "wipe_mode": wipe_method, "timestamp_utc": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
                    "success": True, "system_info": {"hostname": "WebApp-Manual"}, "tool_version": "N/A",
                    "verification": {"log_hash_sha256": log_hash}, "certificate_id": certificate_id, "status": "Success"
                }

                with st.spinner('Processing...'):
                    result = cert_system.process_wipe_data(wipe_data)
                    if result['success']:
                        st.success("Certificate Issued via Manual Form!")
                        st.balloons()
                        st.json(result)
                    else:
                        st.error(f"Certificate Issuance Failed! Error: {result['error']}")

    # ------------- TAB 2: AUTOMATIC WORKFLOW -------------
    with tab2:
        st.info("Yahan core engine se generate hui JSON report file seedha upload karein.")
        uploaded_json_file = st.file_uploader("Upload Wipe Data JSON File", type=['json'])

        if st.button("Process JSON & Issue Certificate"):
            if uploaded_json_file is not None:
                try:
                    # JSON file ko read aur parse karna
                    wipe_data_from_json = json.load(uploaded_json_file)
                    st.write("✅ JSON file read successfully. Issuing certificate with this data:")
                    st.json(wipe_data_from_json)

                    with st.spinner('Processing JSON... Issuing certificate...'):
                        result = cert_system.process_wipe_data(wipe_data_from_json)
                        if result['success']:
                            st.success("Certificate Issued from JSON file!")
                            st.balloons()
                            st.write("Issuance Result:")
                            st.json(result)
                        else:
                            st.error(f"Certificate Issuance Failed! Error: {result['error']}")

                except Exception as e:
                    st.error(f"JSON file process karne mein error aaya: {e}")
            else:
                st.warning("Please upload a JSON file first.")


# ======================================================================================
# USER PANEL (No change)
# ======================================================================================
elif page == "User Panel (Verify Certificate)":
    # User panel ka code bilkul same rahega, usmein koi change nahi hai
    st.header("User Panel: Verify an Existing Certificate")
    st.info("Blockchain se certificate ki details check karne ke liye uski ID yahan daalein.")
    cert_id_to_verify = st.text_input("Enter Certificate ID to Verify")
    if st.button("Verify from Blockchain"):
        if not cert_id_to_verify:
            st.warning("Please enter a Certificate ID.")
        else:
            with st.spinner("Blockchain se data laaya jaa raha hai..."):
                details = cert_system.get_certificate_details(cert_id_to_verify)
                if details['success']:
                    cert_data = details['certificate_details']
                    if cert_data['is_valid']:
                        st.success(f"✅ Certificate '{cert_data['certificate_id']}' is VALID.")
                    else:
                        st.error(f"❌ Certificate '{cert_data['certificate_id']}' has been REVOKED.")
                    st.json(cert_data)
                    if cert_data.get('ipfs_url'):
                        st.markdown(f"**View Certificate on IPFS:** [Click Here]({cert_data['ipfs_url']})")
                else:
                    st.error(f"Verification Failed! Error: {details['error']}")