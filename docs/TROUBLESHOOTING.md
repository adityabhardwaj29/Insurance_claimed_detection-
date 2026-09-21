# FraudShield AI — Troubleshooting & Operations Guide

This guide provides fast solutions for common environment setup, port conflict, dependency, and database connection issues on Windows.

---

## 1. Port Conflicts (Address Already in Use)

If you encounter `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)`:

### Solution
Run the automated port cleanup utility:
```cmd
stop.bat
```
This utility inspects ports `8000` (FastAPI), `3000` (React UI), `5173` (Vite dev), and `8501` (Streamlit) and terminates conflicting processes.

Alternatively, you can manually free the port:
```powershell
# In PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

---

## 2. Python Virtual Environment Issues

### Issue: "Activate.ps1 cannot be loaded because running scripts is disabled on this system"
PowerShell's default execution policy restricts `.ps1` script execution.

### Solution
Run one of the following commands in PowerShell (as Administrator or CurrentUser):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Or simply use the provided `.bat` launchers:
```cmd
setup.bat
run.bat
```
Batch files (`.bat`) are not subject to PowerShell execution policy restrictions.

---

## 3. Node.js & Frontend Build Errors

### Issue: "'npm' is not recognized as an internal or external command"
Node.js is not installed or not added to system PATH.

### Solution
1. Download and install Node.js 18 LTS or higher from [https://nodejs.org/](https://nodejs.org/).
2. Ensure you check **"Add to PATH"** during installation.
3. Restart your terminal or VS Code window so the updated PATH takes effect.

### Issue: "node_modules missing or corrupted"
Clean and reinstall the frontend packages:
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install
cd ..
```

---

## 4. Database Connectivity Issues

### Issue: "Supabase credentials missing; falling back to SQLite"
By default, FraudShield AI operates smoothly with zero configuration using local SQLite:
`database/fraud_detection.db`.

To connect to Supabase PostgreSQL:
1. Copy `.env.example` to `.env`.
2. Populate the Supabase credentials:
   ```env
   DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=your-service-role-or-anon-key
   ```
3. Run the automated migration runner:
   ```cmd
   python scripts/migrate.py --target supabase
   ```

---

## 5. Model Weights or Feature Data Missing

### Issue: "Model artifact not found: models/fraud_model/..."
If model files are absent or need to be reproduced from scratch:
```cmd
run.bat --pipeline
```
This executes the reproducible data extraction, feature generation, graph construction, and XGBoost training pipeline.

---

## 6. Verifying Entire System Health

Whenever in doubt, run the automated diagnostic suite:
```cmd
python scripts/health_check.py
```
This checks all Python packages, SQLite tables, model joblibs, and graph data files, reporting any missing prerequisites.
