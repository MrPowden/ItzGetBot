# ItzGet NFT — Bot + Mini App

## 1. Сначала задеплой Web App

В корне проекта:

```bash
npm install
npx wrangler login
npx wrangler d1 migrations apply itzget --remote
npx wrangler secret put BOT_TOKEN
npx wrangler secret put WEBHOOK_SECRET
npx wrangler deploy
```

После deploy адрес будет примерно:
`https://itzget-pvp.<subdomain>.workers.dev`

Проверь, что этот адрес открывает Mini App.

## 2. Запусти Telegram-бота

Windows PowerShell:

```powershell
cd bot
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env
python bot.py
```

В `.env` укажи реальные значения:

```env
BOT_TOKEN=ТОКЕН_ОТ_BOTFATHER
WEBAPP_URL=https://ТВОЙ_WORKER.workers.dev
ADMIN_IDS=ТВОЙ_TELEGRAM_ID
```

После этого `/start` отправляет приветствие и кнопку **🎮 ИГРАТЬ**, которая открывает Web App.

## 3. Как работает реферальная ссылка

Формат Telegram deep link:

`https://t.me/<ИМЯ_БОТА>?start=<ID_ПОЛЬЗОВАТЕЛЯ>`

Например:

`https://t.me/ItzGetBot?start=123456789`

Важно: используется именно `?start=`, а не `=start?`.

## 4. Production

Бот из этого архива работает через polling. Для 24/7 держи `python bot.py` на VPS/сервере.

Не запускай второй экземпляр этого же polling-бота одновременно.
