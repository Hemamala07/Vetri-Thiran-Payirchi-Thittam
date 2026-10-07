def payload():

    return {
        "story_prompt": (
            "A brave fox explores "
            "an enchanted forest."
        ),

        "character_name": "Lumi",

        "setting": "forest",

        "tone": "dramatic",

        "art_style": "comic book",
    }


def test_home(client):

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_json_generation_in_mock_mode(client):

    response = client.post(
        "/generate-comic/json",
        json=payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(data["panels"]) == 5

    assert len(data["layout"]) == 5

    assert data["pdf_url"].endswith(".pdf")


def test_form_generation_in_mock_mode(client):

    response = client.post(
        "/generate",
        data=payload(),
    )

    assert response.status_code == 200

    assert (
        "Download Your Comic as PDF"
        in response.text
    )


def test_image_route_in_mock_mode(client):

    response = client.post(
        "/test-image",
        json={
            "prompt":
                "A fox in a magical forest"
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["success"]
        is True
    )