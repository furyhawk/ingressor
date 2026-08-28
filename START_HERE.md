# 🚀 START HERE - Quick Launch Guide

Your Marker PDF Converter has been successfully rebuilt with the Reflex Framework!

## ⚡ Super Quick Start (2 Minutes)

### 1️⃣ Install Dependencies
```bash
cd /path/to/ingressor
uv sync
```

### 2️⃣ Run the Application
```bash
reflex run
```

### 3️⃣ Open in Browser
```
http://localhost:3000
```

**That's it!** Your app is running. 🎉

---

## 📖 Next: Read Documentation

Choose what you need:

| Need | Time | File |
|------|------|------|
| **Quick tour** | 5 min | [QUICKSTART.md](QUICKSTART.md) |
| **Full guide** | 20 min | [README.md](README.md) |
| **How it works** | 15 min | [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) |
| **Deploy to web** | 30 min | [DEPLOYMENT.md](DEPLOYMENT.md) |
| **Find everything** | 10 min | [INDEX.md](INDEX.md) |

---

## 🎯 Using the App

1. **Upload a Document**
   - Click "📁 Choose File" button
   - Select a PDF, image, or document

2. **Configure Options** (optional)
   - Output format (Markdown, JSON, HTML, Chunks)
   - Processing mode (auto, balanced, fast)
   - Page range
   - OCR and LLM options

3. **Run Conversion**
   - Click "🚀 Run Conversion"
   - Wait for processing
   - View results on the right

4. **Copy or Save Results**
   - Results are displayed in the right panel
   - Copy markdown/JSON/HTML as needed

---

## 🛠️ Common Commands

```bash
# Run the app
make run
# or
reflex run

# Build for production
make build

# Format code
make format

# Verify setup
bash verify.sh

# Stop the app
Ctrl + C
```

---

## 🐳 Docker (Optional)

If you prefer Docker:

```bash
# Start with Docker Compose
docker-compose up

# Stop
docker-compose down
```

---

## ❓ Troubleshooting

**Issue:** First run is slow
- **Solution:** Models are downloading (~2GB), this is normal

**Issue:** Port 3000 is in use
- **Solution:** `reflex run --port 3001`

**Issue:** Import errors
- **Solution:** `uv sync` to reinstall dependencies

See [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting-deployment) for more help.

---

## 📚 Full Documentation

- **[README.md](README.md)** - Complete user guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast start guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Technical details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[INDEX.md](INDEX.md)** - Documentation index

---

## 🎓 Learning Path

1. Get it running (now!)
2. Read [QUICKSTART.md](QUICKSTART.md) (5 mins)
3. Try converting a PDF (10 mins)
4. Read [README.md](README.md) for full features
5. Deploy to production (see [DEPLOYMENT.md](DEPLOYMENT.md))

---

## 💡 Tips

- **Best Quality?** Use "balanced" mode on GPU systems
- **Fast Processing?** Use "fast" mode on CPU systems  
- **Scanned PDFs?** Enable "Force OCR" option
- **Large Documents?** Process page ranges instead

---

## ✨ What's New (Reflex vs Streamlit)

✅ **Faster** - Non-blocking UI updates
✅ **Better** - Production-ready architecture  
✅ **Scalable** - FastAPI backend
✅ **Type-safe** - Full Python type hints
✅ **Deployable** - Docker + cloud options

---

## 🚀 Ready to Deploy?

When you're ready for production:

1. Read [DEPLOYMENT.md](DEPLOYMENT.md)
2. Choose your deployment method
3. Follow the instructions

Options:
- Docker (easiest)
- Cloud (AWS, Railway, Render, DigitalOcean)
- On-premises (Systemd, Nginx)
- Custom hosting

---

## 📞 Need Help?

1. **Setup Issues?** → Check [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Usage Questions?** → See [README.md](README.md)
3. **Technical Details?** → Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
4. **Can't find something?** → Use [INDEX.md](INDEX.md)

---

## 🎉 You're All Set!

Your Marker PDF Converter is ready to use. 

**Next steps:**
1. Run the app (`reflex run`)
2. Upload a PDF
3. Convert it
4. Read the docs to learn more

Enjoy! 🚀

---

**Questions?** Check [INDEX.md](INDEX.md) for the complete documentation map.
