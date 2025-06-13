from dotenv import load_dotenv
import os
import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

load_dotenv()

# Update OGs accordingly, you can add or remove OGs too
ogs = ["Vesper", "Xenon","Sphera", "Nexus"]
RANGE = "OG_data!A2:H"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
TOKEN = os.getenv('TOKEN')

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
with open("token.json", "w") as token:
    token.write(creds.to_json())

service = build("sheets", "v4", credentials=creds)

def readSpreadsheet():
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE)
        .execute()
    )
    values = result.get("values", [])

    if not values:
        print("No data found.")
        return

    return values

def getData(selected_og):
    values = readSpreadsheet()

    if not values:
        print("No data found.")
        return

    data = [[] for i in range(len(ogs))]

    for row in values:
        for index in range(len(row)):
            if (index % 2 == 1):
                data[index // 2].append(row[index - 1 : index + 1])

    for index, og in enumerate(ogs):
        if (og == selected_og):
            while ['',''] in data[index]:
                data[index].remove(['',''])
            return data[index]

def getOGInfo(selected_og):
    data = getData(selected_og)
    _, location = data.pop(0)
    total_list = data
    present_list = []
    absent_list = []
    for person in data:
        if person[1] == "PRESENT":
            present_list.append(person)
        else:
            absent_list.append(person)
    return total_list, present_list, absent_list, location

def handleChangeAbsent(selected_og, name, reason):
    values = readSpreadsheet()

    for row in values:
        for i in range(len(row)):
            if (row[i] == name):
                row[i + 1] = reason
                break

    value_input_option = "USER_ENTERED"
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range="OG_data!A2:H", valueInputOption=value_input_option, body=body
    ).execute()

def handleChangePresent(selected_og, name):
    values = readSpreadsheet()

    for row in values:
        for i in range(len(row)):
            if (row[i] == name):
                row[i + 1] = "PRESENT"
                break

    value_input_option = "USER_ENTERED"
    body = {
        'values': values
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range="OG_data!A2:H", valueInputOption=value_input_option, body=body
    ).execute()

def handleChangeLocation(selected_og, new_location):
    values = readSpreadsheet()

    og_locations = values[0]
    og_locations[ogs.index(selected_og) * 2 + 1] = new_location

    value_input_option = "USER_ENTERED"
    body = {
        'values': values
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range="OG_data!A2:H", valueInputOption=value_input_option, body=body
    ).execute()

def runTelegramBot():

    logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    DASHBOARD, CHANGELOCATION, SETABSENT, SETPRESENT = range(4)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Send message on `/start`."""
        user = update.message.from_user
        logger.info("User %s started the conversation.", user.first_name)
        context.user_data['userName'] = user.first_name
        keyboard = [[InlineKeyboardButton(og, callback_data=og)] for og in ogs]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Welcome to the OMC Attendance bot.\n\nPlease select your OG!", reply_markup=reply_markup)
        return DASHBOARD

    async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = update.callback_query.data
        context.user_data["OG"] = og

        total_list, present_list, absent_list, location = getOGInfo(og)

        absent_text = ""
        for person in absent_list:
            text = " ".join([person[0], "(" + person[1] + ")"])
            absent_text = "\n".join([absent_text, text])

        total_strength = len(total_list)
        present_strength = len(present_list)
        absent_strength = len(absent_list)

        """Show new choice of buttons"""
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("View Present", callback_data="View Present")],
            [InlineKeyboardButton("View Absent", callback_data="View Absent")],
            [InlineKeyboardButton("Change Location", callback_data="Change Location")],
        ]

        helper_text = f"You have selected {og}\n\nCurrent Location: {location}\nTotal Strength: {total_strength}\nPresent: {present_strength}\nAbsent: {absent_strength}\n" + absent_text + "\n\nPlease select an action."

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = helper_text, reply_markup = reply_markup
        )
        return DASHBOARD

    async def present(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]
        context.user_data["PRESENT/ABSENT"] = "View Present"

        _, present_names, _, _ = getOGInfo(og)

        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in present_names]
        keyboard.append([InlineKeyboardButton("Go Back", callback_data=og)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + ":\n\nList of people who are currently PRESENT.\n\nSelect anyone to edit their information.", reply_markup = reply_markup
        )
        return DASHBOARD

    async def absent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]
        context.user_data["PRESENT/ABSENT"] = "View Absent"

        _, _, absent_names, _ = getOGInfo(og)

        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in absent_names]
        keyboard.append([InlineKeyboardButton("Go Back", callback_data=og)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + ":\n\nList of people who are currently ABSENT.\n\nSelect anyone to edit their information.", reply_markup = reply_markup
        )
        return DASHBOARD

    async def changeLocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]

        _, _, _, location = getOGInfo(og)

        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data=og)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + f":\n\nCurrent Location: {location}.\n\nType a new location to change your location.\n\nIf you do not want to change your location, type: {location}", reply_markup = reply_markup
        )
        return CHANGELOCATION

    async def setPresent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]
        name = context.user_data["name"]
        prev = context.user_data["PRESENT/ABSENT"]

        handleChangePresent(og, name)

        user = context.user_data['userName']

        dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open("attendance.txt", "a")
        f.write(f"{dateTime} {og}: User {user} set {name} as PRESENT\n")
        f.close()

        logger.info("%s: User %s set %s as present", og, user, name)


        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data=prev)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + ":\n\n" + name + ".\n\nSuccess!", reply_markup = reply_markup
        )
        return DASHBOARD

    async def setAbsent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]
        name = context.user_data["name"]
        prev = context.user_data["PRESENT/ABSENT"]

        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Go Back", callback_data=prev)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + ":\n\n" + name + ".\n\nPlease key in a reason or ETA.\n\nYou have to input something before pressing 'Go Back'", reply_markup = reply_markup
        )
        return SETABSENT

    async def editStatus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        og = context.user_data["OG"]
        prev = context.user_data["PRESENT/ABSENT"]

        if update.callback_query.data:
            name = update.callback_query.data
            context.user_data["name"] = name
        else:
            name = context.user_data["name"]

        """Show new choice of buttons"""
        query = update.callback_query

        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Set Present", callback_data="Set Present")],
            [InlineKeyboardButton("Set Absent/Late", callback_data="Set Absent")],
            [InlineKeyboardButton("Go Back", callback_data=prev)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text = og + ":\n\n" + name + ".\n\nSelect an action below.", reply_markup = reply_markup
        )
        return DASHBOARD

    async def getReason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        reason = update.message.text
        name = context.user_data["name"]
        og = context.user_data["OG"]

        user = context.user_data['userName']

        dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open("attendance.txt", "a")
        f.write(f"{dateTime} {og}: User {user} set {name} as ABSENT with reason: {reason}\n")
        f.close()

        logger.info("%s: User %s set %s as absent with reason: %s", og, user, name, reason)
        handleChangeAbsent(og, name, reason)

        await update.message.reply_text("Success! Press 'Go Back'")
        return DASHBOARD

    async def setLocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        new_location = update.message.text.upper()
        og = context.user_data["OG"]

        user = context.user_data["userName"]

        dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f = open("attendance.txt", "a")
        f.write(f"{dateTime} {og}: User {user} changed location to {new_location}\n")
        f.close()

        logger.info("%s: User %s changed location to %s", og, user, new_location)
        handleChangeLocation(og, new_location)

        await update.message.reply_text("Success! Press 'Go Back'")
        return DASHBOARD

    application = ApplicationBuilder().token(TOKEN).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    regex_for_ogs = "|".join([f"^{og}$" for og in ogs])
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DASHBOARD: [
                CallbackQueryHandler(present, pattern="^" + "View Present" + "$"),
                CallbackQueryHandler(absent, pattern="^" + "View Absent" + "$"),
                CallbackQueryHandler(changeLocation, pattern="^" + "Change Location" + "$"),
                CallbackQueryHandler(setPresent, pattern="^" + "Set Present" + "$"),
                CallbackQueryHandler(setAbsent, pattern="^" + "Set Absent" + "$"),
                CallbackQueryHandler(dashboard, pattern=regex_for_ogs),
                CallbackQueryHandler(editStatus)
            ],
            CHANGELOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, setLocation)
            ],
            SETABSENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, getReason)
            ],
            SETPRESENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, setPresent)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    runTelegramBot()

if __name__ == "__main__":
  main()
