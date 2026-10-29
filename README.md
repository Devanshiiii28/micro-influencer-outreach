# Automated Micro-Influencer Outreach System

A Python and Streamlit prototype for discovering or importing creator profiles, classifying influencers against campaign criteria, generating personalized outreach drafts, and tracking simulated outreach in SQLite.

## Features

- Discover YouTube channel records using the official YouTube Data API v3.
- Import creator profiles from CSV files, including Instagram profiles.
- Filter by niche, follower count, and engagement rate.
- Display qualification status and reasons for failed filters.
- Preserve unknown email addresses as `Not Found`.
- Generate personalized email pitches and Instagram DMs.
- Export classified datasets, personalized messages, and outreach logs.
- Track outreach status and timestamps in SQLite.
- Prevent duplicate outreach records using profile URLs.
- Simulate sending without automatically sending real messages.

## Technology Stack

- Python
- Streamlit
- Pandas
- SQLite
- Requests
- python-dotenv
- YouTube Data API v3 for optional live discovery

## Requirements

- Python 3.10 or newer
- Internet connection for live YouTube discovery
- YouTube Data API v3 key for live discovery; optional when importing CSV data

## Setup on Windows

1. Open the `micro_influencer_outreach` project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Optionally copy `.env.example` to `.env` and configure your YouTube API key. Do not commit API keys or secrets to GitHub.
6. Run the application:

   ```powershell
   python -m streamlit run app.py
   ```

7. Open the local URL displayed in the terminal, usually `http://localhost:8501`.

If PowerShell activation is blocked, run the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Data Sources and Discovery

The application supports two input approaches:

1. **YouTube API discovery:** Uses the YouTube Data API v3 to search for channels and retrieve available public channel and video statistics.
2. **CSV import:** Allows creator records from permitted public sources to be imported for classification and personalization.

The current test dataset is `data/india_beauty_influencers_50.csv`. It contains 50 India-focused beauty creator records assembled from a third-party ranking. The follower counts, engagement estimates, profile details, and current activity have not all been independently verified. Treat these values as preliminary and verify them against the creators' current public profiles before outreach.

The API does not reliably provide business email addresses or audience demographics for every creator. Missing email addresses are recorded as `Not Found`, and unavailable demographics as `Not Available`. Do not invent missing information.

## Filtering Methodology

A creator passes the configured filters only when all applicable conditions are met:

- The selected niche matches the creator's category or content themes.
- The follower count falls within the configured minimum and maximum.
- The engagement rate meets or exceeds the configured threshold.

The application displays the number of records loaded, records that passed, records that failed, and reasons for failure.

For YouTube records, the public subscriber count is used as the follower-equivalent metric. For imported records, the follower and engagement values depend on the supplied dataset and its source.

The assignment's typical micro-influencer range is 5,000–100,000 followers. Classification is only as reliable as the imported data.

## Personalization

The application generates an email pitch and Instagram DM using available creator fields and campaign settings, including:

- Creator name
- Category and content themes
- Brand name
- Product or campaign
- Value proposition

The personalization function uses content themes rather than internal verification notes. The intended assignment limits are:

- Email pitch: 60–90 words
- Instagram DM: 15–30 words

Review the generated drafts and displayed word counts before using them. Verify that any creator-specific references accurately describe recent public content.

## Outreach Tracking and Duplicate Prevention

The application records outreach attempts in SQLite and provides an exportable outreach log.

Expected statuses include:

- `SIMULATED_SENT` when a plausible email address is available and the simulation runs
- `SKIPPED_NO_VALID_EMAIL` when no valid email address is available

Duplicate profile URLs are blocked by the tracking database. The application does not send real emails or Instagram messages.

Any future production sending integration should use authorized APIs, explicit human approval, appropriate rate limits, error handling, and applicable consent and unsubscribe procedures. Do not bypass Instagram or Meta platform restrictions.

## Project Structure

```text
micro_influencer_outreach/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   ├── influencers_template.csv
│   ├── demo_influencers.csv
│   ├── mrunal_panchal.csv
│   └── india_beauty_influencers_50.csv
├── src/
│   ├── core.py
│   ├── discovery_youtube.py
│   └── storage.py
└── outreach.db
```

The SQLite database is created or updated when the application runs. Exported CSV files and screenshots may be stored separately in an `outputs/` and `screenshots/` folder.

## Outputs

Depending on the workflow and export buttons used, the application can produce:

- Classified influencer dataset
- Personalized email and DM bundle
- Outreach log
- SQLite outreach database

Use the actual downloaded filenames when documenting your final submission.

## Limitations

- YouTube discovery depends on API quota, search terms, and public data availability.
- Imported profile metrics may be stale or inaccurate.
- Engagement rates from different platforms and data providers may not be directly comparable.
- Public profile data does not guarantee a verified business email or audience demographics.
- The system does not automatically send real outreach.
- Generated messages require human review.
- A dataset containing 50 records does not, by itself, establish that all 50 are verified or qualified micro-influencers.

## Submission Checklist

- [ ] At least 50 real creator records, with profile sources and verification dates documented
- [ ] Classified dataset with pass/fail status and reasons
- [ ] Personalized email and DM drafts for qualified creators
- [ ] Outreach tracker export
- [ ] Screenshots or a short demo video
- [ ] README covering setup, APIs, methodology, limitations, and data sources
- [ ] No API keys, passwords, or other secrets committed to the repository

