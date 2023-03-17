import logging
import datetime
import re
import os
import time
import subprocess
import pwnagotchi.plugins as plugins
import telegram.ext as telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler

class Telegram(plugins.Plugin):
    __author__ = 'WPA2'
    __version__ = '0.0.8'
    __license__ = 'GPL3'
    __description__ = 'Chats to telegram'
    __dependencies__ = 'python-telegram-bot==13.15',

    def on_loaded(self):
        logging.info("telegram plugin loaded.")
        self.options['auto_start'] = True

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
                     InlineKeyboardButton("Read Banthex Cracked", callback_data='read_banthex_cracked')]]
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

    def read_banthex_cracked(self, agent, update, context):
        file_path = "/root/handshakes/banthex.cracked.potfile"
        chunks = self.read_handshake_pot_files(file_path)
        if not chunks or not any(chunk.strip() for chunk in chunks):
            update.effective_message.reply_text("The banthex.cracked.potfile is empty.")
        else:
            for chunk in chunks:
                update.effective_message.reply_text(chunk)
        
    def handshake_count(self, agent, update, context):
        handshake_dir = "/root/handshakes/"
        count = len([name for name in os.listdir(handshake_dir) if os.path.isfile(os.path.join(handshake_dir, name))])

        response = f"Total handshakes captured: {count}"
        update.effective_message.reply_text(response)
           
    def on_internet_available(self, agent):
        config = agent.config()
        display = agent.view()
        last_session = agent.last_session

        if not hasattr(self, "updater"):
            try:
                logging.info("Connecting to Telegram...")

                self.updater = telegram.Updater(token=self.options['bot_token'])
                bot = self.updater.bot

                # Register command handlers
                self.register_command_handlers(agent, self.updater.dispatcher)

                # Start the Bot's polling in a separate thread
                self.updater.start_polling()

                # Send the start menu to a specific user
                keyboard = [[InlineKeyboardButton("Reboot", callback_data='reboot'),
                             InlineKeyboardButton("Shutdown", callback_data='shutdown')],
                            [InlineKeyboardButton("Uptime", callback_data='uptime'),
                             InlineKeyboardButton("Handshake Count", callback_data='handshake_count')],
                            [InlineKeyboardButton("Read WPA-Sec Cracked", callback_data='read_wpa_sec_cracked'),
                             InlineKeyboardButton("Read Banthex Cracked", callback_data='read_banthex_cracked')]]
                response = "Welcome to Pwnagotchi!\n\nPlease select an option:"
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=self.options['chat_id'], text=response, reply_markup=reply_markup)

            except Exception:
                logging.exception("Error while connecting to Telegram")

    if __name__ == "__main__":
        plugin = Telegram()
        plugin.on_loaded()