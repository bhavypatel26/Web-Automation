# Local workflow agent

## Start

Backend, from backend/:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe main.py
```

Frontend, from frontend/:

```powershell
npm install
npm run dev
```

Open http://127.0.0.1:5173. Configure backend/.env with AZURE_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/openai/v1/, AZURE_DEPLOYMENT, and AZURE_API_KEY. Restart after changing environment settings.

## Create and execute

Create: provide a clean video, context, and URL. Azure analyzes up to 32 sampled frames. Review and save the generated workflow.yaml and SKILL.md.

Execute: select a saved skill, enter a command, and Send. Browser Use Agent receives its YAML, skill instructions, and command directly. It manages the browser and action loop. Chat displays progress, the outcome, downloads, and Cancel. Each command is an independent task; UI chat history is not model memory.

Data lives under backend/local-data. Credentials previously saved remain on disk but are not used by the executor. There is no custom login handler, cursor, Chrome executable discovery, or profile configuration. Browser Use defaults may open a separate browser. Login observations can reach the model. Submission authorization remains required for listed submission workflows.

Browser Use 0.13.10 uses the configured Azure Responses API v1 with temperature omitted. Native allowed_domains and download tracking are used. Runs have a ten-minute timeout and a configurable max_turns limit. Completion is model-based; site changes and authentication requirements can interrupt execution.

Frontend checks: npm run build. Backend source is separated into models, routers, services, and tools. The repository currently has no test suite.
