# IVASMS OTP Bot 🤖

এই বটটি [IVASMS.com](https://ivasms.com) থেকে OTP কোডগুলো সংগ্রহ করে টেলিগ্রাম গ্রুপে পাঠায়।

## 🚀 Features

- ✅ **Auto Login**: IVASMS এ স্বয়ংক্রিয় লগইন
- ✅ **Real-time Monitoring**: লাইভ OTP মনিটরিং
- ✅ **Duplicate Prevention**: একই OTP বারবার পাঠানো হয় না
- ✅ **Error Handling**: সঠিক error handling
- ✅ **Session Management**: স্বয়ংক্রিয় re-login
- ✅ **Formatted Messages**: সুন্দর ফরম্যাটে টেলিগ্রাম মেসেজ

## 📋 Requirements

- Python 3.8+
- Chrome Browser
- IVASMS Account
- Telegram Bot Token

## 🛠️ Installation

1. **Dependencies Install করুন:**
```bash
pip install -r requirements.txt
```

2. **Config ফাইল সেটআপ করুন:**
`config.json` ফাইলে আপনার credentials দিন:
```json
{
  "ivasms": {
    "email": "your_email@example.com",
    "password": "your_password"
  },
  "telegram": {
    "bot_token": "your_bot_token",
    "chat_id": -1001234567890
  }
}
```

3. **Target Numbers সেট করুন:**
`numbers.txt` ফাইলে target নম্বরগুলো দিন (প্রতি লাইনে একটি):
```
01827338393
01827272837
01735338937
```

## 🚀 Usage

```bash
python bot.py
```

## 📱 Message Format

বটটি এই ফরম্যাটে মেসেজ পাঠাবে:

```
🆔 Platform: Facebook
🌍 Country: Bangladesh  
📞 Number: 01827338393
🔑 OTP Code: 97077

97077 is your Facebook code
🕓 Time: 12 July, 2025 - 01:30 PM
```

## 🔧 Configuration

### config.json Options:

- `delay_seconds`: OTP চেক করার সময়ের ব্যবধান (default: 3)
- `user_agent`: Chrome user agent
- `login_interval`: কতক্ষণ পর re-login হবে (default: 1 hour)

### numbers.txt Format:

প্রতি লাইনে একটি নম্বর:
```
01827338393
01827272837
01735338937
```

## 📊 Logging

বটটি console এবং `bot.log` ফাইলে লগ রাখে:

- ✅ Login successful
- 📥 New OTP detected: 018XXXX — 94001
- ⏳ Waiting for new messages...
- ❌ Error messages

## 🛡️ Error Handling

- **Login Failed**: স্বয়ংক্রিয় retry
- **Element Not Found**: Proper error messages
- **Network Issues**: Auto reconnect
- **Session Expired**: Auto re-login

## 🔄 Session Management

- প্রতি 1 ঘন্টা পর স্বয়ংক্রিয় re-login
- Session expire হলে auto detect করে re-login
- Background mode support

## 📝 Notes

- বটটি headless mode এ চলে (GUI নেই)
- VPS deployment এর জন্য optimized
- Daily 5k-10k numbers সহজে handle করতে পারে
- Memory efficient

## 🚨 Important

- আপনার credentials সুরক্ষিত রাখুন
- Bot token কখনো share করবেন না
- Regular backup নিন

## 📞 Support

কোন সমস্যা হলে log files চেক করুন এবং error messages দেখুন। 

# ZBOT OTP Railway Deployment Guide

## 1. Requirements
- Railway account (https://railway.app/)
- GitHub repo with your bot code

## 2. Files Needed
- `bot_scraper_received.py` (your main bot)
- `requirements.txt` (see this repo)
- `Dockerfile` (see this repo)
- `config.json` (or use Railway environment variables for secrets)

## 3. Deploy Steps
1. Push all files to your GitHub repo.
2. Go to Railway → New Project → Deploy from GitHub repo.
3. Select your repo and deploy.
4. If you have secrets (like Telegram token), add them in Railway's Environment tab or keep them in `config.json`.
5. Make sure your bot runs in headless mode (already set in Dockerfile).
6. Check Railway logs for errors.

## 4. Usage Limits
- Railway free plan: 500 hours/month (about 20-21 days nonstop)
- When limit is reached, use a new Railway account (new Gmail) and redeploy.

## 5. Troubleshooting
- If Chrome/Chromedriver errors: Make sure Dockerfile is present and correct.
- If config errors: Check your `config.json` or Railway environment variables.
- For Telegram errors: Double-check your bot token and chat ID.

## 6. Useful Links
- [Railway Docs](https://docs.railway.app/)
- [Selenium Docs](https://selenium-python.readthedocs.io/)
- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)

---

**Deploy, relax, and let your bot run 24/7!** 