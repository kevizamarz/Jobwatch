import json
import re

from playwright.sync_api import sync_playwright

from database import save_job_if_new


COMPANIES_FILE = "companies.json"


# ============================================================
# COMPANY CONFIG
# ============================================================

def load_companies():
    with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# JOB FILTER
# ============================================================

def is_relevant(title):
    title = title.lower()

    # Technical jobs
    technical_keywords = [
        "software",
        "developer",
        "development",
        "devops",
        "cloud",
        "sre",
        "site reliability",
        "platform",
        "backend",
        "frontend",
        "full stack",
        "fullstack",
    ]

    if any(keyword in title for keyword in technical_keywords):
        return True

    # Internships - only technical/engineering-related ones
    if "intern" in title or "internship" in title:
        engineering_keywords = [
            "engineering",
            "software",
            "cloud",
            "devops",
            "development",
            "technical",
            "platform",
        ]

        return any(
            keyword in title
            for keyword in engineering_keywords
        )

    return False


# ============================================================
# WORKDAY DETECTION
# ============================================================

def is_workday(url):
    """
    Determine whether a URL belongs to a Workday job site.
    """

    url = url.lower()

    workday_domains = [
        "myworkdaysite.com",
        "myworkdayjobs.com",
    ]

    return any(
        domain in url
        for domain in workday_domains
    )


# ============================================================
# WORKDAY JOB ID
# ============================================================

def extract_job_id(href):
    """
    Workday URLs normally contain IDs such as:
        _R261548
        _R250904
    """

    if not href:
        return None

    match = re.search(r"_([A-Z]\d+)", href)

    if match:
        return match.group(1)

    return None


# ============================================================
# WORKDAY SCRAPER
# ============================================================

def scrape_workday(page, company_name):
    print(f"Scraping Workday page for {company_name}...")

    # Allow Workday's JavaScript application to load
    page.wait_for_timeout(10000)

    job_titles = page.locator(
        '[data-automation-id="jobTitle"]'
    )

    count = job_titles.count()

    print("Jobs found:", count)

    jobs = []

    for i in range(count):

        job = job_titles.nth(i)

        try:
            title = job.inner_text().strip()
            href = job.get_attribute("href")
        except Exception:
            continue

        if not title or not href:
            continue

        if not is_relevant(title):
            continue

        job_id = extract_job_id(href)

        if not job_id:
            continue

        jobs.append({
            "company": company_name,
            "title": title,
            "id": job_id,
        })

    return jobs


# ============================================================
# ITPRO SCRAPER
# ============================================================

def scrape_itpro(page, company_name):
    print(f"Scraping ITPro page for {company_name}...")

    page.wait_for_timeout(3000)

    jobs = []

    # IMPORTANT:
    # Only actual job cards.
    # This prevents sidebar/category links from being treated
    # as jobs.
    job_cards = page.locator("article.job-card")

    count = job_cards.count()

    print("Actual job cards:", count)

    for i in range(count):

        card = job_cards.nth(i)

        try:
            # Example:
            # <h2 class="jc-title">Senior Backend Engineer</h2>

            title_element = card.locator("h2.jc-title")

            title = title_element.inner_text().strip()

            # Example:
            # <article class="job-card" id="14902">

            job_id = card.get_attribute("id")

            # Job URL
            link = card.locator("a").first

            href = link.get_attribute("href")

        except Exception:
            continue

        if not title or not job_id:
            continue

        if not is_relevant(title):
            continue

        jobs.append({
            "company": company_name,
            "title": title,
            "id": job_id,
            "url": href,
        })

    print("Relevant jobs found:", len(jobs))

    return jobs


# ============================================================
# SAVE NEW JOBS
# ============================================================

def save_new_jobs(jobs):
    new_jobs = []

    for job in jobs:

        try:
            if save_job_if_new(job):
                new_jobs.append(job)

        except Exception as e:
            print(
                f"ERROR saving job "
                f"{job.get('company')} | "
                f"{job.get('title')} | "
                f"{job.get('id')}: {e}"
            )

    return new_jobs


# ============================================================
# MAIN
# ============================================================

def main():

    companies = load_companies()

    all_new_jobs = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        for company in companies:

            name = company["name"]
            url = company["url"]
            company_type = company.get("type", "").lower()

            print("\n" + "=" * 50)
            print(f"Checking {name}")
            print("=" * 50)

            # ------------------------------------------------
            # WSO2 / Cloudflare
            # ------------------------------------------------

            if company_type == "cloudflare":
                print("Skipping Cloudflare site for now.")
                continue

            page = browser.new_page()

            try:

                print("Opening page...")

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                print("Title:", page.title())

                # ------------------------------------------------
                # WORKDAY
                # ------------------------------------------------

                if is_workday(url):

                    jobs = scrape_workday(
                        page,
                        name
                    )

                # ------------------------------------------------
                # ITPRO
                # ------------------------------------------------

                elif company_type == "itpro":

                    jobs = scrape_itpro(
                        page,
                        name
                    )

                # ------------------------------------------------
                # UNKNOWN SITE
                # ------------------------------------------------

                else:

                    print(
                        f"Unsupported company type: "
                        f"{company_type or 'not specified'}"
                    )

                    jobs = []

                # ------------------------------------------------
                # DATABASE
                # ------------------------------------------------

                new_jobs = save_new_jobs(jobs)

                print("\n--- NEW JOBS ---")

                for job in new_jobs:

                    print(
                        f"{job['company']} | "
                        f"{job['title']} | "
                        f"{job['id']}"
                    )

                print("-------------------------")
                print("New jobs:", len(new_jobs))

                all_new_jobs.extend(new_jobs)

            except Exception as e:

                print(
                    f"ERROR checking {name}: {e}"
                )

            finally:

                page.close()

        browser.close()

    # ========================================================
    # TOTAL
    # ========================================================

    print("\n" + "=" * 50)
    print("TOTAL NEW JOBS")
    print("=" * 50)

    for job in all_new_jobs:

        print(
            f"{job['company']} | "
            f"{job['title']} | "
            f"{job['id']}"
        )

    print("-------------------------")
    print(
        f"Total new jobs: "
        f"{len(all_new_jobs)}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
