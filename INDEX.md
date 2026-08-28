# 📖 Documentation Index

Welcome to the Marker PDF Converter - Reflex Framework! Here's a complete guide to all available documentation and resources.

---

## 🚀 Getting Started (Start Here!)

### ⚡ For the Impatient (3 Minutes)
**File:** [QUICKSTART.md](QUICKSTART.md)
- Installation in 3 steps
- Your first conversion in 2 minutes
- Common tasks quick reference
- Troubleshooting tips

### 📋 Complete Overview (20 Minutes)
**File:** [README.md](README.md)
- Full feature list
- Detailed usage guide
- Architecture overview
- Configuration options
- Performance tips

---

## 📚 Detailed Guides

### 🔄 Migration from Streamlit
**File:** [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- Streamlit → Reflex comparison
- Architecture differences
- Implementation changes
- Performance benchmarks
- Development tips

### 🐳 Deployment & Production
**File:** [DEPLOYMENT.md](DEPLOYMENT.md)
- Local development setup
- Docker deployment
- Cloud deployment (AWS, DigitalOcean, Railway, etc.)
- Production hardening
- Monitoring & logging
- Performance tuning
- Security checklist
- Troubleshooting guide

### 📊 Project Summary
**File:** [SUMMARY.md](SUMMARY.md)
- What was created
- Project structure
- Technology stack
- File organization
- Next steps for development

---

## 🏗️ Application Architecture

### Main Application File
**File:** [reflex_app.py](reflex_app.py)
- MarkerState (state management)
- UI component functions
- Event handlers
- Business logic
- Configuration

**Sections:**
1. State Management (MarkerState class)
2. File Upload Handling
3. Page Navigation
4. Conversion Logic
5. UI Components
6. Main Layout

### Configuration Files
**File:** [rxconfig.py](rxconfig.py)
- Reflex framework configuration
- App settings

**File:** [pyproject.toml](pyproject.toml)
- Project metadata
- Dependencies
- Build system

---

## 🛠️ Setup & Running

### Quick Install
```bash
# Option 1: Using UV (recommended)
uv sync

# Option 2: Using pip
pip install -e .
```

### Run Application
```bash
# Using make
make run

# Using reflex directly
reflex run

# Using bash script
bash run.sh

# View help
make help
```

### Make Commands
```bash
make install      # Install dependencies
make run          # Run dev server
make build        # Build production
make lint         # Check code style
make format       # Format code
make clean        # Remove artifacts
make help         # Show all commands
```

---

## 🐳 Docker & Containerization

### Docker Files
- **Dockerfile** - Container image definition
- **docker-compose.yml** - Multi-container setup
- **.dockerignore** - Build optimization

### Quick Docker Commands
```bash
# Build
docker build -t marker-converter .

# Run
docker run -p 3000:3000 marker-converter

# With docker-compose
docker-compose up
docker-compose down
```

---

## 📋 Configuration & Environment

### Environment Variables
**File:** [.env.example](.env.example)
Copy to `.env` and customize:
```bash
cp .env.example .env
```

### Makefile
**File:** [Makefile](Makefile)
Development convenience commands:
- Build and install
- Run/dev servers
- Linting and formatting
- Cleanup

### Run Script
**File:** [run.sh](run.sh)
Automated setup and launch with dependencies check

---

## 📁 Project Structure

```
reflex-framework-rebuild/
├── 🎯 CORE APPLICATION
│   ├── reflex_app.py           (Main app - 650+ lines)
│   ├── rxconfig.py             (Framework config)
│   └── requirements.txt         (Python deps)
│
├── 📖 DOCUMENTATION
│   ├── README.md               (Main guide)
│   ├── QUICKSTART.md           (Get started fast)
│   ├── MIGRATION_GUIDE.md      (Streamlit comparison)
│   ├── DEPLOYMENT.md           (Production setup)
│   ├── SUMMARY.md              (Project overview)
│   └── INDEX.md                (This file)
│
├── ⚙️ CONFIGURATION
│   ├── pyproject.toml          (Project metadata)
│   ├── Makefile                (Dev shortcuts)
│   ├── run.sh                  (Launch script)
│   ├── verify.sh               (Setup verification)
│   └── .env.example            (Env template)
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile              (Container image)
│   ├── docker-compose.yml      (Docker orchestration)
│   └── .dockerignore           (Build optimization)
│
├── 🗂️ LEGACY (Reference)
│   └── app/                    (Original Streamlit app)
│       ├── streamlit_app.py
│       ├── common.py
│       └── convert_single.py
│
└── 📓 NOTEBOOKS
    └── notebooks/              (Jupyter notebooks)
```

---

## 🎯 Feature Checklist

### ✅ Implemented Features
- [x] File upload (PDF, images, documents)
- [x] Page navigation with live preview
- [x] 4 output formats (Markdown, JSON, HTML, Chunks)
- [x] 3 processing modes (auto, balanced, fast)
- [x] OCR control options
- [x] LLM integration support
- [x] Debug mode with visualizations
- [x] Error handling & status messages
- [x] Responsive UI
- [x] Async processing

### 🎁 Bonus Features (Reflex Improvements)
- [x] Non-blocking UI updates
- [x] Better state management
- [x] Type-safe components
- [x] Production-ready backend
- [x] Docker containerization
- [x] Comprehensive documentation
- [x] Development convenience tools

---

## 📚 Documentation by Topic

### For Users
1. [QUICKSTART.md](QUICKSTART.md) - How to use the app
2. [README.md](README.md) - Features and usage
3. [DEPLOYMENT.md](DEPLOYMENT.md) - Running on servers

### For Developers
1. [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Architecture
2. [reflex_app.py](reflex_app.py) - Source code
3. [Makefile](Makefile) - Development workflow

### For DevOps
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
2. [Dockerfile](Dockerfile) - Container config
3. [docker-compose.yml](docker-compose.yml) - Orchestration

---

## 🔍 Common Questions

### Getting Started
**Q: How do I run the app?**
A: See [QUICKSTART.md](QUICKSTART.md) (3 steps)

**Q: How do I install it?**
A: ```bash
uv sync
reflex run
```

**Q: What are system requirements?**
A: Python 3.11+, 4GB RAM, ~4GB disk space

### Usage
**Q: How do I convert a PDF?**
A: Upload → Choose options → Click Run → View results

**Q: What output formats are available?**
A: Markdown, JSON, HTML, Chunks (see README.md)

**Q: How do I enable OCR?**
A: Check "Force OCR" option or use "balanced" mode

### Development
**Q: How do I add a new feature?**
A: Edit reflex_app.py → Add to MarkerState → Add UI component

**Q: How do I deploy to production?**
A: See [DEPLOYMENT.md](DEPLOYMENT.md) for multiple options

**Q: Can I use this with multiple users?**
A: Yes, Reflex handles concurrent connections

---

## 🚀 Quick Command Reference

```bash
# Installation
uv sync                    # Install dependencies
pip install -e .          # Alternative pip install

# Running
reflex run                 # Start dev server
make run                   # Same with make
bash run.sh               # Using bash script

# Development
make format               # Format code
make lint                 # Check style
make clean                # Clean artifacts

# Docker
docker build -t app .     # Build image
docker-compose up         # Run with compose

# Verification
bash verify.sh            # Check setup
python -m py_compile *.py # Check syntax

# Access
http://localhost:3000     # Web UI (once running)
http://localhost:8000/docs # API docs (if running backend)
```

---

## 🆘 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Models not loading | First run downloads ~2GB, be patient |
| Port 3000 in use | `reflex run --port 3001` |
| Import errors | `uv sync` to ensure deps installed |
| File upload fails | Check max file size in config |
| Page preview broken | Ensure uploaded file is PDF/image |
| Docker build fails | Check disk space, try `docker prune` |

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting.

---

## 🔗 External Resources

### Marker PDF Library
- **GitHub:** https://github.com/VikParuchuri/marker
- **Documentation:** Part of marker-pdf package

### Reflex Framework
- **Website:** https://reflex.dev
- **Documentation:** https://reflex.dev/docs
- **GitHub:** https://github.com/reflex-dev/reflex

### FastAPI
- **Documentation:** https://fastapi.tiangolo.com
- **API Reference:** https://fastapi.tiangolo.com/docs

### Python & Deployment
- **Python:** https://python.org
- **Docker:** https://docker.com
- **Docker Compose:** https://docs.docker.com/compose

---

## 📞 Getting Help

### Step 1: Check Documentation
1. [QUICKSTART.md](QUICKSTART.md) for quick answers
2. [README.md](README.md) for detailed info
3. [DEPLOYMENT.md](DEPLOYMENT.md) for setup issues
4. [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for technical details

### Step 2: Check Code Comments
- [reflex_app.py](reflex_app.py) has inline documentation
- Look for comments near your issue

### Step 3: External Resources
- [Marker Issues](https://github.com/VikParuchuri/marker/issues)
- [Reflex Discussions](https://github.com/reflex-dev/reflex/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/reflex)

### Step 4: Verify Setup
```bash
bash verify.sh  # Run verification script
```

---

## 📋 Maintenance & Updates

### Check for Updates
```bash
pip install --upgrade reflex marker-pdf
```

### Update Dependencies
```bash
uv lock --upgrade
```

### Clean Up
```bash
make clean           # Remove build artifacts
docker system prune   # Clean Docker
```

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run the application
3. Test basic conversion

### Intermediate (2 hours)
1. Read [README.md](README.md)
2. Explore different output formats
3. Try advanced options

### Advanced (4+ hours)
1. Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
2. Study [reflex_app.py](reflex_app.py) code
3. Read [DEPLOYMENT.md](DEPLOYMENT.md)
4. Set up production environment

### Developer (8+ hours)
1. Full codebase review
2. Add custom features
3. Deploy to cloud
4. Set up monitoring

---

## ✅ Setup Verification

Run verification script to ensure everything is ready:
```bash
bash verify.sh
```

This checks:
- ✅ All required files present
- ✅ Python syntax valid
- ✅ Python version compatible
- ✅ Git repository initialized
- ✅ Configuration files correct

---

## 📝 File Manifest

| File | Lines | Purpose |
|------|-------|---------|
| reflex_app.py | 650+ | Main application |
| QUICKSTART.md | 200+ | Quick start guide |
| README.md | 250+ | Comprehensive guide |
| MIGRATION_GUIDE.md | 350+ | Streamlit comparison |
| DEPLOYMENT.md | 400+ | Production guide |
| SUMMARY.md | 300+ | Project summary |
| Dockerfile | 20 | Container setup |
| docker-compose.yml | 20 | Docker orchestration |
| Makefile | 40 | Dev commands |
| run.sh | 40 | Launch script |
| verify.sh | 100 | Setup verification |

---

## 🎉 You're All Set!

Everything is ready to go. Choose your next step:

1. **Quick Start?** → [QUICKSTART.md](QUICKSTART.md)
2. **Learn Everything?** → [README.md](README.md)
3. **Deploy?** → [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Understand Changes?** → [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
5. **See What's Done?** → [SUMMARY.md](SUMMARY.md)

---

**Happy converting! 🚀**

*Last updated: 2026-08-28*
*For questions, see troubleshooting section above or external resources.*
