from __future__ import annotations

import reflex as rx

from .components import index

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="blue",
        gray_color="slate",
        panel_background="solid",
        radius="medium",
    ),
    style={
        "body": {"background_color": "#f8fafc", "color": "#0f172a"},
        "h1": {"color": "#0f172a"},
        "h2": {"color": "#0f172a"},
        "h3": {"color": "#0f172a"},
        "p": {"color": "#1e293b"},
        "label": {"color": "#0f172a"},
    },
)
app.add_page(index, title="Marker PDF Converter")
