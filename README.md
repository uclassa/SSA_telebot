# SSA_telebot
Telegram Bot for SSA

## User Guide
> ⚠️ When adding bot to groups, bot must be promoted to admin in group setting
Currently, functionalities of the bot are the same regardless of whether the chat is a direct message or in a group. However, to interact with the bot in a group chat, you must call the bot with `@uclassa_telebot`.

## Requirements
```pip install -r requirements.txt```
 
## Developer Details

- Bot name: SSA Ah Gong \
- Bot username: uclassa_telebot \
- Check SSA google drive for the `config.env` file, copy and paste it in your local repo. The `.env` file should contain something like this:
  ```
  TOKEN="API_KEY_HERE"
  BOT_USERNAME="@USERNAME"
  ```
- Image from [Ah Kong Durian](https://www.ahkongdurian.com/) - **_Please check for copyright conflicts!_**
  <img src="./img/ahgong.png">

### Workplan

<u> Database </u>
- [ ] Incorporate [Google API](https://developers.google.com/sheets/api/quickstart/python)
- [ ] read from Google Sheets to identify fams according to their telegram username
- [ ] store selected images to Google Drive
- [ ] write to Google Sheets file for tracking fam scores

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
