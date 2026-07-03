from pyrogram import Client, filters

# നിങ്ങളുടെ വിവരങ്ങൾ ഇവിടെ ചേർത്തിരിക്കുന്നു
api_id = "29192466"
api_hash = "03bac9431503cb805fee8b6a19ed31c3"
bot_token = "8809575029:AAHZJEKV64f7n1k2vwYOeeQfOkujhWZDKGQ"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("ഹലോ! ഞാൻ റെഡിയാണ്.")

app.run()
