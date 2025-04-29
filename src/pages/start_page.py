from nicegui import ui, APIRouter, app


router = APIRouter()

@router.page("/")
async def start_page():
    with ui.row().classes("align-content-center items-center"):
        ui.button("click me")