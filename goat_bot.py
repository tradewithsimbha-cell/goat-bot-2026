#!/usr/bin/env python3
"""
GOAT MODE 2026 — Telegram Bot
Tera personal AI motivator + goal tracker + reminder system
"""

import os
import json
import asyncio
import logging
from datetime import datetime, time
from pathlib import Path

# pip install python-telegram-bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import random

# ══════════════════════════════════════════
#  CONFIG — YAHAN APNI VALUES DAALO
# ══════════════════════════════════════════
TELEGRAM_TOKEN = "APNA_BOT_TOKEN_YAHAN"       # BotFather se milega
YOUR_CHAT_ID   = 0                             # Tera chat ID (bot /start pe batayega)
DATA_FILE      = "goat_data.json"              # Data yahan save hoga

# ══════════════════════════════════════════
#  TERI GOALS
# ══════════════════════════════════════════
GOALS = {
    "defender":    {"name": "🚙 Defender on Birthday",      "target": 100,   "unit": "%",         "deadline": "2026-11-06"},
    "farmhouse":   {"name": "🏡 Farmhouse Build",           "target": 100,   "unit": "%",         "deadline": "2026-12-31"},
    "travel":      {"name": "✈️ 12 Countries Travel",        "target": 12,    "unit": "countries", "deadline": "2026-12-31"},
    "instagram":   {"name": "📸 Instagram 500K",             "target": 500000,"unit": "followers", "deadline": "2026-12-31"},
    "youtube":     {"name": "▶️ YouTube 100K",               "target": 100000,"unit": "subs",      "deadline": "2026-12-31"},
    "bank":        {"name": "💰 Bank Balance 50 Cr",         "target": 5000,  "unit": "lakhs",     "deadline": "2026-12-31"},
    "fitness":     {"name": "💪 Athletic Body",              "target": 100,   "unit": "%",         "deadline": "2026-12-31"},
    "nofap":       {"name": "🧘 No Fap Full Year",           "target": 365,   "unit": "days",      "deadline": "2026-12-31"},
    "pooja":       {"name": "🕉️ Daily Shiv Pooja",           "target": 365,   "unit": "days",      "deadline": "2026-12-31"},
    "propfirm":    {"name": "📊 Prop Firm $1M Funding",      "target": 1000000,"unit": "USD",      "deadline": "2026-12-31"},
    "land":        {"name": "🌾 50 Bigha Land",              "target": 50,    "unit": "bigha",     "deadline": "2026-12-31"},
    "community":   {"name": "🤝 Trading Community 100",      "target": 100,   "unit": "members",   "deadline": "2026-12-31"},
}

HABITS = [
    {"id": "pooja",   "emoji": "🕉️",  "label": "Morning Pooja kiya?"},
    {"id": "gym",     "emoji": "💪",  "label": "Gym / Exercise kiya?"},
    {"id": "nofap",   "emoji": "🧘",  "label": "No Fap — strong raha?"},
    {"id": "trading", "emoji": "📊",  "label": "Trading / Learning kiya?"},
    {"id": "content", "emoji": "📱",  "label": "Content banaya (IG/YT)?"},
    {"id": "read",    "emoji": "📖",  "label": "Kuch padha / sikha?"},
    {"id": "goal",    "emoji": "🎯",  "label": "Main goal pe kaam kiya?"},
    {"id": "sleep",   "emoji": "💤",  "label": "12 baje se pehle soya?"},
]

MOTIVATIONAL_QUOTES = [
    "Bhai, Defender 6 Nov pe chahiye? Uth aur kaam kar! 🚙",
    "50 Cr bank mein nahi aate — trading mein dil lagao. 💰",
    "Har din pooja karo, Mahadev tumhare saath hain. 🕉️",
    "No Fap = clarity, focus, energy. Aaj bhi strong raho. 🧘",
    "Prop firm $1M — yeh sirf teri trading ki taakat se hoga. 📊",
    "Lazy day aaye toh socho: Defender ya bed? 🚙",
    "Athletic body sirf gym se aata hai. Aaj gaye? 💪",
    "Instagram 500K — aaj ek post kiya? 📸",
    "YouTube 100K — aaj ek video ka plan banaya? ▶️",
    "Har Har Mahadev — discipline hi devotion hai. 🕉️",
    "Distraction = Defender nahi milega. Focus karo. ⚡",
    "Trading weapon hai — use kar, baaki sab ho jayega. 📈",
]

# ══════════════════════════════════════════
#  DATA MANAGEMENT
# ══════════════════════════════════════════
def load_data():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "goals": {k: {"current": 0} for k in GOALS},
        "checkins": {},
        "streaks": {},
        "chat_state": {},
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def today():
    return datetime.now().strftime("%Y-%m-%d")

def get_streak(data):
    checkins = data.get("checkins", {})
    streak = 0
    cur = datetime.now()
    for _ in range(365):
        ds = cur.strftime("%Y-%m-%d")
        if checkins.get(ds, {}).get("saved"):
            streak += 1
        else:
            break
        cur = cur.replace(day=cur.day - 1) if cur.day > 1 else cur
        break  # simplified
    return streak

def year_progress():
    start = datetime(2026, 1, 1)
    end = datetime(2027, 1, 1)
    now = datetime.now()
    if now < start:
        return 0.0
    total = (end - start).days
    done = (now - start).days
    return min(100.0, done / total * 100)

def birthday_countdown():
    bd = datetime(2026, 11, 6)
    now = datetime.now()
    diff = bd - now
    if diff.days < 0:
        return "🎉 Defender day aa gaya!"
    days = diff.days
    hrs = diff.seconds // 3600
    mins = (diff.seconds % 3600) // 60
    return f"{days} days, {hrs} hrs, {mins} mins"

# ══════════════════════════════════════════
#  AI MOTIVATOR
# ══════════════════════════════════════════
# ══════════════════════════════════════════
#  SMART MOTIVATOR — NO API NEEDED, 100% FREE
# ══════════════════════════════════════════

RESPONSES = {
    "lazy": [
        "Bhai LAZY? 😤 Defender 6 Nov pe chahiye ya nahi?\n6 Nov tak {days} din bache hain.\nAbhi uth aur EK kaam karo — bas ek!",
        "Lazy matlab Defender nahi milega. Simple math. 🚙\nTrading se 50 Cr banane hain — lazy log nahi banate.\nAja — gym ya trading — kuch bhi karo abhi!",
        "Bhai Mahadev bhi mehnat karne walon ko help karte hain. 🕉️\nLazy rehna = goals miss karna.\nChal uth — 5 min ke liye kuch productive karo.",
    ],
    "tired": [
        "Tired hona normal hai bhai. 💪\nPar Defender khud nahi aayegi ghar.\nSirf 1 chiz karo aaj — bas check-in karo.",
        "Rest karo — body ki suno. 😴\nLekin kal subah 7 baje fresh start.\nPooja se shuru karo — Mahadev energy denge. 🕉️",
        "Tired = signals ki body ko rest chahiye. Thik hai.\nPar mentally goals yaad rakh.\nSone se pehle kal ka plan likh do — bas itna.",
    ],
    "loss": [
        "Loss ek lesson hai bhai — fee nahi, degree hai. 📊\nJournal kholo — kya galat hua? Rules follow kiye?\nEk loss se trader nahi ruka — aage dekho!",
        "Trading mein loss normal hai. 90% traders lose karte hain.\nTu unn 10% mein rehna chahta hai — toh review karo.\nKal fresh start — same mistake mat karna. 💡",
        "Bhai loss ke baad revenge trading mat karna! ⚠️\nBand karo aaj ke liye — fresh mind kal.\nRisk management = prop firm ka raasta.",
    ],
    "gym": [
        "GYM NAHI GAYA?! 💪\nAthletic body khud nahi banta bhai.\nAbhi jao — 30 min kaafi hai. Defender driver ko fit rehna chahiye! 🚙",
        "Bhai gym chhoda = streak toota.\nConsistency hi results deti hai.\nKal subah 6 baje alarm lagao — gym pehle, baaki baad mein.",
        "Athletic body = discipline ka result. 💪\nEk din miss = habit weak hoti hai.\nAaj bhi time hai — 20 min ghar pe bodyweight karo!",
    ],
    "nofap": [
        "STRONG RAHO BHAI! 🧘\nBrahmacharya = clarity + focus + energy.\nMahadev ki shakti tere saath hai — aaj bhi jeet gaya! 🕉️",
        "No Fap = willpower ka test. Tu pass kar raha hai. 💪\nYeh energy trading aur gym mein lagao.\nHar din strong = Defender ek din aur paas!",
        "Bhai yeh journey sab se mushkil hai — par sab se rewarding bhi.\n365 din = complete transformation.\nAaj ka din = ek aur jeet. Mahadev proud! 🕉️",
    ],
    "pooja": [
        "Har Har Mahadev! 🕉️\nPooja se din shuru karo — baaki sab theek hoga.\nMahadev discipline waalon ko bless karte hain!",
        "Shiv ki bhakti + trading discipline = unstoppable combo. 🕉️📊\nAaj ki pooja ki? Nahi? Abhi karo — 5 min.\nBaaki goals baad mein.",
        "Bhai pooja skip mat karo. 🕉️\nYeh sab se important habit hai — mental peace deta hai.\nTrading bhi better hoti hai jab mind calm ho.",
    ],
    "good": [
        "BHAI TU FIRE HAI! 🔥\nYaisa hi chalta reh — Defender paas aa rahi hai!\nAaj ka score achi raha — kal aur better kar!",
        "Kamaal kiya bhai! 💪🔥\nYeh consistency hi 50 Cr banayegi.\nStreak mat todna — aage badhte raho!",
        "Mahadev proud hai tujhpe! 🕉️🔥\nYeh energy — roz aisi rakh.\nDefender 6 Nov pe confirm hai teri mehnat se! 🚙",
    ],
    "default": [
        "Bhai yaad rakh — {days} din bache hain Defender Day tak! 🚙\nAaj kya plan hai? Trading? Gym? Content?\nBata — main help karunga!",
        "Har Har Mahadev! 🕉️\nGoals yaad hain na?\n/status dekh — aaj ka plan bana aur lag ja kaam pe!",
        "Bhai {days} din mein Defender leni hai. ⏳\nHar din count karta hai.\nAaj ka sabse important kaam kya hai? Woh karo pehle.",
        "Trading weapon hai tera — use kar! 📊\nProp firm $1M, 50 Cr bank — sab possible hai.\nAaj ek step aage badha — /checkin karo!",
        "Instagram 500K, YouTube 100K — content bhi chahiye bhai! 📱\nAaj ek post ya video idea socha?\nSmall steps roz = big results end of year.",
    ],
    "achieve": [
        "BHAI KAMAAL!!! 🎉🔥\nYeh toh sirf shuruat hai — aage aur bada hai!\nMahadev ki kripa aur teri mehnat = unbeatable combo! 🕉️",
        "EK AUR STEP CLOSER! 💪🔥\nYaisa hi karta reh — 2026 tera hai!\nDefender paas aa rahi hai bhai! 🚙",
        "GOAT MODE ACTIVATED! 🐐🔥\nYeh feeling yaad rakh — jab mushkil lage.\nAur goals pe focus rakh — abhi toh bahut kuch bacha hai!",
    ],
}

def get_smart_response(user_msg: str, data: dict) -> str:
    msg_lower = user_msg.lower()
    bd = datetime(2026, 11, 6)
    days = (bd - datetime.now()).days

    # Detect context
    if any(w in msg_lower for w in ["lazy", "bore", "nahi karna", "mann nahi", "chhod"]):
        key = "lazy"
    elif any(w in msg_lower for w in ["tired", "thak", "neend", "rest"]):
        key = "tired"
    elif any(w in msg_lower for w in ["loss", "lose", "negative", "bad trade", "stop out"]):
        key = "loss"
    elif any(w in msg_lower for w in ["gym", "exercise", "workout", "fitness"]):
        key = "gym"
    elif any(w in msg_lower for w in ["nofap", "no fap", "fap", "strong"]):
        key = "nofap"
    elif any(w in msg_lower for w in ["pooja", "mahadev", "shiv", "prayer", "mandir"]):
        key = "pooja"
    elif any(w in msg_lower for w in ["achieve", "kiya", "done", "complete", "jeet", "win"]):
        key = "achieve"
    elif any(w in msg_lower for w in ["good", "acha", "badhiya", "great", "amazing"]):
        key = "good"
    else:
        key = "default"

    template = random.choice(RESPONSES[key])
    return template.format(days=max(0, days))

async def get_ai_response(user_msg: str, data: dict, context_type: str = "general") -> str:
    return get_smart_response(user_msg, data)

# ══════════════════════════════════════════
#  COMMAND HANDLERS
# ══════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = f"""
🔥 *GOAT MODE 2026 ACTIVATED!*

Tera personal AI motivator ready hai bhai!

*Tera Chat ID:* `{chat_id}`
_(Ise bot code mein daalo)_

*Commands:*
/goals — Sare goals dekho
/checkin — Daily check-in karo
/update — Goal progress update karo
/status — Aaj ka full status
/defender — Countdown to Defender Day 🚙
/ai — AI se baat karo
/help — Sab commands

*Defender Day countdown:*
⏳ {birthday_countdown()}

Har Har Mahadev! 🕉️
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_goals(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    lines = ["🎯 *YOUR 2026 GOALS*\n"]
    for key, goal in GOALS.items():
        cur = data["goals"].get(key, {}).get("current", 0)
        tgt = goal["target"]
        pct = min(100, cur / tgt * 100) if tgt else 0
        bar_filled = int(pct / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        status = "✅" if pct >= 100 else "🔥" if pct >= 50 else "⬜"
        cur_display = f"{cur:,}" if tgt > 1000 else str(cur)
        tgt_display = f"{tgt:,}" if tgt > 1000 else str(tgt)
        lines.append(
            f"{status} *{goal['name']}*\n"
            f"`{bar}` {pct:.0f}%\n"
            f"_{cur_display} / {tgt_display} {goal['unit']}_\n"
        )
    lines.append(f"\n📊 Year Progress: *{year_progress():.1f}%*")
    lines.append(f"🚙 Defender: *{birthday_countdown()}*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_checkin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    data = load_data()
    today_ci = data["checkins"].get(today(), {})
    habits_done = today_ci.get("habits", {})

    for i in range(0, len(HABITS), 2):
        row = []
        for h in HABITS[i:i+2]:
            done = habits_done.get(h["id"], False)
            label = f"{'✅' if done else '⬜'} {h['emoji']} {h['label'][:15]}"
            row.append(InlineKeyboardButton(label, callback_data=f"habit_{h['id']}"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("💾 Save Check-in", callback_data="save_checkin"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
    ])

    done_count = sum(1 for h in HABITS if habits_done.get(h["id"]))
    score = int(done_count / len(HABITS) * 100)

    await update.message.reply_text(
        f"✅ *DAILY CHECK-IN — {today()}*\n\n"
        f"Har habit tap karke mark karo:\n"
        f"Score: *{score}%* ({done_count}/{len(HABITS)} habits)\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def cmd_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Usage: /update defender 75  or  /update instagram 15000"""
    args = ctx.args
    if len(args) < 2:
        goals_list = "\n".join([f"`/update {k} VALUE` — {v['name']}" for k, v in GOALS.items()])
        await update.message.reply_text(
            f"📝 *Update Goal Progress*\n\nUsage: `/update GOAL_KEY VALUE`\n\n*Available goals:*\n{goals_list}",
            parse_mode="Markdown"
        )
        return

    key = args[0].lower()
    if key not in GOALS:
        await update.message.reply_text(f"❌ Goal '{key}' nahi mila. /update use karo bina args ke list dekhne ke liye.")
        return

    try:
        value = float(args[1])
    except ValueError:
        await update.message.reply_text("❌ Valid number daalo. Example: `/update defender 75`", parse_mode="Markdown")
        return

    data = load_data()
    old_val = data["goals"].get(key, {}).get("current", 0)
    data["goals"][key]["current"] = value
    save_data(data)

    goal = GOALS[key]
    pct = min(100, value / goal["target"] * 100)

    msg = f"✅ *Updated!*\n\n{goal['name']}\n{old_val} → *{value}* {goal['unit']}\nProgress: *{pct:.1f}%*"

    if pct >= 100:
        msg += "\n\n🎉 *GOAL ACHIEVED! BHAI TU GOAT HAI!* 🏆"
    elif pct >= 50:
        msg += "\n\n🔥 Halfway there — keep going!"

    await update.message.reply_text(msg, parse_mode="Markdown")

    # AI celebration if big milestone
    if pct >= 100 or (old_val / goal["target"] * 100 < 25 <= pct):
        ai_msg = await get_ai_response(
            f"Maine {goal['name']} mein {pct:.0f}% achieve kar liya!",
            data, "celebration"
        )
        await update.message.reply_text(f"🤖 *AI Coach:*\n{ai_msg}", parse_mode="Markdown")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    checkins = data.get("checkins", {})
    today_ci = checkins.get(today(), {})
    today_done = today_ci.get("saved", False)
    streak = get_streak(data)
    total_ci = len([d for d in checkins if checkins[d].get("saved")])
    goals_done = sum(
        1 for k in GOALS
        if data["goals"].get(k, {}).get("current", 0) >= GOALS[k]["target"]
    )

    status_emoji = "🔥" if today_done else "❌"

    msg = f"""
📊 *GOAT MODE STATUS — {today()}*

{status_emoji} Today's check-in: {'Done ✅' if today_done else 'Pending — karo abhi!'}
🔥 Current streak: *{streak} days*
📅 Total check-ins: *{total_ci}*
🎯 Goals completed: *{goals_done}/{len(GOALS)}*
📈 Year progress: *{year_progress():.1f}%*
🚙 Defender countdown: *{birthday_countdown()}*

*Top 3 Goals:*
"""
    top_goals = sorted(
        GOALS.items(),
        key=lambda x: data["goals"].get(x[0], {}).get("current", 0) / x[1]["target"],
        reverse=True
    )[:3]

    for key, goal in top_goals:
        cur = data["goals"].get(key, {}).get("current", 0)
        pct = min(100, cur / goal["target"] * 100)
        msg += f"• {goal['name']}: *{pct:.0f}%*\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_defender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    countdown = birthday_countdown()
    msg = f"""
🚙 *DEFENDER DAY COUNTDOWN*

⏳ *{countdown}*

📅 Date: 6 November 2026
🎂 Occasion: Tera Birthday

_"Aaj jo kaam karega, woh 6 Nov ko Defender ki chabi ban kar milega."_

Har Har Mahadev! 🕉️
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_ai(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Chat with motivational coach"""
    user_text = " ".join(ctx.args) if ctx.args else "Mujhe motivate kar aaj ke liye"
    data = load_data()
    response = get_smart_response(user_text, data)
    await update.message.reply_text(
        f"🔥 *Coach:*\n\n{response}",
        parse_mode="Markdown"
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = """
🔥 *GOAT MODE 2026 — Commands*

*Daily Use:*
/checkin — Daily habits check-in ✅
/status — Aaj ka full status 📊
/defender — Defender countdown 🚙

*Goals:*
/goals — Sare goals dekho 🎯
/update goal value — Progress update karo 📝
_Example: /update instagram 25000_

*AI Coach:*
/ai message — AI se baat karo 🤖
_Example: /ai aaj bahut lazy feel ho raha hai_

*Others:*
/help — Yeh message

Har Har Mahadev! 🕉️
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

# ══════════════════════════════════════════
#  CALLBACK HANDLERS (Inline buttons)
# ══════════════════════════════════════════
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_cb = query.data

    if data_cb.startswith("habit_"):
        habit_id = data_cb[6:]
        data = load_data()
        today_ci = data["checkins"].setdefault(today(), {"habits": {}, "saved": False})
        habits = today_ci.setdefault("habits", {})
        habits[habit_id] = not habits.get(habit_id, False)
        save_data(data)

        # Rebuild keyboard
        keyboard = []
        habits_done = habits
        for i in range(0, len(HABITS), 2):
            row = []
            for h in HABITS[i:i+2]:
                done = habits_done.get(h["id"], False)
                label = f"{'✅' if done else '⬜'} {h['emoji']} {h['label'][:15]}"
                row.append(InlineKeyboardButton(label, callback_data=f"habit_{h['id']}"))
            keyboard.append(row)

        done_count = sum(1 for h in HABITS if habits_done.get(h["id"]))
        score = int(done_count / len(HABITS) * 100)

        keyboard.append([
            InlineKeyboardButton("💾 Save Check-in", callback_data="save_checkin"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
        ])

        await query.edit_message_text(
            f"✅ *DAILY CHECK-IN — {today()}*\n\n"
            f"Har habit tap karke mark karo:\n"
            f"Score: *{score}%* ({done_count}/{len(HABITS)} habits)\n",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data_cb == "save_checkin":
        data = load_data()
        today_ci = data["checkins"].setdefault(today(), {"habits": {}, "saved": False})
        habits = today_ci.get("habits", {})
        done_count = sum(1 for h in HABITS if habits.get(h["id"]))
        score = int(done_count / len(HABITS) * 100)
        today_ci["saved"] = True
        today_ci["score"] = score
        today_ci["time"] = datetime.now().isoformat()

        # Auto-update nofap and pooja streaks
        if habits.get("nofap"):
            nofap_streak = sum(
                1 for d in sorted(data["checkins"].keys(), reverse=True)
                if data["checkins"][d].get("habits", {}).get("nofap")
            )
            data["goals"]["nofap"]["current"] = nofap_streak

        if habits.get("pooja"):
            pooja_streak = sum(
                1 for d in sorted(data["checkins"].keys(), reverse=True)
                if data["checkins"][d].get("habits", {}).get("pooja")
            )
            data["goals"]["pooja"]["current"] = pooja_streak

        save_data(data)

        score_msg = (
            "🔥 PERFECT DAY! Mahadev proud hai!" if score == 100
            else "💪 Almost perfect — kal 100% kar!" if score >= 80
            else "😐 Theek hai — kal better kar" if score >= 50
            else "😔 Struggle hua — kal fresh start!"
        )

        await query.edit_message_text(
            f"✅ *Check-in saved!*\n\n"
            f"Score: *{score}%* ({done_count}/{len(HABITS)} habits)\n\n"
            f"{score_msg}\n\n"
            f"🚙 Defender: {birthday_countdown()}",
            parse_mode="Markdown"
        )

        # AI response if score low
        if score < 60:
            ai_msg = await get_ai_response(
                f"Aaj sirf {score}% habits kiye — lazy ho gaya",
                data
            )
            await ctx.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"🤖 *AI Coach:*\n{ai_msg}",
                parse_mode="Markdown"
            )

    elif data_cb == "cancel":
        await query.edit_message_text("❌ Check-in cancelled.")

# ══════════════════════════════════════════
#  FREE TEXT — AI RESPONDS
# ══════════════════════════════════════════
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Any free text message — AI responds"""
    data = load_data()
    user_text = update.message.text

    # Simple keyword detection
    if any(w in user_text.lower() for w in ["lazy", "tired", "bore", "distract", "nahi kar"]):
        context = "user is feeling lazy or distracted"
    elif any(w in user_text.lower() for w in ["achieve", "kiya", "completed", "done"]):
        context = "user achieved something"
    else:
        context = "general conversation"

    response = await get_ai_response(user_text, data, context)
    await update.message.reply_text(
        f"🤖 {response}",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════════
#  SCHEDULED REMINDERS
# ══════════════════════════════════════════
async def send_reminder(bot, chat_id: int, msg: str):
    try:
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Reminder error: {e}")

async def morning_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    quote = MOTIVATIONAL_QUOTES[datetime.now().day % len(MOTIVATIONAL_QUOTES)]
    streak = get_streak(data)
    msg = f"""
🌅 *SUBAH HO GAYI BHAI!*

{quote}

🔥 Current streak: *{streak} days*
🚙 Defender: *{birthday_countdown()}*

Shuru karo:
1️⃣ Pooja karo 🕉️
2️⃣ /checkin karo ✅
3️⃣ Kaam mein lag jao 💪

Har Har Mahadev! 🕉️
"""
    await send_reminder(ctx.bot, YOUR_CHAT_ID, msg)

async def afternoon_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today_ci = data["checkins"].get(today(), {})
    if today_ci.get("saved"):
        return  # Already checked in — no spam

    msg = f"""
☀️ *DOPAHAR HO GAYI!*

Trading kaisi rahi aaj? 📊
Gym ka plan kya hai? 💪

Abhi tak check-in nahi kiya — /checkin karo!

🚙 Defender countdown: *{birthday_countdown()}*
"""
    await send_reminder(ctx.bot, YOUR_CHAT_ID, msg)

async def evening_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    msg = f"""
🌆 *SHAM HO GAYI BHAI!*

Aaj ki checklist:
☐ Pooja kiya? 🕉️
☐ Gym gaye? 💪
☐ Content banaya? 📱
☐ Trading journal likha? 📊

Abhi bhi time hai — karo jo bacha hai!

🚙 {birthday_countdown()}
"""
    await send_reminder(ctx.bot, YOUR_CHAT_ID, msg)

async def night_checkin_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today_ci = data["checkins"].get(today(), {})

    if today_ci.get("saved"):
        score = today_ci.get("score", 0)
        msg = f"""
🌙 *RAAT KA REVIEW*

Aaj ka score: *{score}%* {'🔥' if score >= 80 else '💪' if score >= 50 else '😔'}

{'Kamaal kiya bhai! Kal bhi aisa hi karo!' if score >= 80 else 'Kal 100% karne ki koshish karo!'}

Sone se pehle kal ka plan banao. 📝
Har Har Mahadev! 🕉️
"""
    else:
        msg = f"""
🌙 *RAAT HO GAYI — CHECK-IN PENDING!*

Aaj ka check-in abhi bhi nahi kiya!
/checkin karo — 2 minute ka kaam hai.

Defender chahiye? Consistent raho! 🚙
Streak mat todna bhai! 🔥
"""
    await send_reminder(ctx.bot, YOUR_CHAT_ID, msg)

async def weekly_review(ctx: ContextTypes.DEFAULT_TYPE):
    """Sunday ko weekly review"""
    if datetime.now().weekday() != 6:  # 6 = Sunday
        return

    data = load_data()
    checkins = data.get("checkins", {})

    # Last 7 days
    week_scores = []
    for i in range(7):
        from datetime import timedelta
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        ci = checkins.get(d, {})
        week_scores.append(ci.get("score", 0))

    avg = sum(week_scores) / len(week_scores)
    perfect = sum(1 for s in week_scores if s >= 80)

    msg = f"""
📊 *WEEKLY REVIEW — Week {datetime.now().isocalendar()[1]}*

Average score: *{avg:.0f}%*
Perfect days: *{perfect}/7*
{'🔥 Amazing week!' if avg >= 80 else '💪 Good effort!' if avg >= 60 else '⚠️ Need to improve next week!'}

*Goals this week:*
"""
    for key, goal in list(GOALS.items())[:5]:
        cur = data["goals"].get(key, {}).get("current", 0)
        pct = min(100, cur / goal["target"] * 100)
        msg += f"• {goal['name']}: {pct:.0f}%\n"

    msg += f"\n🚙 Defender: *{birthday_countdown()}*\n\nIs week better karo! 💪"
    await send_reminder(ctx.bot, YOUR_CHAT_ID, msg)

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("goals",    cmd_goals))
    app.add_handler(CommandHandler("checkin",  cmd_checkin))
    app.add_handler(CommandHandler("update",   cmd_update))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("defender", cmd_defender))
    app.add_handler(CommandHandler("ai",       cmd_ai))
    app.add_handler(CommandHandler("help",     cmd_help))

    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Free text → AI
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduled reminders
    job_queue = app.job_queue
    job_queue.run_daily(morning_reminder,       time(hour=7,  minute=0),  name="morning")
    job_queue.run_daily(afternoon_reminder,     time(hour=13, minute=0),  name="afternoon")
    job_queue.run_daily(evening_reminder,       time(hour=18, minute=0),  name="evening")
    job_queue.run_daily(night_checkin_reminder, time(hour=21, minute=30), name="night")
    job_queue.run_daily(weekly_review,          time(hour=20, minute=0),  name="weekly")

    print("🔥 GOAT MODE Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
