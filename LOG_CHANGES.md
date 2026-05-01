# Logic Changes & Bug Fixes Log (Active System)

This file tracks the active architectural decisions and fixes currently in use by the system.

## 2026-05-01 (Friday)

### 1. Unified Speech Pipeline (Sarvam AI SDK)
- **File**: `backend/core/sarvam.py`
- **Change**: Switched both TTS and STT to the official `sarvamai` Python SDK.
- **STT Logic**: Uses `saaras:v3` model with binary file handle uploads.
- **TTS Logic**: Uses `bulbul:v3` for low-latency WebSocket streaming.
- **Reason**: The SDK handles authentication (resolving 403 errors), protocol handshaking, and model versioning more reliably than manual implementations or mixed-provider (Groq/Whisper) setups.

### 2. Standardized Audio Format (.webm)
- **Files**: `frontend/src/mock_interview_test/TestInterview.jsx`, `backend/core/sarvam.py`, `backend/mock_interview_test/router.py`
- **Change**: Standardized the audio recording and temporary storage to use the `.webm` format.
- **Reason**: WebM is natively supported by modern browsers. Sarvam STT processes WebM correctly when the file extension and MIME type match.

### 3. Interview Test Environment (Sandbox)
- **Folders**: `backend/mock_interview_test/`, `frontend/src/mock_interview_test/`
- **Description**: Independent logic bench for testing STS and AI Graph behavior without database or Cloudinary dependencies.
- **Transcript Logging**: Automatically saves full QA history to `backend/test_transcripts/` for quality review.

### 4. Direct Processing (Bypassing Cloudinary)
- **File**: `backend/pipeline/nodes/interview_nodes.py`
- **Change**: Removed Cloudinary audio uploads from the production interview loop.
- **Reason**: To maximize performance and focus on the text transcript. Audio is processed directly from memory to Sarvam STT.
