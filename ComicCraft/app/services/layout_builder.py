from pathlib import Path
from typing import List

from app.schemas import PanelStory


def build_comic_layout(
    story: List[PanelStory],
    image_paths: List[Path],
) -> list[dict]:
    """
    Combine generated story information with generated
    image paths into the final comic panel layout.
    """

    if len(story) != len(image_paths):
        raise ValueError(
            "Story panels and image paths must have the same length."
        )

    layout = []

    for panel, image_path in zip(story, image_paths):
        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image_path": str(image_path),
                "scene_description": panel.scene_description,
                "caption": panel.caption,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
            }
        )

    return layout