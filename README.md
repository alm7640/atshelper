# ATS Helper

Simple ATS Resume Checker and improver using OpenAI and Gradio.

Prerequisites
- Python 3.10+ installed (system or in WSL2)
- An OpenAI API key (set `OPENAI_API_KEY` in your environment or in a `.env` file)

Quick start

1. Create and activate a virtual environment (recommended):

Windows PowerShell (native):

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

WSL2 (recommended for Linux-like environment on Windows):

```bash
# open your WSL2 distro, then:
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python ats_ai_helper.py
```

WSL2 notes and best practices
- Use WSL2 if you prefer a Linux-like environment on Windows; it avoids many Windows path and permission issues.
- Keep your development virtual environment inside the project directory (for example `.venv`).
- Use `python -m venv` (standard library) or tools like `pipx`/`pipenv`/`poetry` if you prefer more advanced workflows.
- To edit files from Windows editors (VS Code), open the project in WSL using `code .` from the WSL shell so extensions and terminal use the WSL Python interpreter.

OpenAI API key
- This project requires an OpenAI API key to call the models. Obtain one at https://platform.openai.com/ and set it as an environment variable:

Windows PowerShell:

```powershell
$Env:OPENAI_API_KEY = "sk-..."
```

WSL2 / Linux:

```bash
export OPENAI_API_KEY="sk-..."
```

Security and notes
- Do not commit your API key or `.env` file to the repository. Add `.env` or other secrets to `.gitignore`.
- Consider using GitHub Secrets and Actions for CI usage.

Notes:
- This repository is configured to use SSH remotes by default if you authenticated with SSH.

