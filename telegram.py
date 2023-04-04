import logging
import datetime
import re
import os
import time
import subprocess
import telegram
import json
import telegram.ext as tg
import pwnagotchi.plugins as plugins
from pwnagotchi.voice import Voice
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, Updater

class Telegram(plugins.Plugin):
    __author__ = 'WPA2'
    __version__ = '0.0.9'
    __license__ = 'GPL3'
    __description__ = 'Chats to telegram'
    __dependencies__ = 'python-telegram-bot==13.15',

    def on_loaded(self):
        logging.info("telegram plugin loaded.")
        self.options['auto_start'] = True
        self.completed_tasks = 0
        self.num_tasks = 6  # Update this value to match the number of tasks performed by this plugin
        self.updater = None  # Add this line to initialize the updater attribute
        self.start_menu_sent = False
        self.last_try_time = 0

    def on_agent(self, agent):
        if 'auto_start' in self.options and self.options['auto_start']:
            self.on_internet_available(agent)

    def register_command_handlers(self, agent, dispatcher):
        dispatcher.add_handler(MessageHandler(Filters.regex('^/start$'), lambda update, context: self.start(agent, update, context)))
        dispatcher.add_handler(CallbackQueryHandler(lambda update, context: self.button_handler(agent, update, context)))

    def start(self, agent, update, context):
        keyboard = [[InlineKeyboardButton("Reboot", callback_data='reboot'),
                     InlineKeyboardButton("Shutdown", callback_data='shutdown')],
                    [InlineKeyboardButton("Uptime", callback_data='uptime'),
                     InlineKeyboardButton("Handshake Count", callback_data='handshake_count')],
                    [InlineKeyboardButton("Read WPA-Sec Cracked", callback_data='read_wpa_sec_cracked'),
                     InlineKeyboardButton("Read Banthex Cracked", callback_data='read_banthex_cracked')],
                    [InlineKeyboardButton("BT Sniffed Info", callback_data='bt_sniff_info'),
                     InlineKeyboardButton("Empty", callback_data='empty')]]
        response = "Welcome to Pwnagotchi!\n\nPlease select an option:"
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(response, reply_markup=reply_markup)

    def button_handler(self, agent, update, context):
        query = update.callback_query
        query.answer()
        if query.data == 'reboot':
            self.reboot(agent, update, context)
        elif query.data == 'shutdown':
            self.shutdown(agent, update, context)
        elif query.data == 'uptime':
            self.uptime(agent, update, context)
        elif query.data == 'read_wpa_sec_cracked':
            self.read_wpa_sec_cracked(agent, update, context)
        elif query.data == 'read_banthex_cracked':
            self.read_banthex_cracked(agent, update, context)
        elif query.data == 'handshake_count':
            self.handshake_count(agent, update, context)
        elif query.data == 'bt_sniff_info':
            self.bt_sniff_info(agent, update, context)
        elif query.data == 'empty':
            return

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def reboot(self, agent, update, context):
        response = "Rebooting now..."
        update.effective_message.reply_text(response)
        subprocess.run(['sudo', 'reboot'])

    def shutdown(self, agent, update, context):
        response = "Shutting down now..."
        update.effective_message.reply_text(response)
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])

    def uptime(self, agent, update, context):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])

        uptime_minutes = uptime_seconds / 60
        uptime_hours = int(uptime_minutes // 60)
        uptime_remaining_minutes = int(uptime_minutes % 60)

        response = f"Uptime: {uptime_hours} hours and {uptime_remaining_minutes} minutes"
        update.effective_message.reply_text(response)

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def read_handshake_pot_files(self, file_path):
        try:
            content = subprocess.check_output(['sudo', 'cat', file_path])
            content = content.decode('utf-8')

            # Extract ESSID and password using regex
            matches = re.findall(r'\w+:\w+:(?P<essid>[\w\s-]+):(?P<password>.+)', content)

            # Format the output
            formatted_output = []
            for match in matches:
                formatted_output.append(f"{match[0]}:{match[1]}")

            # Split output into small chunks
            chunk_size = 5  # Adjust this value to change the number of lines per chunk
            chunks = [formatted_output[i:i + chunk_size] for i in range(0, len(formatted_output), chunk_size)]

            # Join the chunks into strings
            chunk_strings = ['\n'.join(chunk) for chunk in chunks]
            return chunk_strings

        except subprocess.CalledProcessError as e:
            return [f"Error reading file: {e}"]

    def read_wpa_sec_cracked(self, agent, update, context):
        file_path = "/root/handshakes/wpa-sec.cracked.potfile"
        chunks = self.read_handshake_pot_files(file_path)
        if not chunks or not any(chunk.strip() for chunk in chunks):
            update.effective_message.reply_text("The wpa-sec.cracked.potfile is empty.")
        else:
            for chunk in chunks:
                update.effective_message.reply_text(chunk)

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def read_banthex_cracked(self, agent, update, context):
        file_path = "/root/handshakes/banthex.cracked.potfile"
        chunks = self.read_handshake_pot_files(file_path)
        if not chunks or not any(chunk.strip() for chunk in chunks):
            update.effective_message.reply_text("The banthex.cracked.potfile is empty.")
        else:
            for chunk in chunks:
                update.effective_message.reply_text(chunk)

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def handshake_count(self, agent, update, context):
        handshake_dir = "/root/handshakes/"
        count = len([name for name in os.listdir(handshake_dir) if os.path.isfile(os.path.join(handshake_dir, name))])

        response = f"Total handshakes captured: {count}"
        update.effective_message.reply_text(response)

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def on_internet_available(self, agent):
        # Send message about Bluetooth Sniffed that is New or Updated
        self.bt_sniff_message(agent)

        if hasattr(self, 'telegram_connected') and self.telegram_connected:
            return  # Skip if already connected

        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        try:
            logging.info("Connecting to Telegram...")
            bot = telegram.Bot(self.options['bot_token'])

            if self.updater is None:
                self.updater = Updater(token=self.options['bot_token'], use_context=True)
                self.register_command_handlers(agent, self.updater.dispatcher)
                self.updater.start_polling()

            if not self.start_menu_sent:
                keyboard = [[InlineKeyboardButton("Reboot", callback_data='reboot'),
                             InlineKeyboardButton("Shutdown", callback_data='shutdown')],
                            [InlineKeyboardButton("Uptime", callback_data='uptime'),
                             InlineKeyboardButton("Handshake Count", callback_data='handshake_count')],
                            [InlineKeyboardButton("Read WPA-Sec Cracked", callback_data='read_wpa_sec_cracked'),
                             InlineKeyboardButton("Read Banthex Cracked", callback_data='read_banthex_cracked')],
                            [InlineKeyboardButton("BT Sniffed Info", callback_data='bt_sniff_info'),
                             InlineKeyboardButton("Empty", callback_data='empty')]]
                response = "Welcome to Pwnagotchi!\n\nPlease select an option:"
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=self.options['chat_id'], text=response, reply_markup=reply_markup)
                self.start_menu_sent = True

            # Set the flag to indicate that the connection has been established
            self.telegram_connected = True

        except Exception as e:
            logging.error("Error while sending on Telegram")
            logging.error(str(e))

        if last_session.is_new() and last_session.handshakes > 0:
            msg = f"Session started at {last_session.started_at()} and captured {last_session.handshakes} new handshakes"
            self.send_notification(msg)

            if last_session.is_new() and last_session.handshakes > 0:
                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                if self.options['send_message'] is True:
                    bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                    logging.info("telegram: message sent: %s" % message)

                picture = '/root/pwnagotchi.png'
                display.on_manual_mode(last_session)
                display.image().save(picture, 'png')
                display.update(force=True)

                if self.options['send_picture'] is True:
                    bot.sendPhoto(chat_id=self.options['chat_id'], photo=open(picture, 'rb'))
                    logging.info("telegram: picture sent")

                last_session.save_session_id()
                display.set('status', 'Telegram notification sent!')
                display.update(force=True)

    def on_handshake(self, agent, filename, access_point, client_station):
        config = agent.config()
        display = agent.view()

        try:
            logging.info("Connecting to Telegram...")

            bot = telegram.Bot(self.options['bot_token'])

            message = "New handshake captured: {} - {}".format(access_point['hostname'], client_station['mac'])
            if self.options['send_message'] is True:
                bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                logging.info("telegram: message sent: %s" % message)

            display.set('status', 'Telegram notification sent!')
            display.update(force=True)
        except Exception:
            logging.exception("Error while sending on Telegram")

    def terminate_program(self):
        # This function will be called once all tasks have been completed
        # You can add additional cleanup code here if needed
        logging.info("All tasks completed. Terminating program.")

    def bt_sniff_message(self, agent):
        config = agent.config()
        display = agent.view()
        current_time = time.time()
        try:
            bts_timer = self.options['bts_timer']
        except Exception:
            bts_timer = 45
        try:
            bts_json_file = self.options['bts_json_file']
        except Exception:
            bts_json_file = '/root/handshakes/bluetooth_devices.json'
        # Checking the time elapsed since last scan
        if os.path.exists(bts_json_file) and os.path.getsize(self.options['devices_file']) != 0:
            if current_time - self.last_try_time >= bts_timer:
                logging.info("[BtST] Trying to check BT json...")
                self.last_try_time = current_time
                try:
                    # load the JSON file
                    with open(bts_json_file, 'r') as f:
                        bluetooth_data = json.load(f)
                    # check if there is any new info
                    for mac in bluetooth_data:
                        if bluetooth_data[mac]['new_info'] == True:
                            logging.info("[BtST] Connecting to Telegram...")
                            bot = telegram.Bot(self.options['bot_token'])
                            message = f"New Bluetooth device detected:\n\nName: {bluetooth_data[mac]['name']}\nMAC: {mac}\nManufacturer: {bluetooth_data[mac]['manufacturer']}\nFirst Seen: {bluetooth_data[mac]['first_seen']}\nLast Seen: {bluetooth_data[mac]['last_seen']}"
                            logging.info("[BtST] Sending: %s" % message)
                            bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                            bluetooth_data[mac]['new_info'] = False
                            with open(bts_json_file, 'w') as f:
                                json.dump(bluetooth_data, f)
                            logging.info("[BtST] telegram: message sent: %s" % message)
                            display.set('status', 'Telegram notification for Bluetooth sent!')
                            display.update(force=True)
                        elif bluetooth_data[mac]['new_info'] == 2:
                            logging.info("[BtST] Connecting to Telegram...")
                            bot = telegram.Bot(self.options['bot_token'])
                            message = f"Bluetooth device updated:\n\nName: {bluetooth_data[mac]['name']}\nMAC: {mac}\nManufacturer: {bluetooth_data[mac]['manufacturer']}\nFirst Seen: {bluetooth_data[mac]['first_seen']}\nLast Seen: {bluetooth_data[mac]['last_seen']}"
                            logging.info("[BtST] Sending: %s" % message)
                            bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                            bluetooth_data[mac]['new_info'] = False
                            with open(bts_json_file, 'w') as f:
                                json.dump(bluetooth_data, f)
                            logging.info("[BtST] telegram: message sent: %s" % message)
                            display.set('status', 'Telegram notification for Bluetooth sent!')
                            display.update(force=True)
                except Exception:
                    logging.exception("[BtST] Error while sending Bluetooth data on Telegram")

    def bt_sniff_info(self, agent, update, context):
        logging.info("[BtST] Reading JSON file...")
        try:
            bts_json_file = self.options['bts_json_file']
        except Exception:
            bts_json_file = '/root/handshakes/bluetooth_devices.json'
        if os.path.exists(bts_json_file) and os.path.getsize(self.options['devices_file']) != 0:
            with open(bts_json_file, 'r') as f:
                bluetooth_data = json.load(f)
            num_devices = len(bluetooth_data)
            num_unknown = sum(1 for device in bluetooth_data.values() if device['name'] == 'Unknown' or device['manufacturer'] == 'Unknown')
            num_known = num_devices - num_unknown
            response = f"Bluetooth Sniffed Info\n\nAll of them: %s\Fully sniffed: %s" % (num_devices, num_known)
            logging.info("[BtST] Telegram message: %s" % response)
        else:
            response = f"[BtST] Plugin bluetoothsniffer is not loaded."
        update.effective_message.reply_text(response)

        # Increment the number of completed tasks and check if all tasks are completed
        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

if __name__ == "__main__":
    plugin = Telegram()
    plugin.on_loaded()