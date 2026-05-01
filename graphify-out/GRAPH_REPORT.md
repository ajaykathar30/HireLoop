# Graph Report - ..  (2026-05-01)

## Corpus Check
- 154 files · ~131,522 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 758 nodes · 1272 edges · 29 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 476 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]

## God Nodes (most connected - your core abstractions)
1. `cn()` - 77 edges
2. `Job` - 18 edges
3. `Candidate` - 17 edges
4. `run_agent()` - 16 edges
5. `run_pipeline()` - 15 edges
6. `SpeechCrew` - 15 edges
7. `FileCrew` - 15 edges
8. `Application` - 14 edges
9. `Nearbyhospitals` - 14 edges
10. `general_que` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Checks for jobs with passed deadlines and triggers the pipeline.` --uses--> `Job`  [INFERRED]
  backend\core\scheduler.py → backend\models\job.py
- `RecruitSight — Similar Repo Discovery Agent Uses the Exa web search API to find` --uses--> `SimilarRepoOutput`  [INFERRED]
  MCP_AGENTS\agents\similar_repo_discovery.py → MCP_AGENTS\models\schemas.py
- `Discover similar repositories using Exa web search.      Formulates targeted sea` --uses--> `SimilarRepoOutput`  [INFERRED]
  MCP_AGENTS\agents\similar_repo_discovery.py → MCP_AGENTS\models\schemas.py
- `save_answer_node()` --calls--> `upload_file()`  [INFERRED]
  backend\pipeline\nodes\interview_nodes.py → backend\core\cloudinary.py
- `save_answer_node()` --calls--> `generate_embedding()`  [INFERRED]
  backend\pipeline\nodes\interview_nodes.py → backend\core\embeddings.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.03
Nodes (76): Button(), cn(), AlertDialogAction(), AlertDialogCancel(), AlertDialogContent(), AlertDialogDescription(), AlertDialogFooter(), AlertDialogHeader() (+68 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (88): code_quality_agent(), RecruitSight — Code Quality & Logic Agent Evaluates whether the code is logicall, Evaluate the code quality and logic of a repository.          Samples key files,, Intelligently select the most important files to sample.     Prioritizes entry p, _select_key_files(), commit_forensics_agent(), RecruitSight — Commit Forensics Agent Performs forensic analysis of the commit h, Perform forensic analysis on the commit history.          Fetches the full commi (+80 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (48): parse_resume(), parse_resume_text(), ParsedResume, Parses raw resume text using Gemini AI with structured output.     Does NOT int, Parses resume text from DB using Gemini AI with structured output.     Updates, Generates audio using Deepgram Aura (Free Tier friendly).     Requesting 'mulaw, text_to_speech(), Dependency to verify that a job exists and belongs to the currently logged-in co (+40 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (54): BestDeal, run_comparison(), FitScore, Scores the fit between a resume and a job description using Gemini AI., score_fit(), AnswerEvaluation, evaluate_interview_answer(), generate_first_question() (+46 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (46): RecruitSight — Base Agent Runner Reusable async agent executor with retry logic,, Core agent executor.          1. Calls client.aio.models.generate_content() with, run_agent(), linkedin_content_agent(), RecruitSight — LinkedIn Content & Thought Leadership Agent Analyzes the candidat, Analyze a candidate's LinkedIn content and thought leadership.          Args:, linkedin_credibility_agent(), RecruitSight — LinkedIn Achievement & Credibility Agent Verifies and scores the (+38 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (38): care_coordinator(), care_task(), doctor(), FileCrew, general_que, hospital_finder(), medical_consultation(), medical_data() (+30 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (34): Enum, AboutSectionQuality, CertificationPattern, CertRelevance, CommentQuality, CommunicationQuality, ExpertiseAlignment, HonorType (+26 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (31): file_to_text(), main(), print_banner(), RecruitSight — LinkedIn Profile Analyzer Entry point for the LinkedIn multi-agen, Configure structured logging for the LinkedIn pipeline., Print the RecruitSight LinkedIn banner., Basic validation that the URL looks like a LinkedIn profile URL., setup_logging() (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (24): Uploads a file to Cloudinary.     folder_path: e.g., "HireLoop/Resume" or "Hire, upload_file(), generate_embedding(), get_embeddings_model(), Generates a 768-dimensional embedding for the given text using Gemini via LangCh, extract_text_from_pdf(), Downloads a PDF from a URL and extracts all text., update_candidate_details() (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (15): decide_reply(), gemini_response(), general_question(), Takes the complete list of conversation turns and generates a summary., Takes the general que and answer them, summarize_conversation(), media_stream(), Starts ngrok via system command and retrieves the public URL. (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.15
Nodes (13): create_access_token(), get_current_user_id(), User, login(), read_users_me(), register_candidate(), register_company(), authenticate_user() (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.2
Nodes (10): RecruitSight — Similar Repo Discovery Agent Uses the Exa web search API to find, Discover similar repositories using Exa web search.      Formulates targeted sea, similar_repo_discovery_agent(), _get_exa(), RecruitSight — Exa Web Search Tools Wrapper around the Exa Python SDK for discov, Lazily initialize the Exa client., Search for similar GitHub repositories using Exa.     Returns a list of dicts wi, General web search for context (market research, tutorial detection, etc.). (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.2
Nodes (6): lifespan(), check_and_run_pipelines(), Checks for jobs with passed deadlines and triggers the pipeline., start_scheduler(), Triggers the LangGraph-based recruitment pipeline., run_job_pipeline()

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (9): crew(), create_user_profile(), face_recognice(), get_database(), get_face_encodings(), get_user_knowledge_profile(), Runs facial recognition to fetch or create user data,     then stores that data, Converts BGR frame to RGB and returns encodings. (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.32
Nodes (6): apply_for_job(), get_applicants_for_job(), get_my_applications(), apply_to_job(), get_candidate_applications(), get_job_applications()

### Community 15 - "Community 15"
Cohesion: 0.29
Nodes (6): Converts text to speech using Sarvam AI Bulbul v3.     Returns base64 encoded a, Converts speech to text using Groq Whisper (whisper-large-v3-turbo) for ultra-lo, Streams text to speech using Sarvam AI via WebSocket.     Yields audio chunks (, speech_to_text(), stream_text_to_speech(), text_to_speech()

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (1): update_interview_session_statuses  Revision ID: 1eb1f3f83877 Revises: e28a369

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (1): Add InterviewRoomMemory with pgvector  Revision ID: 6bd9c8db652f Revises: 1eb1f3

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (1): add_new_notification_types  Revision ID: 8769bb49450c Revises: e5060454a294

### Community 19 - "Community 19"
Cohesion: 0.5
Nodes (1): fix embeddings type  Revision ID: d4e1dfd55cc5 Revises: c56dacc53f33 Create

### Community 20 - "Community 20"
Cohesion: 0.5
Nodes (1): add_shortlisted_to_application_status  Revision ID: e5060454a294 Revises: d4e

### Community 21 - "Community 21"
Cohesion: 0.5
Nodes (1): baseline existing schema  Revision ID: f9e1dfd55cc4 Revises:  Create Date: 2

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): RecruitSight — Configuration & Client Initialization Loads environment variables

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Uploads a file to Cloudinary.     folder_path: e.g., "HireLoop/Resume" or "Hire

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Converts text to speech using Sarvam AI Bulbul v3.     Returns base64 encoded a

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Converts speech to text using Sarvam AI Saaras v3.     Expects raw audio bytes

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Generates 5 tailored interview questions based on the candidate's resume and job

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Evaluates a single answer on a scale of 0-20.

## Knowledge Gaps
- **108 isolated node(s):** `Add domain knowledge base  Revision ID: 0b0193337f3c Revises: 6bd9c8db652f C`, `update_interview_session_statuses  Revision ID: 1eb1f3f83877 Revises: e28a369`, `Add InterviewRoomMemory with pgvector  Revision ID: 6bd9c8db652f Revises: 1eb1f3`, `add_new_notification_types  Revision ID: 8769bb49450c Revises: e5060454a294`, `sync models with db  Revision ID: c56dacc53f33 Revises: f9e1dfd55cc4 Create` (+103 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 16`** (4 nodes): `1eb1f3f83877_update_interview_session_statuses.py`, `downgrade()`, `update_interview_session_statuses  Revision ID: 1eb1f3f83877 Revises: e28a369`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (4 nodes): `6bd9c8db652f_add_interviewroommemory_with_pgvector.py`, `downgrade()`, `Add InterviewRoomMemory with pgvector  Revision ID: 6bd9c8db652f Revises: 1eb1f3`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (4 nodes): `8769bb49450c_add_new_notification_types.py`, `downgrade()`, `add_new_notification_types  Revision ID: 8769bb49450c Revises: e5060454a294`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (4 nodes): `d4e1dfd55cc5_fix_embeddings_type.py`, `downgrade()`, `fix embeddings type  Revision ID: d4e1dfd55cc5 Revises: c56dacc53f33 Create`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (4 nodes): `e5060454a294_add_shortlisted_to_application_status.py`, `downgrade()`, `add_shortlisted_to_application_status  Revision ID: e5060454a294 Revises: d4e`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (4 nodes): `f9e1dfd55cc4_baseline_existing_schema.py`, `downgrade()`, `baseline existing schema  Revision ID: f9e1dfd55cc4 Revises:  Create Date: 2`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (3 nodes): `config.py`, `BaseSettings`, `Settings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `config.py`, `RecruitSight — Configuration & Client Initialization Loads environment variables`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Uploads a file to Cloudinary.     folder_path: e.g., "HireLoop/Resume" or "Hire`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Converts text to speech using Sarvam AI Bulbul v3.     Returns base64 encoded a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Converts speech to text using Sarvam AI Saaras v3.     Expects raw audio bytes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Generates 5 tailored interview questions based on the candidate's resume and job`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Evaluates a single answer on a scale of 0-20.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Input()` connect `Community 7` to `Community 8`, `Community 0`, `Community 13`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `cn()` connect `Community 0` to `Community 7`?**
  _High betweenness centrality (0.228) - this node is a cross-community bridge._
- **Why does `run_mock_interview()` connect `Community 7` to `Community 6`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `cn()` (e.g. with `Button()` and `AlertDialogOverlay()`) actually correct?**
  _`cn()` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `str` (e.g. with `get_current_user_id()` and `save_answer_node()`) actually correct?**
  _`str` has 27 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Add domain knowledge base  Revision ID: 0b0193337f3c Revises: 6bd9c8db652f C`, `update_interview_session_statuses  Revision ID: 1eb1f3f83877 Revises: e28a369`, `Add InterviewRoomMemory with pgvector  Revision ID: 6bd9c8db652f Revises: 1eb1f3` to the rest of the system?**
  _108 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.03 - nodes in this community are weakly interconnected._