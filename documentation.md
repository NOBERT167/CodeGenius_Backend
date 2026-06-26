Command for running the project:
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

cd C:\inetpub\wwwroot\mvc-code-generator
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

cd C:\Windows\System32\nssm-2.24\nssm-2.24\win64
nssm restart mvcgen

@echo off
cd /d "C:\inetpub\wwwroot\mvc-code-generator"
set PYTHONPATH=C:\inetpub\wwwroot\mvc-code-generator
"C:\Program Files\Python313\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause

cd C:\inetpub\wwwroot\mvc-code-generator
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

then i created start_api.bat on C:\biodata\start_api.bat with the following:
@echo off
cd /d "C:\inetpub\wwwroot\mvc-code-generator"
set PYTHONPATH=C:\inetpub\wwwroot\mvc-code-generator
"C:\Program Files\Python313\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
