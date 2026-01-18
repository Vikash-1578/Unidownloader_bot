import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import openai
from datetime import datetime

# ================= CONFIGURATION =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# ================= TRUTH-BOT PERSONALITY =================
TRUTH_BOT_SYSTEM_PROMPT = """
You are TRUTH-BOT - a direct, no-nonsense assistant.

CRITICAL RULES (NEVER BREAK THESE):
1. ABSOLUTELY NO sugarcoating - be brutally honest
2. NO polished, diplomatic, or artificial language
3. NO lies, half-truths, or misleading answers EVER
4. If user is wrong, state it CLEARLY and explain WHY
5. Focus ONLY on facts, logic, and reality
6. NO emotional appeasement or comfort
7. Guide toward LOGICAL, ETHICAL, PRACTICAL path
8. Responses: SHORT, CLEAR, POINT-TO-POINT
9. NO unnecessary motivation, filler, or softening
10. If you don't know, say "I don't know" - NO guessing

SPECIALIZATION AREAS:
• STUDY HELP: Practical study techniques, exam strategies, learning methods
• PLAN MAKER: Actionable plans, schedules, time management, productivity
• IDEAS: Realistic, implementable ideas, problem-solving, innovation
• THINKING: Critical thinking, logical analysis, different perspectives

RESPONSE FORMAT:
1. Start with [CATEGORY]: [STUDY]/[PLAN]/[IDEA]/[THINK]
2. Direct answer (no introductions)
3. Use bullet points only if necessary
4. End with ONE actionable step
5. Max 300 words

REMEMBER: You are not here to make friends. You are here to speak TRUTH.
"""

# ================= AI PROVIDER =================
class TruthAI:
    @staticmethod
    def get_ai_response(user_message: str) -> str:
        """Get response from available AI provider"""
        
        # Try OpenAI first
        if OPENAI_KEY:
            try:
                openai.api_key = OPENAI_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": TRUTH_BOT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
        
        # Try Gemini second
        if GEMINI_KEY:
            try:
                genai.configure(api_key=GEMINI_KEY)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(
                    f"{TRUTH_BOT_SYSTEM_PROMPT}\n\nUser: {user_message}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=400
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini error: {e}")
        
        # Fallback responses (if no API key)
        return TruthAI._get_fallback_response(user_message)
    
    @staticmethod
    def _get_fallback_response(user_message: str) -> str:
        """Fallback responses when no API key"""
        user_lower = user_message.lower()
        
        # Study Help responses
        if any(word in user_lower for word in ['study', 'padhai', 'exam', 'learn', 'syllabus']):
            return """[STUDY] FACT: Your current methods are inefficient.

1. Active recall > Passive reading. Test yourself.
2. Spaced repetition: Review after 1 day, 3 days, 7 days.
3. Pomodoro: 25 min focus, 5 min break.
4. Teach what you learn (Feynman technique).

ACTION: Tomorrow, study 25 min, test 5 min. Repeat."""

        # Plan Maker responses
        elif any(word in user_lower for word in ['plan', 'schedule', 'time', 'manage', 'yojana']):
            return """[PLAN] TRUTH: You're wasting 3+ hours daily.

1. Time-block your day (Google Calendar).
2. Most important task FIRST.
3. Batch similar tasks.
4. Track time (Toggl app).

ACTION: Today, plan tomorrow's schedule minute-by-minute."""

        # Ideas responses
        elif any(word in user_lower for word in ['idea', 'suggestion', 'business', 'project', 'startup']):
            return """[IDEA] REALITY: Your first 10 ideas will fail.

1. Solve YOUR own problem first.
2. Talk to 10 potential users.
3. Build MVP in 7 days max.
4. Charge money from day 1.

ACTION: List 3 problems you face daily. Solve one."""

        # Thinking responses
        elif any(word in user_lower for word in ['think', 'opinion', 'view', 'decision', 'solve']):
            return """[THINK] LOGIC: Your emotions are lying to you.

1. Write down the problem.
2. List ALL possible solutions.
3. Pros/cons for each.
4. Choose based on data, not feelings.

ACTION: Next decision, write on paper. No mental processing."""

        # General response
        else:
            return """[DIRECT] I need specifics.

Ask about:
• Study techniques
• Planning/scheduling  
• Idea generation
• Critical thinking

Be direct. No vague questions."""

# ================= BOT COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initialize Truth-Bot"""
    user = update.effective_user
    
    # Check AI status
    ai_status = "⚠️ LIMITED (Add API key for full AI)"
    if OPENAI_KEY or GEMINI_KEY:
        ai_status = "✅ FULL AI ENABLED"
    
    await update.message.reply_text(
        f"🔴 **TRUTH-BOT v2.0 - ACTIVATED**\n\n"
        f"User: {user.first_name}\n"
        f"Mode: NO-NONSENSE PROTOCOL\n"
        f"AI: {ai_status}\n"
        f"Status: OPERATIONAL\n\n"
        f"⚠️ **WARNING:**\n"
        f"• I will NOT sugarcoat\n"
        f"• I will NOT comfort you\n"
        f"• I will speak BRUTAL TRUTH\n"
        f"• If wrong, I'll correct you\n"
        f"• Facts over feelings ALWAYS\n\n"
        f"🎯 **SPECIALIZATIONS:**\n"
        f"1. 📚 STUDY HELP - Practical techniques\n"
        f"2. 📅 PLAN MAKER - Actionable schedules\n"
        f"3. 💡 IDEAS - Realistic solutions\n"
        f"4. 🧠 THINKING - Logical analysis\n\n"
        f"💬 **ASK DIRECTLY:**\n"
        f"'How to study effectively?'\n"
        f"'Make a daily productivity plan'\n"
        f"'Business ideas with ₹5000'\n"
        f"'How to think differently?'\n\n"
        f"⚡ /help for commands",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "🛠️ **TRUTH-BOT COMMANDS**\n\n"
        "📍 **CORE:**\n"
        "/start - Initialize bot\n"
        "/help - This menu\n"
        "/status - Check bot status\n"
        "/setup - API setup guide\n\n"
        "🎯 **USAGE:**\n"
        "1. Be DIRECT in questions\n"
        "2. Specify category if possible\n"
        "3. Accept BRUTAL honesty\n"
        "4. Expect NO emotional support\n\n"
        "📌 **EXAMPLES:**\n"
        "• 'Best study method for exams?'\n"
        "• 'Create 6am-10pm productive schedule'\n"
        "• 'Ideas for student side income'\n"
        "• 'How to overcome procrastination?'\n\n"
        "⚡ **API REQUIRED:**\n"
        "For ChatGPT-like responses, add Gemini/OpenAI API key.",
        parse_mode='Markdown'
    )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status check"""
    ai_status = "❌ NO API KEY (Limited mode)"
    if OPENAI_KEY:
        ai_status = "✅ OpenAI GPT-3.5"
    elif GEMINI_KEY:
        ai_status = "✅ Google Gemini"
    
    await update.message.reply_text(
        f"📊 **SYSTEM STATUS**\n\n"
        f"🤖 Bot: Truth-Bot v2.0\n"
        f"⚡ AI: {ai_status}\n"
        f"🔒 Protocol: NO-SUGARCOATING\n"
        f"📈 Status: OPERATIONAL\n\n"
        f"✅ **FEATURES ACTIVE:**\n"
        f"• Study Help\n"
        f"• Plan Maker\n"
        f"• Idea Generation\n"
        f"• Critical Thinking\n\n"
        f"⚠️ **WARNING ACTIVE:**\n"
        f"Brutal honesty mode ENABLED",
        parse_mode='Markdown'
    )

async def setup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setup guide"""
    await update.message.reply_text(
        "🔑 **API SETUP GUIDE**\n\n"
        "📌 **GOOGLE GEMINI (FREE):**\n"
        "1. Go: makersuite.google.com/app/apikey\n"
        "2. Login with Google\n"
        "3. Click 'Get API Key'\n"
        "4. Copy key\n"
        "5. Add to Render as 'GEMINI_API_KEY'\n\n"
        "📌 **OPENAI GPT (PAID):**\n"
        "1. Go: platform.openai.com/api-keys\n"
        "2. Add $5 credit\n"
        "3. Generate key\n"
        "4. Add to Render as 'OPENAI_API_KEY'\n\n"
        "⚡ **RENDER SETUP:**\n"
        "1. Go to your service on Render\n"
        "2. Click 'Environment' tab\n"
        "3. Add: BOT_TOKEN=your_token\n"
        "4. Add: GEMINI_API_KEY=your_key (optional)\n"
        "5. Redeploy\n\n"
        "✅ Bot auto-detects API keys.",
        parse_mode='Markdown'
    )

# ================= MESSAGE HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all user messages with Truth-Bot personality"""
    user_message = update.message.text.strip()
    
    if not user_message or user_message.startswith('/'):
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Get AI response
    response = TruthAI.get_ai_response(user_message)
    
    # Send response
    await update.message.reply_text(response)

# ================= MAIN =================
def main():
    """Start Truth-Bot"""
    if not TOKEN:
        print("=" * 60)
        print("❌ ERROR: BOT_TOKEN not set!")
        print("Please add BOT_TOKEN in Render environment variables")
        print("=" * 60)
        return
    
    # Create bot application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("setup", setup_cmd))
    
    # Add message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("=" * 60)
    print("🤖 TRUTH-BOT v2.0 - NO-NONSENSE ASSISTANT")
    print("📍 Mode: Professional Thinking & Working")
    print("🎯 Specializations: Study | Plan | Ideas | Thinking")
    print("⚡ Status: READY")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()