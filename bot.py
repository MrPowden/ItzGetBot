import os
import logging
from urllib.parse import quote

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = (os.environ.get("WEBAPP_URL") or os.environ.get("WORKER_URL", "")).rstrip("/")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL","").rstrip("/")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "").strip()
PORT = int(os.environ.get("PORT", "10000"))
ADMIN_IDS = {int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()}

if not WEBAPP_URL:
    raise RuntimeError("WEBAPP_URL is required")

app = FastAPI(title="ItzGet Telegram Bot")
bot_app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    payload = context.args[0].strip() if context.args else ""
    web_url = WEBAPP_URL
    if payload:
        web_url += "?start=" + quote(payload, safe="")
    keyboard = [[InlineKeyboardButton("🎮 ИГРАТЬ", web_app=WebAppInfo(url=web_url))]]
    text = (
        "👋 <b>Добро пожаловать в ItzGet NFT!</b>\n\n"
        "⚔️ Новый PvP-бот с играми, NFT и собственным маркетом.\n"
        "🎁 Открывай кейсы, участвуй в PvP, покупай и продавай предметы.\n"
        "💎 Пополняй баланс Stars / TON и участвуй в событиях.\n\n"
        "Нажми <b>ИГРАТЬ</b>, чтобы открыть ItzGet NFT."
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет доступа.")
        return
    keyboard = [[InlineKeyboardButton("🛠 Открыть админку", web_app=WebAppInfo(url=f"{WEBAPP_URL}/admin.html"))]]
    await update.message.reply_text("🛠 Панель администратора ItzGet", reply_markup=InlineKeyboardMarkup(keyboard))

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("admin", admin))

@app.get("/")
async def root():
    return {"ok": True, "service": "itzget-bot"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if WEBHOOK_SECRET:
        provided = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if provided != WEBHOOK_SECRET:
            raise HTTPException(status_code=403, detail="forbidden")
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return JSONResponse({"ok": True})

@app.on_event("startup")
async def startup():
    await bot_app.initialize()
    await bot_app.start()
    webhook_url = WEBHOOK_URL
    await bot_app.bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET or None,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logging.info("Webhook set: %s", webhook_url)

@app.on_event("shutdown")
async def shutdown():
    await bot_app.bot.delete_webhook(drop_pending_updates=False)
    await bot_app.stop()
    await bot_app.shutdown()

if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT)
