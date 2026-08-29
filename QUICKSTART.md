# Quick Start Guide

Get the Marker PDF Converter running in minutes!

## Prerequisites

- Python 3.11 or higher
- ~2GB free disk space (for ML models on first run)
- Internet connection

## Installation & Run (3 Steps)

### 1. Install Dependencies
```bash
cd reflex-framework-rebuild

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Run the Application
```bash
# Using make
make run

# Or directly with reflex
reflex run

# Or using the bash script
bash run.sh
```

### 3. Open in Browser
```
http://localhost:3000
```

That's it! 🎉

## First Run Checklist

✅ **Initial Setup (~2 minutes)**
- First run downloads ML models (~2GB)
- Be patient - this is a one-time download
- You'll see a progress indicator

✅ **Test Conversion**
1. Click "Choose File" in sidebar
2. Upload a PDF or image
3. Click "Run Conversion"
4. Results appear in right panel

✅ **Try Different Formats**
- Switch "Output Format" to markdown, JSON, HTML, or chunks
- Re-run conversion to see format differences

## Common Tasks

### Convert a PDF to Markdown
1. Upload PDF
2. Select "markdown" format
3. Click "Run Conversion"
4. Copy markdown from results panel

### Extract Multiple Pages
1. Upload PDF
2. Enter page range: "0-5" (pages 0-5)
3. Select desired output format
4. Click "Run Conversion"

### Use OCR for Scanned PDFs
1. Upload scanned PDF
2. Check "Force OCR" option
3. Set mode to "balanced" (requires GPU for best performance)
4. Click "Run Conversion"

### Debug Layout Issues
1. Upload problematic PDF
2. Check "Debug Mode"
3. Click "Run Conversion"
4. View debug images in left panel

## Performance Tips

- **Fast Processing**: Use "fast" mode on CPU-only systems
- **Best Quality**: Use "balanced" mode on GPU systems
- **Large PDFs**: Process one page or page range at a time
- **Memory Constraints**: Disable LLM option

## Troubleshooting

### "Models failed to load"
```bash
# Clear Reflex cache and try again
rm -rf .reflex
reflex run
```

### "Port 3000 already in use"
```bash
# Use different port
reflex run --port 3001
```

### "Out of memory"
```bash
# Process fewer pages or use fast mode
# Disable LLM and OCR if not needed
```

### "Page navigation not working"
Make sure you uploaded a PDF file (not an image)

### "Results not displaying"
Check browser console (F12) for errors. If still stuck, check server logs.

## Output Formats Explained

| Format | Best For | Notes |
|--------|----------|-------|
| **Markdown** | Reading, editing | Clean formatting, images embedded |
| **JSON** | Programmatic use | Structured data, metadata included |
| **HTML** | Web display | Full styling, ready to share |
| **Chunks** | RAG systems | Segmented content with metadata |

## Next Steps

Once running:

1. **Explore Settings**
   - Try different processing modes
   - Experiment with OCR options
   - Test LLM mode (if you have LLM configured)

2. **Process Real Documents**
   - Convert your actual PDFs
   - Test different output formats
   - Compare quality across modes

3. **Integrate with Workflow**
   - Use JSON output for automation
   - Embed HTML in web pages
   - Process batch of documents

4. **Advanced Usage**
   - Check MIGRATION_GUIDE.md for architecture
   - Read README.md for detailed features
   - Look at [src/ingressor/](src/ingressor/) for customization

## Keyboard Shortcuts

- `Ctrl+C` to stop the server
- `R` to reload browser after file changes
- `F12` to open browser developer tools

## Getting Help

### Documentation
- **README.md** - Comprehensive documentation
- **MIGRATION_GUIDE.md** - Technical architecture
- **QUICKSTART.md** - This file!

### External Resources
- [Marker Docs](https://github.com/VikParuchuri/marker)
- [Reflex Docs](https://reflex.dev/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)

## Common Questions

**Q: How do I save the results?**
A: Markdown and HTML can be copied from the UI. JSON can be exported via API calls.

**Q: Can I process multiple files?**
A: Currently one at a time. Process files sequentially by uploading and converting each.

**Q: Is there a command-line version?**
A: Yes, the original marker CLI is still available via `marker` command.

**Q: How do I deploy this?**
A: See README.md for production build and deployment instructions.

**Q: What about authentication/users?**
A: This is a demo app. For multi-user setup, see deployment docs.

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4GB | 8GB+ |
| Disk | 4GB | 8GB+ |
| GPU | No | NVIDIA/AMD for best performance |

## Performance Expectations

| Task | Fast Mode | Balanced Mode |
|------|-----------|---------------|
| Simple PDF | 10-30s | 20-60s |
| Scanned PDF | 20-60s | 30-120s |
| Multi-page | +10s per page | +20s per page |
| With LLM | +2-5x | +2-5x |

*Times depend on document complexity and hardware*

---

**Happy converting!** 🚀

For detailed docs, see [README.md](README.md)
