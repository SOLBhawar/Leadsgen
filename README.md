# LeadsGen

Generate a small list of B2B leads from Clearbit Autocomplete, scrape light on-site insights, and create a short personalized message with Google Gemini.

## Requirements
- Python 3.9+
- A Google Gemini API key (for content generation)

## Install dependencies
It's recommended to use a virtual environment, but not required.

```powershell
# From the project root
python -m pip install --upgrade pip;
python -m pip install requests beautifulsoup4 google-generativeai python-dotenv
```

## Configure your Gemini API key
Create a `.env` file in the project root with your key:

```
GOOGLE_API=YOUR_GEMINI_API_KEY
```

## Usage
Basic example (writes to `leads.json`):

```powershell
python .\leadsgen.py --industry "fintech" --size "200-500" --location "Europe"
```

Optional flags:
- `--output` to choose a different output file (default: `leads.json`)

## Example output (truncated)
```json
[
  {
    "company_name": "Acme Fintech",
    "domain": "acmefintech.com",
    "employee_range": "200-500",
    "location": "Europe",
    "insights": [
      "Acme provides modern payment APIs for European SMEs.",
      "Focus on compliance and PSD2-ready integrations."
    ],
    "personalized_message": "Hi Acme Fintech,\n\nAppreciate your focus on PSD2 and SME payment APIs. We help fintech teams accelerate rollouts while keeping compliance tight—especially around auth and reconciliation. If helpful, I can share a short outline on reducing integration time across your EU corridors."
  },
  {
    "company_name": "NovaPay",
    "domain": "novapay.io",
    "employee_range": "200-500",
    "location": "Europe",
    "insights": [
      "Cross-border remittance and FX features",
      "Mobile-first onboarding"
    ],
    "personalized_message": "Hi NovaPay,\n\nYour mobile-first onboarding and cross‑border focus stand out. We’ve supported teams improving FX transparency and onboarding funnels without adding friction. Happy to share examples and see if they map to your next release."
  }
]
```

## Why Clearbit instead of Apollo?
- Clearbit Autocomplete is open and simple to query for domains and company names.
- Apollo does not provide API access on the Pro trial, so it cannot be used reliably for automated lead generation in this script.

## Can we improve this?
Yes—if we had a proper, fully functioning API with reliable access and filters, we could:
- Pull richer firmographics (industry, size, location) directly without scraping
- Support advanced filtering and pagination for larger batches
- Improve enrichment accuracy and reduce noise in insights
- Add better deduplication and domain confidence scoring

## Troubleshooting
- Few or no leads? Try a broader `--industry` term.
- Empty or generic insights? Some sites block scraping or have minimal public content.
- Message generation fails? Verify `.env` contains a valid `GOOGLE_API` and there’s network access.
