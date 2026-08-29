# Marker PDF Converter - Reflex Framework

A modern web application built with **Reflex** that converts PDFs, images, and documents to Markdown, HTML, JSON, or chunks using the [Marker](https://github.com/VikParuchuri/marker) library.

## Features

- 📄 **Multi-format Support**: Convert PDFs, images, and documents (PNG, JPG, GIF, PPTX, DOCX, XLSX, HTML, EPUB)
- 🎨 **Live Preview**: View document pages in real-time as you navigate
- 📝 **Multiple Output Formats**: Export as Markdown, JSON, HTML, or chunks
- ⚡ **Flexible Processing**: Choose between fast, balanced, or auto processing modes
- 🔍 **Advanced OCR Options**: Control OCR behavior with granular settings
- 🤖 **LLM Support**: Optional LLM integration for higher quality processing
- 🐛 **Debug Mode**: Analyze document layout with debug visualizations
- 🎯 **Page Range Selection**: Process specific pages or page ranges

## Installation

### Prerequisites
- Python 3.11 or higher
- UV package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd reflex-framework-rebuild
```

2. Install dependencies using UV:
```bash
uv sync
```

Or with pip:
```bash
pip install -e .
```

3. Install Reflex CLI (if not included):
```bash
pip install reflex
```

## Running the Application

### Using Reflex Development Server

```bash
reflex run
```

The application will start on `http://localhost:3000`

### Production Build

```bash
reflex build
reflex export
```

Then deploy the generated files or run:
```bash
reflex run --env prod
```

## Usage Guide

### Basic Workflow

1. **Upload a Document**
   - Click the "Choose File" button in the left sidebar
   - Select your PDF, image, or supported document format

2. **Navigate (PDF only)**
   - Use the page number input or the arrow buttons to view different pages
   - Page navigation is 1-based; page ranges remain zero-based
   - Preview updates in the left panel

3. **Configure Conversion Options**
   - **Output Format**: Choose output type (markdown, JSON, HTML, chunks)
   - **Processing Mode**:
     - `auto`: Automatically selects based on device (GPU = balanced, CPU/MPS = fast)
     - `balanced`: Uses VLM layout model + full-page OCR (best on GPU)
     - `fast`: Lightweight CPU detectors, only OCRs garbled/empty content
   - **Page Range**: Specify which pages to process with zero-based ranges (e.g., "0,5-10,20")

4. **Configure Advanced Options**
   - **Use LLM**: Enable for higher quality processing
   - **Force OCR**: Force OCR on all pages
   - **Disable OCR**: Skip OCR (text-layer extraction only)
   - **Strip Existing OCR**: Re-OCR the document
   - **Show Page Headers/Footers**: Include headers and footers in output
   - **Debug Mode**: Generate debug visualizations

5. **Run Conversion**
   - Click the "Run Conversion" button
   - Monitor progress via status messages
   - View results in the right panel (automatically formatted)

## Output Formats

### Markdown
- Clean, readable markdown representation
- Images embedded as base64-encoded HTML
- Tables, equations, and formatting preserved

### JSON
- Structured data format
- Useful for programmatic processing
- Full metadata included

### HTML
- Web-ready HTML output
- Fully styled and formatted
- Direct preview in browser

### Chunks
- Segmented content
- Useful for RAG (Retrieval-Augmented Generation)
- JSON format with chunk metadata

## Architecture

### Components

- **State Management** (`MarkerState`): 
  - Centralized state for file handling, options, and results
  - Async conversion handling

- **UI Components**:
  - `render_sidebar()`: Controls and options
  - `render_preview()`: Document preview with debug images
  - `render_results()`: Formatted output display

- **Backend Integration**:
  - Marker library integration for PDF/document conversion
  - PyPDF integration for page extraction
  - PIL for image handling

### File Structure

```
ingressor/
├── src/ingressor/         # Main application package
│   ├── app.py             # Reflex app bootstrap
│   ├── components.py      # UI composition
│   ├── marker.py          # Marker conversion helpers
│   └── state.py           # Reflex state and actions
├── reflex_app.py          # Legacy compatibility entrypoint
├── marker_converter/      # Reflex entrypoint module
├── rxconfig.py            # Reflex configuration
├── pyproject.toml         # Project dependencies
└── app/                   # Legacy Streamlit helpers
```

## Technology Stack

- **Frontend Framework**: Reflex (Python-based React)
- **Backend**: FastAPI (integrated with Reflex)
- **Document Processing**: Marker PDF
- **PDF Handling**: PyPDF, pypdfium2
- **Image Processing**: Pillow

## Configuration

### Environment Variables

```bash
# PyTorch/ML
PYTORCH_ENABLE_MPS_FALLBACK=1    # Enable MPS fallback on Apple Silicon

# Logging
GRPC_VERBOSITY=ERROR              # Suppress gRPC logging
GLOG_minloglevel=2                # Suppress TensorFlow logging
```

## Troubleshooting

### Models not loading
- First run downloads large ML models (~2GB)
- Initial conversion may take 1-2 minutes
- Check internet connection

### Memory issues
- Use "fast" mode for resource-constrained systems
- Process one page at a time
- Disable LLM and OCR if not needed

### OCR not working
- Ensure scanned pages are high quality
- Enable "Force OCR" option
- Check debug images to verify detection

### Layout detection issues
- Use "balanced" mode on GPU systems
- Check debug images in debug mode
- Try adjusting page range

## Performance Tips

1. **GPU Systems**: Use "balanced" mode for best quality
2. **CPU Systems**: Use "fast" mode for reasonable speed
3. **Large Documents**: Process page ranges instead of full documents
4. **Memory**: Disable LLM if running low on memory

## Development

### Adding New Features

1. Extend `MarkerState` for new state variables
2. Add handler methods for new operations
3. Create UI components with `rx.Component` return type
4. Integrate into main layout

### Running Tests

```bash
# Run linting
reflex lint

# Format code
reflex format
```

## Known Limitations

- Reflex rendering may be resource-intensive for very large PDFs
- Some advanced Marker features may require CLI usage
- Real-time live updates require WebSocket connection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Same license as the parent project

## References

- [Marker Documentation](https://github.com/VikParuchuri/marker)
- [Reflex Documentation](https://reflex.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## Support

For issues or questions:
1. Check the [Marker Issues](https://github.com/VikParuchuri/marker/issues)
2. Check the [Reflex Docs](https://reflex.dev/docs)
3. Open an issue in this repository
