from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw

from app.config import Settings
from app.utils.files import safe_filename


class ImageGenerator:

    def __init__(
        self,
        settings: Settings,
    ):

        self.settings = settings

    def generate_image(
        self,
        prompt: str,
        panel_number: int = 1,
    ) -> Path:

        if self.settings.ai_mode.lower() == "mock":

            return self._mock_image(
                prompt,
                panel_number,
            )

        provider = self.settings.image_provider.lower()

        if provider == "hf":

            return self._huggingface_image(
                prompt,
                panel_number,
            )

        if provider == "local":

            return self._local_diffusers_image(
                prompt,
                panel_number,
            )

        raise RuntimeError(
            f"Unsupported IMAGE_PROVIDER: {provider}"
        )

    def _huggingface_image(
        self,
        prompt: str,
        panel_number: int,
    ):

        if not self.settings.hf_token:

            raise RuntimeError(
                "HF_TOKEN is not configured."
            )

        from huggingface_hub import InferenceClient

        client = InferenceClient(
            provider=self.settings.hf_provider,
            api_key=self.settings.hf_token,
        )

        image = client.text_to_image(
            prompt=prompt,
            model=self.settings.hf_image_model,
            width=self.settings.image_width,
            height=self.settings.image_height,
        )

        filename = (
            f"panel_{panel_number}_"
            f"{safe_filename(prompt[:35])}_"
            f"{uuid4().hex[:8]}.png"
        )

        path = self.settings.panel_dir / filename

        image.save(path)

        return path

    def _local_diffusers_image(
        self,
        prompt: str,
        panel_number: int,
    ):

        try:

            import torch

            from diffusers import (
                AutoPipelineForText2Image,
            )

        except ImportError as exc:

            raise RuntimeError(
                "Install requirements-local-diffusers.txt "
                "for local Diffusers mode."
            ) from exc

        device = self.settings.local_device

        if device == "auto":

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        dtype = (
            torch.float16
            if device == "cuda"
            else torch.float32
        )

        pipe = AutoPipelineForText2Image.from_pretrained(
            self.settings.local_image_model,
            torch_dtype=dtype,
        )

        pipe = pipe.to(device)

        image = pipe(
            prompt,
            width=self.settings.image_width,
            height=self.settings.image_height,
            num_inference_steps=28,
        ).images[0]

        filename = (
            f"panel_{panel_number}_"
            f"{safe_filename(prompt[:35])}_"
            f"{uuid4().hex[:8]}.png"
        )

        path = self.settings.panel_dir / filename

        image.save(path)

        return path

    def _mock_image(
        self,
        prompt: str,
        panel_number: int,
    ):

        image = Image.new(
            "RGB",
            (
                self.settings.image_width,
                self.settings.image_height,
            ),
            "white",
        )

        draw = ImageDraw.Draw(image)

        draw.rectangle(
            (
                12,
                12,
                self.settings.image_width - 12,
                self.settings.image_height - 12,
            ),
            outline="black",
            width=5,
        )

        draw.text(
            (35, 35),
            f"ComicCraft — Panel {panel_number}",
            fill="black",
        )

        draw.text(
            (35, 100),
            prompt[:180],
            fill="black",
        )

        filename = (
            f"mock_panel_{panel_number}_"
            f"{uuid4().hex[:8]}.png"
        )

        path = self.settings.panel_dir / filename

        image.save(path)

        return path