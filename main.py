"""Main script to run monsterizer app."""

from nicegui import app, ui
from src.pages import start_page

app.include_router(start_page.router)

port = 8000


ui.run(
    title="Monsterizer",
    reload=True,
    port=port,
    host="0.0.0.0",
    storage_secret="new_secret",
    dark=False,
    show=False,
)