"""Start page for the monster generator."""

from nicegui import APIRouter, app, ui

from src.nicegui_formatting import theme_main

router = APIRouter()

@router.page("/")
async def start_page():
    with theme_main.theme_frame("Start Page"):
        with ui.row().classes("align-content-center items-center"):
            ui.button("click me")