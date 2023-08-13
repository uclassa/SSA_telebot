# SSA_telebot
Telegram Bot for SSA

## User Guide
> ⚠️ When adding bot to groups, bot must be promoted to admin in group setting
Currently, functionalities of the bot are the same regardless of whether the chat is a direct message or in a group. However, to interact with the bot in a group chat, you must call the bot with `@uclassa_telebot`.

Groups will be added to the list of known group IDs only when `/start` command is called in the group that the bot is in. **Only known groups will receive announcement broadcasts.**

## Developer Notes

- Bot name: SSA Ah Gong \
- Bot username: uclassa_telebot \
- Check SSA google drive for the `config.env` file, copy and paste it in your local repo. The `.env` file should contain something like this:
- Image from [Ah Kong Durian](https://www.ahkongdurian.com/) - **_Please check for copyright conflicts!_**
  <img src="./img/ahgong.png">

### Requirements
```pip install -r requirements.txt```

### Backend Details

(Skip to step 3 if you already have `token.json`)
1. Copy `credentials.json` from Google Cloud Platform or the Google Drive 'Telebot' folder to the root folder of the repo. 
2. Run `quickstart.py` in the `backend` folder to generate `token.json` in the root folder of the repo.
3. Copy the following fields from the `token.json` into `config.env` and name them accordingly:
    ```
    "refresh_token": os.environ.get('google_refresh_token'),
    "client_id": os.environ.get('google_client_id'),
    "client_secret": os.environ.get('google_client_secret'),
    "token_uri": os.environ.get('google_token_uri'),
    ```
This is support deployment on Railway where we set the environment variables manually.

### Workplan

<u> Database </u>
- [x] Incorporate [Google API](https://developers.google.com/sheets/api/quickstart/python)
- [ ] read from Google Sheets to identify fams according to their telegram username
- [ ] store selected images to Google Drive
- [ ] write to Google Sheets file for tracking fam scores
- [x] read event information from Google Sheets
- [x] send reminders if event is coming up in 7 days (add Groups with the bot will be updated)

<u> Telegram API </u>
- [ ] identify an image being sent and the user information
- [ ] identify context and group images based on event/fam
- [ ] create a response AI (bonus: use some singaporean speech generator)

<u> Image Detection </u>
- [ ] facial recognition
- [ ] similarity comparison to identify photos from the same event/activity
- [ ] filter unrelated images (non fam outing/hangout type of images)
- [ ] quality selection to find the best photo within a group of photos

<u> Others </u>
- [ ] error handling
- [ ] testing
- [ ] time zone based on event location or based on user location
