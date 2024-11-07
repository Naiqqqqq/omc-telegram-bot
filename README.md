# Orientation Attendance Bot

A Telegram bot created to streamline attendance taking and tracking within orientation camps.

## Getting Started

### 1. Install Python

```
brew install python
```

OR

[Download it here](https://www.python.org/downloads/)

### 2. Install dependencies

```
pip3 install -r requirements.txt
```

OR

```
pip install -r requirements.txt
```

### 3. Link up with Google Cloud Console

- [Create a Google Cloud Console project](console.cloud.google.com)
- Go to APIs and Services --> Credentials
- Create Credentials --> OAuth client ID --> Desktop app
- Download the `credentials.json` file generated and place it in the root directory of the application

### 4. Link up with Google Sheets

- Copy this [Google Sheets template](https://docs.google.com/spreadsheets/d/1VHlun2B3p2ckcK-9hMN5P0bEglbYmqnBE19aVN79G2o/edit?usp=sharing) onto your Google Drive
- Create a `.env` file in the root directory and copy the spreadsheet ID

```
SPREADSHEET_ID=<your-spreadsheet-id>
```

### 5. Link up with Telegram bot

- Create a new Telegram bot with BotFather
- Get the bot token and copy it into the `.env` file

```
TOKEN=<your-token-here>
```

### 6. Update OG names

- Update OG names on both the Google Sheets and on line 19 in `app.py`

## Run the application

```
python3 app.py
```

OR

```
python app.py
```

## How it works

- Real-time attendance will be updated on the Google Sheets accordingly
- Attendance log will be generated and updated in `attendance.txt`

## How to use it

- Users have to find the Telegram bot by name on Telegram
- Type `/start` to start or reset the bot

## Changing the number of OGs

- You can change the number of OGs by removing or adding columns on the `OG_data` spreadsheet
- Edit the OGs accordingly on line 19 in `app.py`

## Refresh Token

- When token in `token.json` expires, generate a new one by deleting `token.json` and running the application.
