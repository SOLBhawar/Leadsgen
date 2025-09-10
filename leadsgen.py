import requests
import json
import argparse
from bs4 import BeautifulSoup
import google.generativeai as genai
import os
from dotenv import load_dotenv
import random
import re
load_dotenv()
GOOGLE_API = os.getenv("GOOGLE_API")

# Configure Gemini
genai.configure(api_key=GOOGLE_API)
model = genai.GenerativeModel("gemini-1.5-flash")

def fetch_companies(keyword, limit=5):
    """Fetch companies using Clearbit Autocomplete API."""
    url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={keyword}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception("Error fetching companies from Clearbit")
    return resp.json()[:limit]

def scrape_insights(domain, max_insights=4):
    """Scrape website for textual insights using BeautifulSoup."""
    if not domain:
        return ["No insights found"]
    url = f"http://{domain}"
    try:
        resp = requests.get(url, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")

        texts = [p.get_text(strip=True) for p in soup.find_all("p")]
        texts = [t for t in texts if len(t.split()) > 5]  # filter short lines

        # Filter out Cloudflare/security-page noise
        noise_patterns = [
            r"cloudflare",
            r"ray id",
            r"cf-ray",
            r"this website is using a security service",
            r"blocked",
            r"access denied",
            r"performance\s*&\s*security",
            r"your ip",
            r"ddos",
            r"captcha",
            r"malformed data",
            r"security solution",
            r"please include what you were doing",
            r"IP",
        ]
        texts = [t for t in texts if not any(re.search(p, t, re.IGNORECASE) for p in noise_patterns)]

        return random.sample(texts, min(len(texts), random.randint(2, max_insights)))
    except Exception as e:
        return ["No insights found"]

def generate_message(company, industry, insights):
    """Generate personalized outreach message body using Gemini (no greeting/signoff)."""
    prompt = f"""
    You are writing the BODY (no greeting, no sign-off) of a short, personalized B2B outreach note.
    Company: {company}
    Industry: {industry}
    Insights: {insights}

    Instructions:
    - Return ONLY the message body text (no greeting like "Hi" and no sign-off).
    - Do not use any placeholders or bracketed tokens such as [Name], {{Name}}, <Name>, or similar.
    - 40-80 words, specific, professional, and concise.
    - Naturally reference the insights when useful; skip if irrelevant.
    """
    response = model.generate_content(prompt)
    return response.text.strip() if response else ""


def sanitize_message(company, message: str) -> str:
    """Replace leftover placeholders and bracketed name/company tokens with the company name; strip stray brackets."""
    if not message:
        return message
    patterns = [
        r"\[[^\]]*Name[^\]]*\]",
        r"\{[^}]*Name[^}]*\}",
        r"<[^>]*Name[^>]*>",
        r"\[[^\]]*(Company|company)[^\]]*\]",
        r"\{[^}]*(Company|company)[^}]*\}",
        r"<[^>]*(Company|company)[^>]*>",
    ]
    for pat in patterns:
        message = re.sub(pat, company, message)
    # Remove any accidental double brackets around the company name
    message = message.replace(f"[{company}]", company).replace(f"{{{company}}}", company).replace(f"<{company}>", company)
    return message

def main():
    parser = argparse.ArgumentParser(description="B2B Lead Generator")
    parser.add_argument("--industry", required=True, help="Industry keyword")
    parser.add_argument("--size", default="50-200", help="Company size range")
    parser.add_argument("--location", default="Global", help="Company location")
    parser.add_argument("--output", default="leads.json", help="Output JSON file")
    args = parser.parse_args()

    companies = fetch_companies(args.industry)
    leads = []

    for comp in companies:
        company_name = comp.get("name")
        domain = comp.get("domain")
        insights = scrape_insights(domain)

        # Build lead first so values are clearly passed down
        lead = {
            "company_name": company_name,
            "domain": domain,
            "employee_range": args.size,
            "location": args.location,
            "insights": insights,
        }

        # Generate body after all fields are resolved, then compose greeting with company name
        body = generate_message(lead["company_name"], args.industry, lead["insights"]) or ""
        body = sanitize_message(lead["company_name"], body)
        lead["personalized_message"] = f"Hi {lead['company_name']},\n\n{body}".strip()

        leads.append(lead)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=4, ensure_ascii=True)

    print(f"Saved {len(leads)} leads to {args.output}")

if __name__ == "__main__":
    main()
