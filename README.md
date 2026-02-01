# Blockchain-Based Certificate Validation System

A decentralized application (DApp) that generates secure, tamper-proof certificates for data sanitization (wiped drives) and records them on the Ethereum blockchain. This project ensures integrity and transparency by storing certificate documents on IPFS and their verification hashes on a local blockchain.

## 🚀 Overview

This system allows users to securely wipe storage devices and automatically generate a **Digital Deletion Certificate** (PDF). The certificate is then:
1.  **Stored on IPFS:** The PDF is uploaded to the InterPlanetary File System (using Pinata) for decentralized storage.
2.  **Verified on Blockchain:** The hash of the certificate and metadata are stored on a local Ethereum blockchain (using Ganache) via a Smart Contract.

This ensures that once a certificate is issued, it cannot be altered or faked.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (for the user interface)
* **Blockchain:** [Ganache](https://trufflesuite.com/ganache/) (Local Ethereum blockchain)
* **Smart Contracts:** Solidity (`CertiWipe` contract)
* **Storage:** IPFS (via [Pinata API](https://www.pinata.cloud/))
* **Backend/Logic:** Python
    * `web3.py` (Ethereum interaction)
    * `reportlab` (PDF generation)
    * `requests` (API calls)

## ✨ Features

* **Secure Data Wiping Simulation:** Simulates industry-standard wiping methods (e.g., NIST Purge).
* **Automatic PDF Generation:** Creates a professional certificate containing the device UUID, timestamp, and wiping method.
* **Decentralized Storage:** Uploads the certificate PDF to IPFS to ensure availability and immutability.
* **Blockchain Verification:** Stores the IPFS hash and certificate details on the Ethereum blockchain.
* **User-Friendly Interface:** Simple web interface built with Streamlit.

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

* **Python 3.8+**
* **Ganache** (Running on port `7545` or `8545`)
* **Pinata Account** (API Key and Secret Key)

## ⚙️ Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/shyam4545/blockchain-certificate-validation.git](https://github.com/shyam4545/blockchain-certificate-validation.git)
    cd blockchain-certificate-validation
    ```

2.  **Install Dependencies**
    Create a `requirements.txt` file or install directly:
    ```bash
    pip install streamlit web3 reportlab requests python-dotenv
    ```

3.  **Configure Environment Variables**
    Create a `.env` file in the root directory to store your sensitive keys:
    ```env
    PINATA_API_KEY=your_pinata_api_key
    PINATA_SECRET_API_KEY=your_pinata_secret_key
    GANACHE_RPC_URL=[http://127.0.0.1:7545](http://127.0.0.1:7545)
    PRIVATE_KEY=your_ganache_wallet_private_key
    CONTRACT_ADDRESS=your_deployed_contract_address
    ```

## 🚀 Usage

1.  **Start Ganache:** Open Ganache and quick start a workspace.
2.  **Deploy Smart Contract:** (If not already done) Deploy your `CertiWipe.sol` contract using Remix or Truffle and update the `CONTRACT_ADDRESS` in your `.env` file.
3.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```
4.  **Interact:**
    * Enter the drive details.
    * Click to "Wipe & Generate Certificate".
    * View the generated IPFS link and Blockchain transaction hash.

## 📂 Project Structure
