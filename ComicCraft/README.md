# ComicCraft

ComicCraft is an AI-powered five-panel comic story creator.

## Technology

- Python
- FastAPI
- Jinja2
- Gemini
- Hugging Face
- Stable Diffusion-compatible image generation
- Pillow
- fpdf2
- pytest

## Workflow

The application follows this pipeline:

User prompt
    ↓
Gemini outline generation
    ↓
Five-panel story
    ↓
Gemini detailed narration
    ↓
Image generation
    ↓
Comic layout
    ↓
PDF export
    ↓
Browser preview

## Installation

Create a virtual environment.

Windows:

```powershell
py -3.11 -m venv .venv

.venv\Scripts\Activate.ps1