import datetime
import os
from pathlib import Path
from typing import List, Optional

from config import UPLOAD_DIR
from db import SessionLocal, Post
from media_utils import add_brand_overlay
from social_connectors import (
    post_facebook_image,
    post_instagram_image,
    post_twitter_image,
)


def _most_recent_media() -> Optional[str]:
    """
    Returns path relative to project root (e.g. 'uploads/file.png')
    for the most recently modified file in UPLOAD_DIR.
    """
    files = list(UPLOAD_DIR.glob("*"))
    if not files:
        return None
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest = files[0]
    return latest.relative_to(UPLOAD_DIR.parent).as_posix()


def run_agent_create_and_post(
    prompt: str, platforms: List[str], scheduled_time: Optional[str]
) -> dict:
    """
    Core agent logic:
      1. Pick latest media in uploads/
      2. Brand it
      3. Use prompt as caption (you can plug OpenAI here)
      4. If scheduled_time provided -> store as scheduled
         else -> post immediately to each platform
      5. Save records in DB and return JSON for frontend
    """
    db = SessionLocal()
    posts_out = []
    media_rel = _most_recent_media()
    if not media_rel:
        return {
            "error": "No media found. Please upload an image first.",
            "posts": [],
        }

    # Step 2: brand overlay
    branded_rel = add_brand_overlay(media_rel)

    # Step 3: caption – use prompt as caption for now
    caption = prompt.strip() or "New post from Jeng Frames ✨"

    # Step 4: scheduling
    scheduled_dt = None
    if scheduled_time:
        try:
            scheduled_dt = datetime.datetime.fromisoformat(scheduled_time)
        except Exception:
            scheduled_dt = None

    for platform in platforms:
        platform = platform.lower()
        post = Post(
            platform=platform,
            caption=caption,
            media_path=media_rel,
            branded_path=branded_rel,
            status="scheduled" if scheduled_dt else "posting",
            scheduled_time=scheduled_dt,
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        result = {
            "post_id": post.id,
            "platform": platform,
            "status": post.status,
            "scheduled_time": str(post.scheduled_time)
            if post.scheduled_time
            else None,
        }

        # If no schedule → try to post now
        if not scheduled_dt:
            try:
                if platform == "facebook":
                    api_res = post_facebook_image(branded_rel, caption)
                elif platform == "instagram":
                    api_res = post_instagram_image(branded_rel, caption)
                elif platform == "twitter":
                    api_res = post_twitter_image(branded_rel, caption)
                else:
                    api_res = {"status": "skipped", "reason": "unsupported"}

                post.status = "posted"
                post.posted_at = datetime.datetime.utcnow()
                post.platform_post_id = str(api_res.get("id", ""))
                db.add(post)
                db.commit()
                result["status"] = "posted"
            except Exception as e:
                post.status = "error"
                post.error = str(e)
                db.add(post)
                db.commit()
                result["status"] = "error"
                result["error"] = str(e)

        posts_out.append(result)

    db.close()
    return {
        "media": media_rel,
        "branded": branded_rel,
        "posts": posts_out,
    }
