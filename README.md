# TraceLens

### Face Identification & Blockchain Verification

TraceLens is a digital forensics pipeline that combines **face matching, reverse image search, public web evidence discovery, and blockchain-based integrity verification**.

The system takes a reference image containing a face, searches the public web for visually related images, independently compares the detected face against discovered candidates, and records a cryptographic fingerprint of the resulting evidence on the **Polygon Amoy testnet**.

<!-- The blockchain is used as an **integrity and audit layer** — it does not store biometric data and does not determine whether a person is truly identified. -->

---

## Overview

TraceLens follows this pipeline:

```text
Reference Image
       │
       ▼
Face Detection & Encoding
       │
       ▼
Reverse Image Search
       │
       ▼
Candidate Image Discovery
       │
       ▼
Independent Face Matching
       │
       ▼
Best Matching Public Evidence
       │
       ▼
Evidence Fingerprint
       │
       ▼
Polygon Amoy Blockchain
       │
       ▼
Re-verification
       │
       ▼
VERIFIED / TAMPER DETECTED
```

The project was developed as a solution for the **HH Goa 2026 Shortlisting Task 3: Face Identification & Blockchain Verification**.

---

## Key Features

* Face detection using **InsightFace**
* CPU-based face recognition using ONNX Runtime
* Face embeddings and cosine similarity comparison
* Genuine reverse image search using **Google Lens through SerpApi**
* Automatic retrieval of publicly accessible candidate images
* Independent face matching against discovered candidates
* SHA-256 evidence fingerprinting
* Smart-contract based evidence registration
* Blockchain verification using **Polygon Amoy**
* Tamper detection through fingerprint comparison
* No raw biometric embeddings stored on-chain
* CLI-based workflow, no website required
* Unit tests for core functionality

---

## Why Blockchain?

TraceLens does **not** use blockchain to identify a person.

Instead, blockchain provides an immutable record of an evidence fingerprint.

For example:

```text
Discovered Evidence
       │
       ▼
Canonical Evidence Record
       │
       ▼
SHA-256 Fingerprint
       │
       ▼
Polygon Smart Contract
       │
       ▼
On-chain Record
```

Later, the same evidence can be hashed again.

If:

```text
Current Hash == On-chain Hash
```

the evidence is considered:

```text
VERIFIED
```

If:

```text
Current Hash != On-chain Hash
```

the system reports:

```text
TAMPER DETECTED
```

This means the blockchain verifies **integrity**, not authenticity or identity.

---

# Technology Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Language             | Python 3.11           |
| Face Detection       | InsightFace           |
| Face Runtime         | ONNX Runtime          |
| Image Processing     | OpenCV                |
| Numerical Processing | NumPy                 |
| Reverse Image Search | SerpApi / Google Lens |
| HTTP Requests        | Requests              |
| Blockchain           | Polygon Amoy          |
| Smart Contract       | Solidity              |
| Blockchain Client    | Web3.py               |
| Contract Compilation | py-solc-x             |
| Configuration        | python-dotenv         |
| Testing              | pytest                |
| CLI Output           | Rich                  |

---

# Project Structure

```text
TraceLens/
│
├── README.md
├── TECHNICAL.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── main.py
│
├── app/
│   ├── __init__.py
│   ├── face_engine.py
│   ├── reverse_search.py
│   ├── candidate_fetcher.py
│   ├── matcher.py
│   ├── fingerprint.py
│   ├── blockchain.py
│   ├── verifier.py
│   └── pipeline.py
│
├── contracts/
│   └── ContentRegistry.sol
│
├── scripts/
│   └── deploy.py
│
├── tests/
│   ├── test_face.py
│   ├── test_matcher.py
│   ├── test_fingerprint.py
│   ├── test_blockchain.py
│   └── test_verifier.py
│
├── docs/
│   └── ARCHITECTURE.md
│
└── data/
    ├── input/
    ├── candidates/
    └── results/
```

---

# How It Works

## 1. Reference Image

The user supplies an image containing a face.

Example:

```text
data/input/query.jpg
```

TraceLens loads the image and detects faces using InsightFace.

If multiple faces are detected, the current implementation uses the **largest detected face** as the primary face.

---

## 2. Face Detection & Encoding

The detected face is converted into a numerical embedding.

Conceptually:

```text
Image
  ↓
Face Detection
  ↓
Face Crop
  ↓
Face Embedding
```

The embedding represents facial features in numerical form.

TraceLens does not treat the embedding as proof of identity.

---

## 3. Reverse Image Search

The original image is submitted to a reverse image search service.

TraceLens uses:

```text
SerpApi
   ↓
Google Lens
```

The reverse search produces visually related public results.

The system collects information such as:

* Result title
* Source
* Page URL
* Image URL
* Search ranking
* Other available metadata

No result URL is hardcoded into the pipeline.

---

## 4. Candidate Discovery

TraceLens attempts to retrieve the publicly accessible images returned by the reverse search.

Each candidate is checked before processing.

The system verifies that:

* The URL is accessible
* The response is actually an image
* The file size is within the configured limit
* The downloaded file can be processed

Invalid or inaccessible candidates are skipped.

---

## 5. Independent Face Matching

Reverse image search alone is not treated as proof of a match.

For every usable candidate image:

```text
Candidate Image
      ↓
Face Detection
      ↓
Candidate Face Embedding
      ↓
Cosine Similarity
      ↓
Reference Embedding
```

The similarity score is used to rank candidate faces.

The system can classify results using configurable thresholds such as:

```text
< 0.50
NO_MATCH

0.50 – 0.70
POSSIBLE_MATCH

>= 0.70
STRONG_MATCH
```

These values are **demonstration heuristics**, not universal biometric thresholds.

---

# 6. Evidence Selection

Once candidate images have been evaluated, TraceLens selects the strongest usable result according to the matching pipeline.

An evidence record may look like:

```json
{
  "post_url": "https://example.com/post",
  "source": "Example Site",
  "title": "Example Post",
  "image_sha256": "..."
}
```

Only information actually discovered by the search process is recorded.

---

# 7. Evidence Fingerprinting

TraceLens generates cryptographic fingerprints using SHA-256.

The candidate image is hashed:

```text
Candidate Image
      ↓
SHA-256
      ↓
Image Fingerprint
```

The evidence metadata is then canonicalized before generating the final evidence fingerprint.

Conceptually:

```text
Evidence Metadata
      ↓
Canonical JSON
      ↓
SHA-256
      ↓
Evidence Fingerprint
```

Canonicalization ensures that equivalent JSON structures produce a deterministic fingerprint.

---

# 8. Blockchain Registration

The evidence fingerprint is registered on the **Polygon Amoy testnet**.

The smart contract stores:

```text
Fingerprint
Timestamp
Submitting Wallet
```

It does **not** store:

* Face embeddings
* Raw face images
* Private information
* Private keys
* Full web pages

---

# 9. Re-verification

TraceLens can calculate the fingerprint again later.

For the original evidence:

```text
Current Fingerprint
        │
        ▼
Blockchain Record
        │
        ▼
MATCH
        │
        ▼
VERIFIED
```

If the evidence is modified:

```text
Modified Evidence
        │
        ▼
New Fingerprint
        │
        ▼
Blockchain Record
        │
        ▼
MISMATCH
        │
        ▼
TAMPER DETECTED
```

---

# Blockchain

TraceLens uses:

**Polygon Amoy Testnet**

The project uses a dedicated testnet wallet for development and demonstration.

The deployed contract exposes two primary operations:

### Register

```solidity
registerContent(bytes32 fingerprint)
```

Registers a fingerprint on-chain.

### Verify

```solidity
verifyContent(bytes32 fingerprint)
```

Checks whether the fingerprint exists and returns its recorded timestamp and submitting address.

---

# Installation

## Requirements

Make sure the following are installed:

* Python 3.11
* Git
* Internet connection
* A SerpApi account/API key
* A Polygon-compatible testnet wallet
* Testnet POL for transaction fees

A GPU is **not required**.

TraceLens is configured to run face recognition using the CPU.

---

## Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd TraceLens
```

---

## Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file from `.env.example`.

```env
SERPAPI_KEY=

POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
PRIVATE_KEY=
CONTRACT_ADDRESS=

FACE_MATCH_THRESHOLD=0.50
```

### Environment Variables

| Variable               | Purpose                         |
| ---------------------- | ------------------------------- |
| `SERPAPI_KEY`          | SerpApi API key                 |
| `POLYGON_RPC_URL`      | Polygon Amoy RPC endpoint       |
| `PRIVATE_KEY`          | Testnet wallet private key      |
| `CONTRACT_ADDRESS`     | Deployed smart contract address |
| `FACE_MATCH_THRESHOLD` | Face matching threshold         |

### Important

**Never commit `.env` to GitHub.**

Your `.gitignore` should contain:

```text
.env
```

Never expose your wallet's private key in:

* GitHub
* README files
* screenshots
* screen recordings
* source code
* issue trackers

Use a dedicated testnet wallet for this project.

---

# Smart Contract Deployment

The project contains:

```text
contracts/ContentRegistry.sol
```

Deploy it to Polygon Amoy using:

```bash
python scripts/deploy.py
```

After deployment, the project records the contract information required by the application.

The contract address should then be placed in:

```env
CONTRACT_ADDRESS=YOUR_CONTRACT_ADDRESS
```

---

# Running TraceLens

Place the reference image inside:

```text
data/input/
```

For example:

```text
data/input/query.jpg
```

Run:

```bash
python main.py --image data/input/query.jpg
```

The pipeline performs:

```text
Face Detection
      ↓
Reverse Image Search
      ↓
Candidate Retrieval
      ↓
Face Matching
      ↓
Evidence Fingerprinting
      ↓
Blockchain Registration
      ↓
Blockchain Verification
```

---

# Example Output

A successful run should produce output similar to:

```text
TraceLens
----------------------------------------

[1] Face Detection
    Faces detected: 1
    Primary face selected

[2] Reverse Image Search
    Engine: Google Lens
    Results discovered: 12

[3] Candidate Retrieval
    Images downloaded: 7
    Failed/skipped: 5

[4] Face Matching
    Candidates evaluated: 7

    Best candidate:
    Source: Example Website
    Similarity: 0.78
    Classification: STRONG_MATCH

[5] Evidence Fingerprint
    SHA-256: ...

[6] Blockchain
    Network: Polygon Amoy
    Transaction: 0x...

[7] Verification
    Blockchain record: FOUND
    Fingerprint: MATCH

    STATUS: VERIFIED
```

The exact results depend on the input image and the live reverse-search results.

---

# Results

Generated runtime data is stored under:

```text
data/results/
```

Example:

```text
data/results/
├── final_result.json
└── contract.json
```

Candidate images are stored under:

```text
data/candidates/
```

Runtime-generated data should not be committed to the repository.

---

# Testing

Run the test suite with:

```bash
pytest
```

The tests cover components such as:

* SHA-256 fingerprint generation
* Canonical JSON serialization
* Face similarity calculations
* Match classification
* Verification logic
* Blockchain interaction logic

External services should be mocked during unit testing so tests do not require live API calls or blockchain transactions.

---

<!-- # Limitations

TraceLens has several important limitations.

### Face recognition is probabilistic

A high similarity score does not prove that two images contain the same person.

Factors such as:

* Lighting
* Pose
* Image quality
* Occlusion
* Camera characteristics
* Age differences
* Facial expressions

can affect similarity.

---

### Reverse image search is not guaranteed

Google Lens may:

* Return no results
* Return unrelated results
* Return duplicate results
* Change ranking
* Fail to access certain websites
* Produce different results over time

The system therefore cannot guarantee discovery of a matching public post.

---

### Public web access is limited

TraceLens only works with results that can be accessed through the search API and normal public HTTP requests.

It does not attempt to bypass:

* Authentication
* CAPTCHAs
* Paywalls
* Access controls
* Anti-bot protections

---

### Blockchain does not prove truth

A blockchain record proves that a particular fingerprint was registered at a particular time.

It does not prove:

```text
"This person is definitely X."
```

or:

```text
"This web post is definitely authentic."
```

It proves:

```text
"This exact fingerprint was registered on-chain."
```

---

### Search results can change

Reverse search engines are external services.

The same image may produce different results at different times.

--- -->

# Privacy & Responsible Use

TraceLens is intended as a technical demonstration of combining:

```text
Computer Vision
+
Web Search
+
Cryptographic Fingerprinting
+
Blockchain
```

It should be used responsibly.

Use images that you are authorized to process, preferably:

* Your own images
* Publicly licensed images
* Synthetic/test images
* Images where the subject has provided consent

Do not use TraceLens to conduct invasive identification or tracking of private individuals.

The project deliberately avoids storing raw biometric embeddings on the blockchain.

---

# Security Considerations

### Private keys

Private keys are loaded from environment variables and must never be committed.

### Blockchain

Only fingerprints are stored on-chain.

### Downloaded images

Candidate images are treated as untrusted external data.

The system should:

* Validate content type
* Limit download size
* Use safe filenames
* Avoid executing downloaded files

### API credentials

API keys must remain in `.env`.

---

# What TraceLens Demonstrates

The project demonstrates how multiple technologies can be combined into one practical pipeline:

### Computer Vision

Detect and compare faces using modern face-recognition models.

### Reverse Search

Discover publicly available visual evidence using a genuine reverse image search API.

### Evidence Processing

Convert discovered information into deterministic cryptographic fingerprints.

### Blockchain

Create an immutable audit record of the fingerprint.

### Verification

Recalculate the fingerprint later and compare it against the blockchain record.

---

# Future Improvements

Possible future extensions include:

* Multiple-face tracking and matching
* Better candidate ranking
* More reverse-search providers
* Social-platform-specific search adapters
* Evidence timestamps
* Web-page content fingerprinting
* Merkle-tree based evidence batches
* IPFS-based evidence archival
* Confidence calibration on benchmark datasets
* Human-in-the-loop evidence review
* Stronger provenance tracking
* Automated evidence reports

---

# Ethical Design Principles

TraceLens follows three important principles:

### 1. Identity ≠ similarity

A face similarity score should never be presented as absolute identity proof.

### 2. Blockchain ≠ truth oracle

Blockchain provides integrity and timestamped registration, not factual validation.

### 3. Public ≠ unrestricted

Information being publicly accessible does not automatically make every use ethical or appropriate.

---

<!-- # License

This project is intended for educational, experimental, and research purposes.

See `LICENSE` for the applicable license terms.

--- -->

## Documentation

For the complete technical implementation details, see:

```text
TECHNICAL.md
```

For the system architecture and data-flow diagrams, see:

```text
docs/ARCHITECTURE.md
```

<!-- ---

## Disclaimer

TraceLens is a technical prototype and should not be used as a standalone identity-verification, law-enforcement, employment, surveillance, or other high-impact decision-making system.

The results produced by the face-matching and reverse-search components are subject to errors and external-service limitations. -->
