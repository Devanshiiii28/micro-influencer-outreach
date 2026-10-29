import re
import pandas as pd

ALIASES = {
    "name": ["name", "influencer name", "channel_title", "creator_name"],
    "platform": ["platform", "social platform"],
    "profile_url": ["profile_url", "profile url", "url", "channel_url"],
    "followers": ["followers", "follower_count", "subscribers", "subscriber_count"],
    "engagement_rate": ["engagement_rate", "engagement rate", "engagement_pct"],
    "category": ["category", "niche", "category / niche"],
    "content_themes": ["content_themes", "content themes", "themes", "description"],
    "email": ["email", "contact_email", "contact email"],
    "geography": ["geography", "location", "audience_geography"],
    "audience_age": ["audience_age", "audience age"],
    "audience_gender": ["audience_gender", "audience gender"],
    "website": ["website", "channel_website"],
    "recent_content": ["recent_content", "recent content", "recent_video_titles"],
}

def normalize_columns(df):
    df = df.copy()
    lookup = {str(c).strip().lower(): c for c in df.columns}
    rename = {}
    for canonical, options in ALIASES.items():
        for option in options:
            if option.lower() in lookup:
                rename[lookup[option.lower()]] = canonical
                break
    df = df.rename(columns=rename)
    return ensure_columns(df)

def ensure_columns(df):
    df = df.copy()
    defaults = {
        "name": "", "platform": "", "profile_url": "", "followers": 0,
        "engagement_rate": 0.0, "category": "", "content_themes": "",
        "email": "Not Found", "geography": "Not Available",
        "audience_age": "Not Available", "audience_gender": "Not Available",
        "website": "", "recent_content": ""
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
    df["followers"] = pd.to_numeric(df["followers"], errors="coerce").fillna(0).astype(int)
    df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce").fillna(0.0)
    df["email"] = df["email"].fillna("Not Found").astype(str).replace({"": "Not Found", "nan": "Not Found"})
    return df

def apply_filters(df, niche, min_followers=5000, max_followers=100000, min_engagement=1.0):
    out = ensure_columns(df)
    niche_match = out["category"].astype(str).str.contains(re.escape(niche), case=False, na=False) | out["content_themes"].astype(str).str.contains(re.escape(niche), case=False, na=False)
    follower_match = out["followers"].between(min_followers, max_followers, inclusive="both")
    engagement_match = out["engagement_rate"] >= min_engagement
    out["qualified"] = niche_match & follower_match & engagement_match
    def reason(row):
        reasons = []
        if not (min_followers <= row["followers"] <= max_followers): reasons.append("Follower count outside range")
        if float(row["engagement_rate"]) < min_engagement: reasons.append("Engagement below threshold")
        if not (re.search(re.escape(niche), str(row["category"]), re.I) or re.search(re.escape(niche), str(row["content_themes"]), re.I)):
            reasons.append("Niche/content mismatch")
        return "Passed all criteria" if not reasons else "; ".join(reasons)
    out["filter_reason"] = out.apply(reason, axis=1)
    return out

# def personalize_record(row, brand_name, product, brand_value):
#     name = str(row.get("name") or "there").strip()
#     first_name = name.split()[0] if name else "there"
#     niche = str(row.get("category") or "creator").strip()
#     themes = str(row.get("content_themes") or "").strip()
#     recent = str(row.get("recent_content") or "").strip()
#     signal = recent if recent and recent.lower() not in {"nan", "not available"} else (themes if themes else niche + " content")
#     email = (
#         f"Hi {first_name},\n\n"
#         f"I came across your {niche.lower()} work and liked the focus of your content around {signal}. "
#         f"We’re exploring a creator partnership for {product}, and your content may be a strong fit for the audience we want to reach. "
#         f"Through {brand_name}, we can offer {brand_value}. We’d be happy to discuss a concept that fits your style and gives you room to create in your own voice. "
#         f"If this sounds interesting, could I share the brief and proposed deliverables?\n\n"
#         f"Best,\n{brand_name} Team"
#     )
#     dm = f"Hi {first_name}! I liked your {niche.lower()} content on {signal}. Would you be open to discussing a {brand_name} creator collaboration?"
#     subject = f"Creator collaboration opportunity with {brand_name}"
#     return {"subject": subject, "email": email, "dm": dm}

def personalize_record(row, brand_name, product, brand_value):
    name = str(row.get("name") or "there").strip()
    first_name = name.split()[0] if name else "there"

    niche = str(row.get("category") or "creator").strip().lower()

    # Use content themes, never internal verification notes.
    themes = str(row.get("content_themes") or "").strip()
    theme = themes.split(",")[0].strip() if themes else f"{niche} content"
    theme = " ".join(theme.split()[:5])

    brand_name = str(brand_name or "Our Brand").strip()
    product = str(product or "our upcoming campaign").strip()
    brand_value = str(
        brand_value or "a paid collaboration with clear deliverables"
    ).strip()

    subject = f"Creator collaboration opportunity with {brand_name}"

    email = (
        f"Hi {first_name},\n\n"
        f"I enjoyed seeing your {niche} content, especially your focus on "
        f"{theme}. We’re exploring a creator partnership for {product}, "
        f"and your style may suit the audience we hope to reach. "
        f"{brand_name} can offer {brand_value}, with clear deliverables "
        f"and creative freedom to keep the content authentic to your voice. "
        f"Would you be open to reviewing a brief with the proposed concept, "
        f"timeline, and deliverables?\n\n"
        f"Best,\n{brand_name} Team"
    )

    dm = (
        f"Hi {first_name}! I like your {niche} content, especially "
        f"{theme}. Would you be open to discussing a paid "
        f"{brand_name} collaboration?"
    )

    return {
        "subject": subject,
        "email": email,
        "dm": dm
    }
