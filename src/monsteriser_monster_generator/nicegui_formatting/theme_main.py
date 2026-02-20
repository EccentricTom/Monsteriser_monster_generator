"""The main theme of the application."""

from contextlib import contextmanager

from nicegui import app, context, ui

@contextmanager
def theme_frame(navtitle:str, session: bool = False):
    """
    Create a default theme for the application.

    Args:
    navtitle: The name of the page
    session: boolean used to create escape clause in menu, not implemented

    """
    context.client.content.tailwind.padding("p-5")
    context.client.content.classes("w-screen h-[94vh]")
    with ui.header() as header:
        ui.label("Monsteriser: A monster creation tool for TTRPGs")
        ui.label(navtitle)
        with ui.row():
            with ui.menu():
                ui.menu_item("placeholder 1")
                ui.menu_item("placeholder 2")
    yield
    with ui.footer() as footer:
        ui.label("Legal stuff goes here")