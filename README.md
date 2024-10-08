# SSA_telebot
This is the Telegram Bot for SSA@UCLA! We use the <a href="https://python-telegram-bot.org/">`python-telegram-bot`</a> framework for our development.

## Developer Notes

- Bot name: SSA Ah Gong
- Bot username: uclassa_telebot
- Image from [Ah Kong Durian](https://www.ahkongdurian.com/) - **_Please check for copyright conflicts!_**

  <img src="./img/ahgong.png">

### Environment Variables
Check the `config.env.template` file for the required environment variables. You can leave `TIMEZONE` blank. Use any api key you want, but just make sure it matches the one you use on your local django server. Refer to <a href="https://core.telegram.org/bots/tutorial#obtain-your-bot-token">telegram's documentation</a> on how to get a `TOKEN`.

### Running Locally
Refer to the <a href="https://github.com/uclassa/charkwayteow">`charkwayteow`</a> repository's README for steps to set up a python virtual environment. Install the required dependencies and run `src/main.py` to run the bot.
```
pip3 install -r requirements.txt
python3 src/main.py
```

Most of the functionality of the bot is closely tied with the backend server. Follow the instructions in the `charkwayteow` repository to run it locally.

### Workplan

See <a href="https://www.notion.so/SSA-SWE-b1b5607878fa429ba967ea707d0ca5b4?pvs=4">notion page</a> for more details.
