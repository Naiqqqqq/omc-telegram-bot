# OMC Attendance Bot

A Telegran Bot created to streamline attendance taking and tracking within orientation camps.

## Getting Started

### 1. Install python \(created with 3.12.5\)

`brew install python`

OR

Download it here(https://www.python.org/downloads/)

### 2. Install dependencies

`pip3 install -r requirements.txt`

OR

`pip install -r requirements.txt`

### 3. Link up with Google Cloud Console

- Create a Google Cloud Console project here(console.cloud.google.com)
- Go to APIs and Services --> Credentials
- Create Credentials --> OAuth client ID --> Desktop app
- Download the `credentials.json` file generated and place it in the root directory of the application

### 4. Link up with Google Sheets

- Copy this google sheets template(https://docs.google.com/spreadsheets/d/14jbJnMyWMaDqw9ZoF5UAC62kja30Ux8x/edit?usp=sharing&ouid=107399073491140729219&rtpof=true&sd=true) onto your Google Drive
- Create a .env file in the root directory and copy the spreadsheet ID

`SPREADSHEET_ID=<your-spreadsheet-id>`

### 5. Link up with Telegram Bot

- Create a new Telegram Bot with BotFather
- Get the bot token and copy it into the `.env` file

`TOKEN=<your-token-here>`

## Run the application

`python3 app.py`

OR

`python app.py`
