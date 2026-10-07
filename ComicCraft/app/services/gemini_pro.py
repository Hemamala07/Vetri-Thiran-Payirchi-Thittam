import json
from typing import List

from google import genai
from pydantic import TypeAdapter

from app.config import Settings
from app.schemas import (
    PanelOutline,
    PanelStory,
    PromptRequest,
)


class GeminiProService:

    def __init__(
        self,
        settings: Settings,
    ):

        self.settings = settings

        if settings.gemini_api_key:

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

        else:

            self.client = None

    def generate_story(
        self,
        request: PromptRequest,
        outline: List[PanelOutline],
    ) -> List[PanelStory]:

        if self.settings.ai_mode.lower() == "mock":

            return self._mock(
                request,
                outline,
            )

        if not self.client:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        outline_json = json.dumps(
            [
                panel.model_dump()
                for panel in outline
            ],
            ensure_ascii=False,
        )

        prompt = f"""
Write concise final narration for a
{self.settings.panel_count}-panel comic.

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Original idea:
{request.story_prompt}

Panel outline:

{outline_json}

Return ONLY JSON matching:

[
  {{
    "panel_number": 1,
    "title": "panel title",
    "scene_description": "short scene-setting description",
    "caption": "brief ambient caption",
    "narration": "concise narration",
    "dialogue": "natural character dialogue"
  }}
]

Requirements:

1. Return exactly five panels.
2. Preserve panel sequence.
3. Maintain character continuity.
4. Make dialogue short.
5. Keep narration suitable for a comic.
6. Ensure the final panel provides a conclusion.
"""

        response = self.client.models.generate_content(
            model=self.settings.gemini_story_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[PanelStory],
                "temperature": 0.85,
            },
        )

        panels = TypeAdapter(
            list[PanelStory]
        ).validate_python(
            json.loads(response.text)
        )

        if len(panels) != self.settings.panel_count:

            raise RuntimeError(
                "Gemini returned an unexpected number of story panels."
            )

        return panels

    @staticmethod
    def _mock(
        request: PromptRequest,
        outline: List[PanelOutline],
    ):

        return [

            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                caption=(
                    f"{request.setting} — "
                    f"{request.tone} mood."
                ),
                narration=(
                    f"{request.character_name} "
                    f"moves forward, determined to "
                    f"discover what happens next."
                ),
                dialogue=(
                    f"{request.character_name}: "
                    f"We can do this!"
                ),
            )

            for panel in outline
        ]