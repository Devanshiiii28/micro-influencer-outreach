import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# from src.core import normalize_columns, apply_filters, personalize_record, ensure_columns
# from src.storage import init_db, log_outreach, get_outreach_log, was_contacted
# from src.discovery_youtube import discover_youtube

try:
    from src.core import normalize_columns, apply_filters, personalize_record, ensure_columns
    from src.storage import init_db, log_outreach, get_outreach_log, was_contacted
    from src.discovery_youtube import discover_youtube
except ModuleNotFoundError as e:
    if e.name != "src":
        raise
    from core import normalize_columns, apply_filters, personalize_record, ensure_columns
    from storage import init_db, log_outreach, get_outreach_log, was_contacted
    from discovery_youtube import discover_youtube




load_dotenv()
st.set_page_config(page_title="Micro-Influencer Outreach", page_icon="📣", layout="wide")
init_db()

st.title(" AI Micro-Influencer Outreach System")
st.caption("Discover → Filter → Enrich → Personalize → Review → Simulate sending → Track")

with st.sidebar:
    st.header("Campaign settings")
    niche = st.selectbox("Target niche", ["Beauty", "Fashion", "Fitness", "Technology", "Gaming", "Lifestyle", "Parenting", "Fintech"])
    min_followers = st.number_input("Minimum followers", min_value=0, value=5000, step=1000)
    max_followers = st.number_input("Maximum followers", min_value=1000, value=100000, step=5000)
    min_engagement = st.number_input("Minimum engagement rate (%)", min_value=0.0, max_value=100.0, value=1.0, step=0.5)
    brand_name = st.text_input("Brand name", value="Your Brand")
    product = st.text_input("Product / campaign", value="our upcoming creator campaign")
    brand_value = st.text_input("Value proposition", value="a paid collaboration with clear deliverables")
    st.divider()
    st.info("Sending is simulated by default. Review each message before using any real email integration.")

tab_discover, tab_upload, tab_results, tab_log = st.tabs(["1. Discover", "2. Import dataset", "3. Filter & personalize", "4. Outreach tracker"])

with tab_discover:
    st.subheader("Discover public YouTube creators")
    st.write("Uses the official YouTube Data API. The API provides public channel metrics; it usually does not expose contact emails.")
    api_key = st.text_input("YouTube Data API key", value=os.getenv("YOUTUBE_API_KEY", ""), type="password")
    query = st.text_input("Search keywords", value=f"{niche} creator")
    count = st.slider("Number of channels to discover", min_value=10, max_value=100, value=50, step=10)
    if st.button("Discover creators", type="primary"):
        if not api_key:
            st.error("Add YOUTUBE_API_KEY to your .env file or enter it above.")
        else:
            with st.spinner("Calling YouTube Data API..."):
                try:
                    found = discover_youtube(api_key, query, count, niche)
                    st.session_state["influencers"] = normalize_columns(found)
                    st.success(f"Retrieved {len(found)} channel records. Check source metrics and data completeness before submission.")
                except Exception as e:
                    st.error(f"Discovery failed: {e}")
    st.caption("Use the API within its terms and quota limits. Discovery results are real API results, not a fabricated sample.")

with tab_upload:
    st.subheader("Import your own discovered influencers")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    st.markdown("Required fields: name, platform, profile_url, followers, engagement_rate, category, content_themes, email. Unknown email must be `Not Found`.")
    if uploaded:
        try:
            df = normalize_columns(pd.read_csv(uploaded))
            st.session_state["influencers"] = df
            st.success(f"Loaded {len(df)} records.")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
    template_path = "data/influencers_template.csv"
    if os.path.exists(template_path):
        with open(template_path, "rb") as f:
            st.download_button("Download CSV template", f, file_name="influencers_template.csv", mime="text/csv")

with tab_results:
    if "influencers" not in st.session_state:
        st.info("First discover creators with the API or import a CSV.")
    else:
        df = ensure_columns(st.session_state["influencers"])
        filtered = apply_filters(df, niche, int(min_followers), int(max_followers), float(min_engagement))
        st.subheader("Filtering results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Records loaded", len(df))
        c2.metric("Passed filters", int(filtered["qualified"].sum()))
        c3.metric("Failed filters", int((~filtered["qualified"]).sum()))
        st.dataframe(filtered[["name","platform","followers","engagement_rate","category","email","qualified","filter_reason"]], use_container_width=True)
        st.download_button("Download classified dataset", filtered.to_csv(index=False).encode("utf-8"), "classified_influencers.csv", "text/csv")

        qualified = filtered[filtered["qualified"]].copy()
        if not qualified.empty:
            st.subheader("Personalized outreach")
            selected_name = st.selectbox("Choose a qualified influencer", qualified["name"].astype(str).tolist())
            row = qualified[qualified["name"].astype(str) == selected_name].iloc[0].to_dict()
            messages = personalize_record(row, brand_name, product, brand_value)
            st.markdown("**Email subject**")
            st.code(messages["subject"])
            st.markdown("**Email pitch**")
            st.write(messages["email"])
            st.caption(f"Email word count: {len(messages['email'].split())} words")
            st.markdown("**Instagram DM**")
            st.write(messages["dm"])
            st.caption(f"DM word count: {len(messages['dm'].split())} words")
            email = str(row.get("email", "Not Found")).strip()
            valid_email = "@" in email and "." in email.split("@")[-1] and email.lower() != "not found"
            st.write(f"Contact email: **{email if email else 'Not Found'}**")
            if was_contacted(str(row.get("profile_url", ""))):
                st.warning("This profile already exists in the outreach log. Duplicate outreach is blocked.")
            else:
                if st.button("Simulate email send and log", type="primary"):
                    status = "SIMULATED_SENT" if valid_email else "SKIPPED_NO_VALID_EMAIL"
                    log_outreach(
                        name=str(row.get("name", "")),
                        profile_url=str(row.get("profile_url", "")),
                        email=email or "Not Found",
                        subject=messages["subject"],
                        email_message=messages["email"],
                        dm_message=messages["dm"],
                        status=status
                    )
                    st.success(f"Logged status: {status}. No email was actually sent.")
            st.download_button("Download this message bundle", pd.DataFrame([{
                "name": row.get("name"), "email": email, "subject": messages["subject"],
                "email_pitch": messages["email"], "instagram_dm": messages["dm"]
            }]).to_csv(index=False).encode("utf-8"), "personalized_message.csv", "text/csv")

with tab_log:
    st.subheader("Outreach tracker")
    log_df = get_outreach_log()
    if log_df.empty:
        st.info("No outreach records yet.")
    else:
        st.dataframe(log_df, use_container_width=True)
        st.download_button("Download outreach log", log_df.to_csv(index=False).encode("utf-8"), "outreach_log.csv", "text/csv")
