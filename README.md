# JobWatch

JobWatch is a lightweight job monitoring system designed to periodically check multiple career websites for newly published positions that match a defined set of technical and internship related keywords.

The project is designed to run on a personal homelab server and uses browser automation where necessary, PostgreSQL for persistent job tracking, and Telegram for notifications.

## Project Goals

JobWatch is intended to:

1. Monitor multiple job sources from a single application
2. Support different website structures through source specific scrapers
3. Filter jobs according to software engineering, DevOps, cloud, platform, development, and internship related criteria
4. Detect jobs that have not previously been seen
5. Persist previously discovered jobs in PostgreSQL
6. Send a consolidated Telegram notification when new jobs are found
7. Run automatically at a regular interval on a server

## Current Architecture

The application follows this general flow:

    Job Sources
        |
        v
    Playwright or HTML scraper
        |
        v
    Relevant Job Filter
        |
        v
    Job ID Extraction
        |
        v
    PostgreSQL Deduplication
        |
        v
    New Jobs Collection
        |
        v
    Telegram Notification

Different websites can use different scraping strategies. Workday based career pages use their structured job elements, while other supported sources can use source specific HTML selectors.

## Technology Stack

Python

Playwright

PostgreSQL

Neon PostgreSQL

Telegram Bot API

Requests

Git and GitHub

Linux

## Project Structure

    jobwatch/
    |
    ├── jobwatch.py
    ├── database.py
    ├── companies.json
    ├── test_database.py
    ├── career_page.html
    ├── .gitignore
    └── venv/

### jobwatch.py

Main application containing:

1. Company configuration loading
2. Website selection
3. Browser based scraping
4. Source specific scraping logic
5. Job relevance filtering
6. Job ID extraction
7. New job collection
8. Telegram notification handling

### database.py

Contains the PostgreSQL connection and job persistence logic.

The database is used to prevent the same job from being reported repeatedly.

### companies.json

Contains the configured job sources.

A source entry follows this general structure:

    {
        "name": "Source Name",
        "type": "source_type",
        "url": "https://example.com/jobs"
    }

The source name identifies where the job was discovered. It does not necessarily represent the employer.

### test_database.py

Contains database related tests.

### career_page.html

A locally stored HTML page that can be useful for development and testing of scraping logic without repeatedly requesting the live website.

## Job Relevance Filtering

JobWatch currently focuses on positions related to areas such as:

Software

Developer

Development

DevOps

Cloud

SRE

Site Reliability

Platform

Backend

Frontend

Full Stack

Fullstack

Intern

Internship

For internship positions, additional engineering and technical keywords are considered to reduce unrelated internship results.

The filtering logic can be expanded as additional job sources and requirements are introduced.

## Database

JobWatch uses PostgreSQL for persistent storage.

The database stores information required to identify previously discovered jobs, including:

Company

Job title

Job ID

The application uses database conflict handling so that an existing job is not reported again.

The database connection is supplied through the DATABASE_URL environment variable.

Example:

    export DATABASE_URL="your_database_connection_string"

The actual database credentials must never be committed to GitHub.

## Telegram Notifications

JobWatch uses the Telegram Bot API to notify the user when new jobs are discovered.

The bot token and chat ID are supplied through environment variables.

Set them on the server with:

    export TELEGRAM_BOT_TOKEN="your_bot_token"
    export TELEGRAM_CHAT_ID="your_chat_id"

The application only sends a notification when at least one genuinely new job has been found.

Multiple new jobs discovered during one run are combined into a single Telegram message.

A typical notification contains:

    JobWatch: New Jobs

    Company
    Job title
    Job ID

Sensitive credentials must never be stored directly inside the Python source code.

## Local Setup

Clone the repository:

    git clone git@github.com:YOUR_USERNAME/Jobwatch.git

Enter the project:

    cd Jobwatch

Create a virtual environment:

    python3 -m venv venv

Activate it:

    source venv/bin/activate

Install dependencies:

    pip install playwright requests psycopg

Install the required Playwright browser:

    playwright install chromium

On Debian or Ubuntu systems, browser dependencies may also be required:

    playwright install-deps chromium

## Environment Variables

Before running JobWatch, configure the required environment variables.

    export DATABASE_URL="your_database_connection_string"
    export TELEGRAM_BOT_TOKEN="your_bot_token"
    export TELEGRAM_CHAT_ID="your_chat_id"

For a permanent server configuration, these values can be supplied through a secure environment configuration rather than committed to the repository.

## Running JobWatch

Activate the virtual environment:

    source venv/bin/activate

Run:

    python jobwatch.py

The application checks each configured source and reports the number of newly discovered relevant jobs.

Example:

    Checking Source
    Opening page...
    Jobs found: 20

    --- NEW JOBS ---

    Source | Example Technical Internship | 12345

    -------------------------
    Total new jobs: 1

If no new jobs are found, no Telegram notification is sent.

## Source Specific Scraping

JobWatch does not assume that every career website has the same HTML structure.

For example, Workday based sites can expose structured elements such as:

    [data-automation-id="jobTitle"]

Other websites may require selectors specific to their job card structure.

This source specific approach is intentional. A universal scraper based only on generic links is unreliable because career websites use different HTML structures, JavaScript rendering systems, pagination methods, and anti bot mechanisms.

The application therefore uses a common interface for job data while allowing each source to have its own extraction implementation.

## Error Handling

A failure on one source should not prevent the remaining sources from being checked.

Sources that cannot currently be accessed because of anti bot protection or incompatible page structures can be skipped while the rest of the monitoring process continues.

This allows the system to remain useful even when individual websites change or become temporarily unavailable.

## Security

Never commit any of the following:

Database credentials

Telegram bot tokens

Private API keys

Server credentials

Personal access tokens

Environment files containing secrets

The .gitignore file should exclude local virtual environments, Python cache files, and environment files.

Before pushing changes to GitHub, check:

    git status

and:

    git diff

to ensure that no credentials are included.

## Development Workflow

A typical development workflow is:

    Edit source
        |
        v
    Run locally
        |
        v
    Test scraper
        |
        v
    Test database behavior
        |
        v
    Test Telegram notification
        |
        v
    Commit changes
        |
        v
    Push to GitHub

Use descriptive commits that explain what changed.

Examples:

    feat: add Telegram notifications
    feat: add new job source
    fix: correct job company extraction
    fix: handle unavailable career page
    test: add database tests

## Current MVP

The current MVP provides:

1. Multiple job source configuration
2. Support for different scraping strategies
3. Browser automation using Playwright
4. Technical and internship job filtering
5. Job ID extraction
6. PostgreSQL based persistence
7. Duplicate job prevention
8. Employer extraction for supported sources
9. Consolidated Telegram notifications
10. Linux server compatibility
11. Git based source control

## Planned Improvements

The next improvements can include:

1. Automatic scheduled execution
2. Better logging
3. Improved retry and timeout handling
4. More robust source specific scrapers
5. Additional job sources
6. Improved database constraints
7. Automated tests for scraper behavior
8. Docker containerization
9. CI/CD using GitHub Actions
10. Monitoring and health checks

Docker and CI/CD should be added after the application behavior is stable so that deployment automation does not hide application level problems.

## Scalability

The architecture is designed around multiple independent job sources rather than a single scraper.

Each source can have its own extraction logic while producing the same normalized job structure:

    {
        "source": "Source Name",
        "company": "Employer",
        "title": "Job title",
        "id": "Job ID"
    }

This makes it possible to add new sources without rewriting the entire application.

As the number of sources grows, source specific scraper modules can be separated into their own files.

For example:

    scrapers/
    ├── workday.py
    ├── itpro.py
    └── other_source.py

The main application can then orchestrate the scrapers while the individual modules handle website specific behavior.

## Homelab Deployment

JobWatch is currently intended to run on a Linux homelab server.

The server is responsible for:

1. Running the Python application
2. Accessing configured career websites
3. Connecting to the PostgreSQL database
4. Sending Telegram notifications
5. Running the application on a regular schedule

