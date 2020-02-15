# Exchange Rate Telegram Bot

## Prerequisites:

- installed [ngrok](https://ngrok.com/download)
- installed [docker](https://docs.docker.com/install/)
- bot from @BotFather on Telegram

### Steps for launching project
1. launch ngrok on 5000 by command `ngrok http 5000`
2. on another terminal session `docker build -t exchange-bot .`
3. `docker run -p 5000:5000 -e TOKEN=<your tg bot token> -e WEBHOOK_BASE_URL=<ngrok https url from list> exchange-bot`
4. enjoy it :)

