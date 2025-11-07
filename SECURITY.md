# Security Checklist for Campus Resource Hub

## Before Pushing to GitHub ✅

### 1. **Sensitive Files** - CRITICAL
- [x] `.env` file is in `.gitignore` ✅
- [x] `.env.example` created as template
- [x] Gemini API key is NOT in git history

**Action Required:** 
```bash
# Make sure .env is not tracked:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### 2. **Passwords** ✅ SECURE
- [x] Passwords are hashed using `werkzeug.security.generate_password_hash()`
- [x] Using bcrypt/pbkdf2 (via Werkzeug)
- [x] Never storing plaintext passwords

### 3. **API Keys** ✅ SECURE
- [x] Gemini API key loaded from `.env` (not hardcoded)
- [x] API key is in `.gitignore`

### 4. **Database** ✅ SECURE
- [x] Using SQLite with `instance/` folder in `.gitignore`
- [x] Database file is NOT in git

### 5. **Session/Secret Keys** ✅ SECURE
- [x] Using Flask `SECRET_KEY` for sessions
- [x] Should be strong random value in production

### 6. **Configuration** ✅
- [x] `.env.example` provided for setup
- [x] Different configs for development/production ready

---

## Setup Instructions for Production

### Step 1: Clone Repository
```bash
git clone https://github.com/kanemolly/aidd_t4.git
cd aidd_t4/campus_resource_hub
```

### Step 2: Create `.env` from Template
```bash
cp .env.example .env
```

### Step 3: Update `.env` with Real Values
Edit `.env` and add:
- **FLASK_ENV=production**
- **SECRET_KEY=** (generate with: `python -c 'import secrets; print(secrets.token_hex(32))'`)
- **GEMINI_API_KEY=** (your actual API key from https://ai.google.dev)

### Step 4: Set Proper Permissions
```bash
# Make sure .env is not readable by others
chmod 600 .env
```

### Step 5: Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Run Application
```bash
python app.py
```

---

## Security Best Practices Implemented

1. **Password Hashing** 🔒
   - Passwords use PBKDF2/bcrypt via Werkzeug
   - Salted and hashed (NOT reversible)
   - `check_password()` method for verification

2. **Environment Variables** 🔐
   - Sensitive data in `.env` (not in code)
   - `.env` in `.gitignore` (not in git)
   - `.env.example` shows structure

3. **Session Security** 🛡️
   - Flask-Login for authentication
   - Session tokens are secure
   - CSRF protection enabled

4. **API Key Management** 🔑
   - Gemini API key in `.env`
   - Never hardcoded in source files
   - Rotatable without code changes

---

## Recommended Additional Security (for Production)

1. **HTTPS/SSL** - Use in production
2. **Rate Limiting** - Add Flask-Limiter
3. **CORS** - Configure properly for production domain
4. **Database Encryption** - Use PostgreSQL with SSL
5. **Audit Logging** - Log sensitive actions
6. **Input Validation** - Already implemented via forms
7. **SQL Injection Prevention** - Using ORM (SQLAlchemy)
8. **XSS Protection** - Jinja2 auto-escaping enabled

---

## How to Generate Production SECRET_KEY

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Copy the output and paste into `.env`

---

## Files Excluded from Git (via .gitignore)

- ✅ `.env` - Environment variables with API keys
- ✅ `.venv/` - Virtual environment
- ✅ `__pycache__/` - Python cache files
- ✅ `*.pyc` - Compiled Python
- ✅ `*.sqlite3` - Database files
- ✅ `instance/` - Flask instance folder
- ✅ `static/uploads/` - User-uploaded files
- ✅ `.pytest_cache/` - Test cache

---

## Verify Before Pushing

```bash
# Check what will be committed:
git status

# Make sure NO .env or sensitive files appear:
git log --diff-filter=D --summary  # Check deleted files

# List files being tracked:
git ls-files | grep -E "(\.env|password|secret|api)"
# Should return NOTHING
```

---

**Status**: ✅ Ready for GitHub
All sensitive data is properly secured and excluded from version control.
