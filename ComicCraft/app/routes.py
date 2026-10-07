from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import ImageTestRequest, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import GeminiFlashService
from app.services.gemini_pro import GeminiProService
from app.services.image_generator import ImageGenerator
from app.services.layout_builder import build_comic_layout
from app.utils.files import static_url_from_path


router = APIRouter()

settings = get_settings()

templates = Jinja2Templates(
    directory=str(settings.templates_dir)
)


def run_generation(data: PromptRequest):

    flash_service = GeminiFlashService(settings)

    pro_service = GeminiProService(settings)

    image_generator = ImageGenerator(settings)

    # Step 1:
    # Generate five-panel outline
    outline = flash_service.generate_outline(data)

    # Step 2:
    # Generate detailed narration
    story = pro_service.generate_story(
        data,
        outline,
    )

    # Step 3:
    # Generate images
    image_paths = []

    for panel in outline:

        image_path = image_generator.generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(image_path)

    # Step 4:
    # Build comic layout
    layout = build_comic_layout(
        story,
        image_paths,
    )

    title = f"{data.character_name}'s Comic"

    # Step 5:
    # Export PDF
    pdf_path = save_pdf(
        layout,
        settings,
        title,
    )

    # Convert local paths to browser URLs
    for panel in layout:

        panel["image_url"] = static_url_from_path(
            Path(panel["image_path"]),
            settings.static_dir,
        )

    pdf_url = static_url_from_path(
        pdf_path,
        settings.static_dir,
    )

    return (
        title,
        outline,
        story,
        layout,
        pdf_url,
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        (
            title,
            outline,
            story,
            layout,
            pdf_url,
        ) = run_generation(data)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "title": title,
                "outline": outline,
                "story": story,
                "layout": layout,
                "pdf_url": pdf_url,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    payload: PromptRequest,
):

    try:

        (
            title,
            outline,
            story,
            layout,
            pdf_url,
        ) = run_generation(payload)

        return {
            "success": True,
            "title": title,
            "outline": [
                item.model_dump()
                for item in outline
            ],
            "panels": [
                item.model_dump()
                for item in story
            ],
            "layout": layout,
            "pdf_url": pdf_url,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post("/test-image")
async def test_image(
    payload: ImageTestRequest,
):

    try:

        image_generator = ImageGenerator(settings)

        path = image_generator.generate_image(
            prompt=payload.prompt,
            panel_number=0,
        )

        return {
            "success": True,
            "image_url": static_url_from_path(
                path,
                settings.static_dir,
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    filename: str = "",
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "filename": filename,
        },
    )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "service": settings.app_name,
        "ai_mode": settings.ai_mode,
        "image_provider": settings.image_provider,
    }


@router.get("/download/{filename}")
async def download_pdf(
    filename: str,
):

    safe_name = Path(filename).name

    path = settings.export_dir / safe_name

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=safe_name,
    )