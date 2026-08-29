from __future__ import annotations

import reflex as rx

from .components import index

app = rx.App()
app.add_page(index, title="Marker PDF Converter")
