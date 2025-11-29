import os
import requests

from config import BASE_URL

# Meta / Facebook / Instagram
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")
META_PAGE_ID = os.getenv("META_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")

# Twitter (optional – simple stub)
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


def public_url(local_media_path: str) -> str:
    """
    Convert a relative media path (e.g. 'uploads/file.png')
    into a full URL (e.g. 'https://app.onrender.com/uploads/file.png').
    """
    fixed = local_media_path.replace("\\", "/")
    return f"{BASE_URL}/{fixed.lstrip('/')}"


# ---------------- FACEBOOK PAGE ---------------- #

def post_facebook_image(local_media_path: str, caption: str) -> dict:
    """
    Post an image to a Facebook Page using the Page access token.
    Uses /{PAGE_ID}/photos, not deprecated user endpoints.
    """
    if not META_PAGE_ACCESS_TOKEN or not META_PAGE_ID:
        raise RuntimeError("META_PAGE_ACCESS_TOKEN or META_PAGE_ID not set")

    image_url = public_url(local_media_path)

    url = f"https://graph.facebook.com/v20.0/{META_PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "published": "true",
        "access_token": META_PAGE_ACCESS_TOKEN,
    }

    r = requests.post(url, data=payload)
    data = r.json()
    if r.status_code != 200:
        raise RuntimeError(f"Facebook API error: {r.status_code}, {data}")
    return data


# ---------------- INSTAGRAM BUSINESS ---------------- #

def post_instagram_image(local_media_path: str, caption: str) -> dict:
    """
    Post an image to Instagram Business via IG Graph API.
    1) POST /{ig-user-id}/media
    2) POST /{ig-user-id}/media_publish
    """
    if not META_PAGE_ACCESS_TOKEN or not IG_USER_ID:
        raise RuntimeError("META_PAGE_ACCESS_TOKEN or IG_USER_ID not set")

    image_url = public_url(local_media_path)

    # Step 1: create media container
    create_url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    create_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": META_PAGE_ACCESS_TOKEN,
    }
    r = requests.post(create_url, data=create_payload)
    data = r.json()
    if r.status_code != 200:
        raise RuntimeError(
            f"Instagram create media error: {r.status_code}, {data}"
        )

    creation_id = data.get("id")
    if not creation_id:
        raise RuntimeError(f"Instagram create media error: missing id in {data}")

    # Step 2: publish
    publish_url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": META_PAGE_ACCESS_TOKEN,
    }
    r2 = requests.post(publish_url, data=publish_payload)
    data2 = r2.json()
    if r2.status_code != 200:
        raise RuntimeError(
            f"Instagram publish media error: {r2.status_code}, {data2}"
        )

    return data2


# ---------------- TWITTER / X (simple stub) ---------------- #

def post_twitter_image(local_media_path: str, caption: str) -> dict:
    """
    For this project we just simulate a Twitter post.
    You can extend this with Tweepy / official API if needed.
    """
    return {
        "status": "simulated",
        "caption": caption,
        "note": "Twitter/X posting not fully implemented in this demo.",
    }
