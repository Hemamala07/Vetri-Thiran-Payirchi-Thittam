import json
from typing import List

from google import genai
from pydantic import TypeAdapter

from app.config import Settings
from app.schemas import PanelOutline, PromptRequest


class GeminiFlashService:

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

    def generate_outline(
        self,
        request: PromptRequest,
    ) -> List[PanelOutline]:

        # Offline testing mode
        if self.settings.ai_mode.lower() == "mock":

            return self._mock(request)

        if not self.client:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        prompt = f"""
Create exactly {self.settings.panel_count}
connected comic panels.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Return ONLY JSON matching:

[
  {{
    "panel_number": 1,
    "title": "short panel title",
    "scene_description": "1-2 sentence visual scene description",
    "image_prompt": "detailed image-generation prompt"
  }}
]

Requirements:

1. Return exactly five panels.
2. Keep the protagonist visually consistent.
3. Make the story sequential.
4. Include a clear beginning.
5. Include a conflict or challenge.
6. Include a resolution.
7. Image prompts should be detailed enough for an image model.
"""

        response = self.client.models.generate_content(
            model=self.settings.gemini_outline_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[PanelOutline],
                "temperature": 0.9,
            },
        )

        panels = TypeAdapter(
            list[PanelOutline]
        ).validate_python(
            json.loads(response.text)
        )

        if len(panels) != self.settings.panel_count:

            raise RuntimeError(
                "Gemini returned an unexpected number of panels."
            )

        return panels

    @staticmethod
    def _mock(
        request: PromptRequest,
    ):

        items = [

            (
                "The Beginning",
                (
                    f"{request.character_name} "
                    f"begins the adventure in "
                    f"{request.setting}."
                ),
            ),

            (
                "A Strange Sign",
                (
                    f"{request.character_name} "
                    f"discovers a mysterious clue."
                ),
            ),

            (
                "The Challenge",
                (
                    f"{request.character_name} "
                    f"faces the central challenge."
                ),
            ),

            (
                "The Turning Point",
                (
                    f"{request.character_name} "
                    f"finds a clever way forward."
                ),
            ),

            (
                "The Ending",
                (
                    f"{request.character_name} "
                    f"reaches a satisfying conclusion."
                ),
            ),
        ]

        return [

            PanelOutline(
                panel_number=i,
                title=title,
                scene_description=description,
                image_prompt=(
                    f"{request.art_style} comic illustration, "
                    f"{request.character_name}, "
                    f"{request.setting}, "
                    f"consistent character design"
                ),
            )

            for i, (title, description)
            in enumerate(items, start=1)
        ]