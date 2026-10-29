import requests
from statistics import mean

BASE = "https://www.googleapis.com/youtube/v3"

def _get(endpoint, params):
    response = requests.get(f"{BASE}/{endpoint}", params=params, timeout=25)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "YouTube API error"))
    return payload

def discover_youtube(api_key, query, count=50, niche="Technology"):
    """Discover real YouTube channels via the official YouTube Data API v3."""
    found = {}
    page_token = None
    while len(found) < count:
        params = {"part": "snippet", "q": query, "type": "channel", "maxResults": min(50, count-len(found)), "key": api_key}
        if page_token:
            params["pageToken"] = page_token
        data = _get("search", params)
        for item in data.get("items", []):
            channel_id = item.get("id", {}).get("channelId")
            if channel_id:
                found[channel_id] = item.get("snippet", {})
        page_token = data.get("nextPageToken")
        if not page_token or not data.get("items"):
            break

    ids = list(found.keys())
    records = []
    for start in range(0, len(ids), 50):
        batch = ids[start:start+50]
        channel_data = _get("channels", {"part":"snippet,statistics,brandingSettings", "id":",".join(batch), "key":api_key})
        for ch in channel_data.get("items", []):
            stats = ch.get("statistics", {})
            snippet = ch.get("snippet", {})
            subs = int(stats.get("subscriberCount", 0) or 0)
            channel_id = ch["id"]
            # Recent video stats provide a rough public interaction rate when available.
            search = _get("search", {"part":"snippet", "channelId":channel_id, "type":"video", "order":"date", "maxResults":5, "key":api_key})
            video_ids = [v.get("id", {}).get("videoId") for v in search.get("items", []) if v.get("id", {}).get("videoId")]
            rates = []
            titles = []
            if video_ids:
                video_data = _get("videos", {"part":"statistics,snippet", "id":",".join(video_ids), "key":api_key})
                for video in video_data.get("items", []):
                    vstats = video.get("statistics", {})
                    views = int(vstats.get("viewCount", 0) or 0)
                    likes = int(vstats.get("likeCount", 0) or 0)
                    comments = int(vstats.get("commentCount", 0) or 0)
                    if views > 0:
                        rates.append((likes + comments) / views * 100)
                    title = video.get("snippet", {}).get("title")
                    if title:
                        titles.append(title)
            description = snippet.get("description", "")
            links = snippet.get("customUrl", "")
            handle = links.lstrip("@")
            profile_url = f"https://www.youtube.com/@{handle}" if handle else f"https://www.youtube.com/channel/{channel_id}"
            records.append({
                "name": snippet.get("title", "Unknown"),
                "platform": "YouTube",
                "profile_url": profile_url,
                "followers": subs,
                "engagement_rate": round(mean(rates), 2) if rates else 0.0,
                "category": niche,
                "content_themes": description[:500],
                "email": "Not Found",
                "geography": snippet.get("country", "Not Available"),
                "audience_age": "Not Available",
                "audience_gender": "Not Available",
                "website": "",
                "recent_content": " | ".join(titles[:3]),
                "data_source": "YouTube Data API v3"
            })
    return records
