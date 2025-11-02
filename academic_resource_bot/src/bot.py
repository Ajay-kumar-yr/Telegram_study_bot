from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton,InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from telegram.error import NetworkError
from scraping import get_source,fetch_links_from_url,download_file
from rag import rag_pipeline,ask_llm
import os
from dotenv import load_dotenv
import re 
import shutil  

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKENS") 

# /start command
async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Notes Bot!\n\n"
        "Use /notes to get notes.\n"
        "Use /store to store the notes in database.\n"
        "Use /ask to ask a question.\n"
        "Use /help for guidance."
    )


# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Steps to get notes\n\n"
        "Step 1: Use /notes to begin.\n"
        "Step 2: Select your branch.\n"
        "Step 3: Select your semester.\n"
        "Step 3: Select your subject code.\n"
        "Step 4: you will receive available notes.\n\n"
        "[Note: Now to /ask questions store these \n notes data in database]\n\n"
        "----------------------------------------------------------------------\n"
        "Store a data in database \n\n"
        "Step 1: send /store command\n"
        "Step 2: stores data in database\n"
        "Now you ask questions on that notes\n\n"
        "----------------------------------------------------------------------\n"
        "Ask a question ? \n\n"
        "Before asking a question download the /notes and /store notes in database\n\n"
        "Step 1: Use /ask command to begin.\n"
        "Step 2: it replies with (send a question).\n"
        "Step 3: you send a question to chart.\n"
        "Step 4: it replies with answer .\n\n"
        "----------------------------------------------------------------------\n"
        "[IMPORTANT NOTE: Answer for the question will be given based on the notes " \
        "which you will store in database using llm]\n\n"
        "----------------------------------------------------------------------\n"
        "Work flow\n\n"
        "notes will be sent to chart and aslo downloaded in server\n"
        "that will be stored in database and remove downloaded notes from the server\n"
        "using /ask will gives most relavent answer to question using llm(deepseek)\n\n"
        "----------------------------------------------------------------------\n"
        "Commands:\n"
        "/start – Welcome message and show commands available\n"
        "/notes – Begin notes search\n"
        "/store – Store notes in database\n"
        "/ask   – Begin to search answer\n"
        "/help  – This command helps to get notes"
    )

# /notes command → show branch buttons
async def notes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("CSE", callback_data="branch_CSE"),
         InlineKeyboardButton("CSEDS", callback_data="branch_CSEDS")],
        [InlineKeyboardButton("CSEAIML", callback_data="branch_CSEAIML"),
         InlineKeyboardButton("ECE", callback_data="branch_ECE")],
        [InlineKeyboardButton("EEE", callback_data="branch_EEE"),
         InlineKeyboardButton("ISE", callback_data="branch_ISE")],
        [InlineKeyboardButton("CV", callback_data="branch_CV"),
         InlineKeyboardButton("ME", callback_data="branch_ME")],
        [InlineKeyboardButton("MBA", callback_data="branch_MBA")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📚 Select your branch:", reply_markup=reply_markup)

# Handle branch selection → send branch + subject buttons
async def handle_branch_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    branch = query.data.split("_")[1]
    context.user_data["branch"] = branch

    await query.message.reply_text(f"✅ Branch selected: {branch}")
    
    if branch == "MBA":
        keyboard = [
            [InlineKeyboardButton("I SEMESTER", callback_data="sem_I SEMESTER"),
             InlineKeyboardButton("II SEMESTER", callback_data="sem_II SEMESTER")],
            [InlineKeyboardButton("III SEMESTER", callback_data="sem_III SEMESTER"),
             InlineKeyboardButton("IV SEMESTER", callback_data="sem_IV SEMESTER")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📘 Select your semester:", reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("PHYSICS-CYCLE", callback_data="sem_PHYSICS-CYCLE"),
             InlineKeyboardButton("CHEMISTRY-CYCLE", callback_data="sem_CHEMISTRY-CYCLE")],
            [InlineKeyboardButton("III SEMESTER", callback_data="sem_III SEMESTER"),
             InlineKeyboardButton("IV SEMESTER", callback_data="sem_IV SEMESTER")],
            [InlineKeyboardButton("V SEMESTER", callback_data="sem_V SEMESTER"),
             InlineKeyboardButton("VI SEMESTER", callback_data="sem_VI SEMESTER")],
            [InlineKeyboardButton("VII SEMESTER", callback_data="sem_VII SEMESTER"),
             InlineKeyboardButton("VIII SEMESTER", callback_data="sem_VIII SEMESTER")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📘 Select your semester:", reply_markup=reply_markup)

async def handle_semester_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    semester = query.data.split("_")[1]
    context.user_data["semester"] = semester
    branch = context.user_data.get("branch", "unknown")
    lowerbranch=branch.lower()
    await query.message.reply_text(f"📖 Semester selected: {semester}")

    if semester=="PHYSICS-CYCLE" or semester=="CHEMISTRY-CYCLE":
        lowersem=semester.lower()
        value="no"
        subject_codes,blog_links=get_source(lowersem,value)
    else:
        subject_codes,blog_links=get_source(lowerbranch,semester)

    keyboard = []
    if blog_links and subject_codes!="NULL":
        for i, code in enumerate(subject_codes):
            context.user_data[f"subject_{i}"] = code
            context.user_data[f"link_{i}"] = blog_links[i]
            button = InlineKeyboardButton(code, callback_data=f"subject_{i}")
            keyboard.append([button])
    
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📚 Select your subject:", reply_markup=reply_markup)
    else:
        await query.message.reply_text("❌pdf's not available on website")


async def handle_subject_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject_index = query.data.split("_")[1]
    subject_code = context.user_data.get(f"subject_{subject_index}", "unknown")
    blog_link = context.user_data.get(f"link_{subject_index}", "")
    branch = context.user_data.get("branch", "unknown")

    await query.message.reply_text(f"📚 Fetching pdf's for {branch} - {subject_code} which are available on svit website...")
    await query.message.reply_text("fetching.........wait...")

    if blog_link:
        links = fetch_links_from_url(blog_link)
    
        if links:
            for i, pdf_link in enumerate(links):
                safe_subject_code = re.sub(r'[\\/*?:"<>|]', '-', subject_code)
                filename = f"{safe_subject_code}_{i}.pdf"
                downloaded_file_path = download_file(pdf_link, filename)

                if downloaded_file_path and os.path.exists(downloaded_file_path):
                    try:
                        with open(downloaded_file_path, 'rb') as f:
                            await context.bot.send_document(
                                chat_id=query.message.chat_id,
                                document=InputFile(f, filename=filename),
                                caption=f"{subject_code} ({i+1})"
                            )
                    except Exception as e:
                        await query.message.reply_text(f"loading....")
                else:
                    await query.message.reply_text("❌ Download failed ")
            await query.message.reply_text("✅ sent successfully!") 
            await query.message.reply_text(" Now you can /store the notes  in database to /ask questions")

        else:
            await query.message.reply_text("⚠ No PDF or Google Drive links found on the page.")
    else:
        await query.message.reply_text("❌ Blog link not found.")

async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("storing data in database...wait......")
    try:
        message=rag_pipeline()
        await update.message.reply_text(message)
        await update.message.reply_text("data of these notes also stored sucessfully in database✅")
    except OSError as e:
        await update.message.reply_text("Error in storing the data in database")
        
    try:
        if os.path.exists("C:\\Users\\user\\Downloads\\academic_resource_bot\\downloaded_notes"):
            shutil.rmtree("C:\\Users\\user\\Downloads\\academic_resource_bot\\downloaded_notes")
            print("removed folder from server")
        else:
            await update.message.reply_text("folder is empty to store")
            print("folder is  empty")
    except OSError as e:
        await update.message.reply_text(f"error removing downloaded file{e}")
    await update.message.reply_text("Now you can /ask question on stored notes")

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_question"] = True
    await update.message.reply_text(
        "🧠 Send your question for stored data\n\n"
        "[Note:make sure notes are downloaded and stored in database]\n"
        "[if not - use /notes to download and /store to store data]"
    )
    
# Unknown command handler
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command.\nUse /help to see available options.")

# Unknown message handler
async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_question"):
        context.user_data["awaiting_question"] = False
        question = update.message.text
        await update.message.reply_text("searching for best answer wait.......")
        final_ans=ask_llm(question)
        print("answer sent")
        MAX_LENGTH = 4096
        for i in range(0, len(final_ans), MAX_LENGTH):
            await update.message.reply_text(final_ans[i:i+MAX_LENGTH])
        #await update.message.reply_text(final_ans)
    else:
        await update.message.reply_text("🤔 I didn't understand that message.\nUse /help to see what I can do.")
# Main function
def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_message))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("notes", notes_command))
    application.add_handler(CommandHandler("ask",ask_command))
    application.add_handler(CommandHandler("store",store_command))

    application.add_handler(CallbackQueryHandler(handle_branch_selection, pattern="^branch_"))
    application.add_handler(CallbackQueryHandler(handle_semester_selection, pattern="^sem_"))
    application.add_handler(CallbackQueryHandler(handle_subject_selection, pattern="^subject_"))

    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    try:
        application.run_polling()
    except NetworkError as e:
        print(f"Telegram bot failed due to network error: {e}")

if __name__ == "__main__":
    main()