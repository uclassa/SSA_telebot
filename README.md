# SSA_telebot
Telegram Bot for SSA

## User Guide
> ⚠️ When adding bot to groups, bot must be promoted to admin in group setting

## Requirements
```pip install -r requirements.txt```
 
## Developer Details
Currently hosted on https://www.pythonanywhere.com 

- Bot name: SSA Ah Gong \
- Bot username: uclassa_telebot \
- Bot description: As SSA's Ah Gong, I shall watch over SSA - tele channels and make people's lifes easier.
- Check SSA google drive for the `config.env` file, copy and paste it in your local repo. The `.env` file should contain something like this:
  ```
  TOKEN="API_KEY_HERE"
  BOT_USERNAME="@USERNAME"
  ```
- Image from Ah Kong Durian (https://www.ahkongdurian.com/):
  <img src="./img/ahgong.png">
  <!-- Please check for copyright conflicts! -->

### Workplan

<u> Database </u>
- [ ] read from CSV file to identify fams according to their telegram username
- [ ] store selected images
- [ ] write to CSV file for tracking fam scores

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
