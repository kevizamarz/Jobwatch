import os
import requests

from database import get_jobs


PAGE_SIZE = 10


def send_telegram_message(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=15
    )

    response.raise_for_status()


def get_telegram_updates(offset=None):
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    url = f"https://api.telegram.org/bot{token}/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    response = requests.get(
        url,
        params=params,
        timeout=40
    )

    response.raise_for_status()

    return response.json()["result"]


def send_jobs_page(page_number):
    offset = (page_number - 1) * PAGE_SIZE

    jobs = get_jobs(
        limit=PAGE_SIZE,
        offset=offset
    )

    if not jobs:
        send_telegram_message(
            "JobWatch\n\n"
            "No more jobs available."
        )
        return

    message = (
        f"JobWatch - Current Jobs\n"
        f"Page {page_number}\n\n"
    )

    for company, title, job_id in jobs:
        message += (
            f"{company}\n"
            f"{title}\n"
            f"{job_id}\n\n"
        )

    if len(jobs) == PAGE_SIZE:
        message += (
            f"Use /jobs {page_number + 1} "
            f"for the next page."
        )

    if page_number > 1:
        message += (
            f"\nUse /jobs {page_number - 1} "
            f"for the previous page."
        )

    send_telegram_message(message)


def check_telegram_commands():
    updates = get_telegram_updates()

    for update in updates:

        message = update.get("message")

        if not message:
            continue

        text = message.get("text", "").strip()

        if text == "/jobs":
            send_jobs_page(1)

        elif text.startswith("/jobs "):

            try:
                page_number = int(
                    text.split()[1]
                )

                if page_number < 1:
                    raise ValueError

                send_jobs_page(page_number)

            except (ValueError, IndexError):
                send_telegram_message(
                    "Usage:\n"
                    "/jobs\n"
                    "/jobs 2\n"
                    "/jobs 3"
                )


if __name__ == "__main__":

    print("JobWatch Telegram bot started.")

    offset = None

    while True:

        try:
            updates = get_telegram_updates(offset)

            for update in updates:

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                text = message.get("text", "").strip()

                if text == "/jobs":
                    send_jobs_page(1)

                elif text.startswith("/jobs "):

                    try:
                        page_number = int(
                            text.split()[1]
                        )

                        if page_number < 1:
                            raise ValueError

                        send_jobs_page(page_number)

                    except (ValueError, IndexError):

                        send_telegram_message(
                            "Usage:\n"
                            "/jobs\n"
                            "/jobs 2\n"
                            "/jobs 3"
                        )

        except Exception as e:

            print(
                f"Telegram error: {e}"
            )
