# telegram.py Interactive pwnagotchi plugin


![Screenshot 2024-02-09 230346](https://github.com/wpa-2/telegram.py/assets/9049886/7733bb84-64b5-493e-b0ba-b8a386f2d348)




A simple interactive telegram plugin for pwnagotchi the works in manual mode and AI mode, When internet is connected it takes a minute or 3 before you should get a menu
pop up.

https://github.com/wpa-2/tele.py (Here is a simple script to test if you have the correct Bot_id and Chat_id)



## Setup

### Via installation script

From your pwnagotchi's user home directory (```cd $HOME```), run the following command:

``` bash
git clone https://github.com/wpa-2/telegram.py telegram-bot
cd telegram-bot
chmod 744 install.sh
./install.sh
```

This script will do the same manual steps as listed bellow.

### Manual
```
__dependencies__ =
`sudo pip3 uninstall telegram  python-telegram-bot`
`sudo pip3 install python-telegram-bot==13.15`
`For newer OS's like bookworm issues this command`
`sudo pip3 install python-telegram-bot==13.15 --break-system-packages`

```

Copy plugin to your custom folder normally here
```
/usr/local/share/pwnagotchi/custom-plugins
```

Edit your config.toml wit there details
```
main.plugins.telegram.enabled = true
main.plugins.telegram.bot_token = "BOT ID"
main.plugins.telegram.bot_name = "pwnagotchi"
main.plugins.telegram.chat_id = CHAT ID
main.plugins.telegram.send_picture = true
main.plugins.telegram.send_message = true
```

Current known issues
None

Please report any issues and get in touch over in the pwnagotchi discord.

Special thank you to https://github.com/nothingbutlucas for all his hard work impriving the bot. 
