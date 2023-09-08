# telegram.py interactive pwnagotchi plugin

![Alt text]([image link](https://cdn.discordapp.com/attachments/807640716040732723/1149691096146903111/2023-09-08_13_53_58-bytezero_Mozilla_Firefox.png))

A simple interactive telegram plugin for pwnagotchi the works in manual mdoe and AI mode, When internet is connected it takeS a minute or 3 before you should get a menu 
pop up. 

https://github.com/wpa-2/tele.py (Here is a simple script to test if you have the correct Bot_id and Chat_id)



## Setup
```
__dependencies__ = 
`sudo pip3 uninstall telegram  python-telegram-bot` 
`sudo pip3 install python-telegram-bot==13.15
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
main.plugins.telegram.chat_id = "CHAT ID"
main.plugins.telegram.send_picture = true
main.plugins.telegram.send_message = true
```

Current known issues 
https://github.com/wpa-2/telegram.py/issues/4 -- Working on fixing 


Please report any issues and get in touch over in the pwnagotchi discord. 
