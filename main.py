import requests
import asyncio
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# ---------------- CONFIG ---------------- #
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

PRODUCT_URL = "https://www.jiomart.com/p/groceries/onion-1-kg-pack/611163418"
PINCODE = "733134"

CHECK_INTERVAL = 300  # seconds (5 minutes)
# ---------------------------------------- #

bot = Bot(token=BOT_TOKEN)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-IN,en;q=0.9"
}

last_stock_status = False  # False = out of stock, True = in stock


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def check_stock():
    try:
        session = requests.Session()
        session.headers.update(headers)

        session.post(
            "https://www.jiomart.com/api/customer/pincode",
            json={"pincode": PINCODE},
            timeout=10
        )

        response = session.get(PRODUCT_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text().lower()
        return "out of stock" not in text and "currently unavailable" not in text

    except Exception as e:
        log(f"Error checking stock: {e}")
        return last_stock_status  # don't flip state on error


async def send_alert(in_stock):
    status = "AVAILABLE 🟢" if in_stock else "OUT OF STOCK 🔴"

    await bot.send_message(
        chat_id=CHAT_ID,
        text=(
            f"🧅 *JioMart Stock Update*\n\n"
            f"Status: *{status}*\n"
            f"Pincode: `{PINCODE}`\n"
            f"Time: `{datetime.now().strftime('%H:%M:%S')}`\n\n"
            f"{PRODUCT_URL}"
        ),
        parse_mode="Markdown"
    )


async def main():
    global last_stock_status
    log("📦 24/7 JioMart Stock Monitor Started...")

    while True:
        in_stock = check_stock()

        if in_stock != last_stock_status:
            await send_alert(in_stock)
            log(f"Stock status changed: {in_stock}")

        last_stock_status = in_stock
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
                                      
