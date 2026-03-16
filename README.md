# Industrial AI Maintenance Assistant

Offline Windows-first desktop assistant for industrial troubleshooting. It analyzes PLC signals, manuals, alarm tables, and maintenance documents, then provides explanations, likely causes, and recommended manual checks.

## Safety Boundary

This assistant is strictly read-only. It must never:

- modify PLC programs
- send commands to PLCs
- change machine parameters
- control machines

That boundary is enforced in [backend/plc_interface/base.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/backend/plc_interface/base.py).

## Target Product

The primary delivery target is a Windows desktop installer:

1. User downloads `Industrial-AI-Assistant-Setup.exe`
2. User installs the application
3. The assistant runs locally without Docker
4. The LLM runs locally with an embedded `llama.cpp`-style runtime
5. Documents and vector data remain local for offline operation

## Repository Layout

```text
industrial-ai-assistant/
├── backend/
├── rag_system/
├── ai_engine/
├── desktop_app/
├── models/
│   └── deepseek-r1/
├── data/
├── installer/
├── build/
├── tests/
├── README.md
├── requirements.txt
└── requirements-windows.txt
```

## Architecture

- [desktop_app/main.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/desktop_app/main.py): PySide6 floating desktop assistant
- [backend/assistant_service.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/backend/assistant_service.py): shared local application service used by desktop UI and optional FastAPI endpoints
- [rag_system/chroma_store.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/rag_system/chroma_store.py): ChromaDB-backed retrieval layer with a lightweight in-memory fallback for dev/test environments
- [ai_engine/local_llm.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/ai_engine/local_llm.py): embedded local model runtime adapter for a bundled GGUF model
- [backend/plc_interface/protocols.py](/workspaces/AI-Based-Industrial-Maintenance-Assistant/backend/plc_interface/protocols.py): read-only OPC UA, Modbus TCP, MQTT, and REST gateway connectors

Core reasoning flow:

1. Import manuals, guides, alarm tables, and engineering documents
2. Extract text from `.txt`, `.md`, `.pdf`, and `.docx`
3. Chunk the text
4. Store embeddings in ChromaDB
5. Read a safe PLC snapshot
6. Run machine-state analysis
7. Ground the prompt with retrieved evidence
8. Generate an offline answer with the local model

## Industrial Scope

- Equipment knowledge: motors, pumps, compressors, conveyors, sensors, PLC logic
- Signal types: DI, DO, AI, AO, alarm bits
- Standards context: ISO 9001, ISO 12100, ISO 13849, IEC 61131-3, IEC 61508, IEC 62443

## Desktop Features

- floating chat window
- always-on-top assistant panel
- collapsible layout
- question input and local response output
- document import for `.pdf`, `.docx`, `.txt`, `.md`
- clipboard capture for selected text from PLC/HMI/documentation screens

## Model Packaging

The Windows build expects a bundled GGUF model in [models/deepseek-r1](/workspaces/AI-Based-Industrial-Maintenance-Assistant/models/deepseek-r1):

- expected file: `deepseek-r1-8b-q4.gguf`

The build scripts package everything in that folder into the desktop application so the final installer works offline without Ollama.

## Windows Build

On a Windows build machine:

1. Place the GGUF model in `models\deepseek-r1\deepseek-r1-8b-q4.gguf`
2. Install Inno Setup 6
3. Run:

```powershell
installer\build_windows.ps1
```

This will:

- create a Windows virtual environment
- install runtime and packaging dependencies
- build `IndustrialAIAssistant.exe` with PyInstaller
- build `Industrial-AI-Assistant-Setup.exe` with Inno Setup

Main build assets:

- [build/industrial_ai_assistant.spec](/workspaces/AI-Based-Industrial-Maintenance-Assistant/build/industrial_ai_assistant.spec)
- [installer/Industrial-AI-Assistant.iss](/workspaces/AI-Based-Industrial-Maintenance-Assistant/installer/Industrial-AI-Assistant.iss)
- [installer/build_windows.ps1](/workspaces/AI-Based-Industrial-Maintenance-Assistant/installer/build_windows.ps1)

## GitHub Release Distribution

The repository includes [`.github/workflows/windows-release.yml`](/workspaces/AI-Based-Industrial-Maintenance-Assistant/.github/workflows/windows-release.yml) to build and attach the installer to a tagged GitHub release.

Once release assets are published, users can download the latest installer via:

```text
https://github.com/mr-Anil-prajapati/AI-Based-Industrial-Maintenance-Assistant/releases/latest/download/Industrial-AI-Assistant-Setup.exe
```

This follows GitHub’s documented `releases/latest/download/<asset>` pattern: https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases

Important:

- if no GitHub Release exists yet, the link returns `404`
- if the release exists but `Industrial-AI-Assistant-Setup.exe` is not attached, the link also returns `404`
- after you publish a release and attach that exact filename, the link will download the latest installer

## Development and API Mode

The desktop app is the primary product. A FastAPI surface is still available for local testing and integration:

```bash
bash install.sh
source .venv/bin/activate
uvicorn backend.main:app --reload
```

Desktop launch in a Python environment:

```bash
python desktop_app/main.py
```

## Testing

Local automated tests:

```bash
python -m pytest
```

Recommended Windows VM acceptance test:

1. Download `Industrial-AI-Assistant-Setup.exe`
2. Install it on a clean Windows VM
3. Launch the desktop assistant
4. Import a sample document
5. Ask a question such as `Why is Motor-1 not running?`
6. Confirm the response works without internet access

## Current Limitation

This repository contains the packaging flow and model bundle location, but it does not include the multi-GB `deepseek-r1` GGUF file itself in source control. To produce the final offline installer, that model file must be placed in the expected `models/deepseek-r1/` path before running the Windows build.
