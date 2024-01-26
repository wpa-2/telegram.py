import logging
import datetime
import re
import os
import time
import subprocess
import telegram
import telegram.ext as tg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, Updater, CommandHandler
import pwnagotchi.plugins as plugins
from pwnagotchi.voice import Voice
import pwnagotchi

class Telegram(plugins.Plugin):
    __author__ = 'WPA2'
    __version__ = '0.0.9'
    __license__ = 'GPL3'
    __description__ = 'Chats to telegram'
    __dependencies__ = 'python-telegram-bot==13.15',

    def on_loaded(self):
        logging.info("telegram plugin loaded.")
        self.logger = logging.getLogger("TelegramPlugin")
        self.options['auto_start'] = True
        self.completed_tasks = 0
        self.num_tasks = 6
        self.updater = None
        self.start_menu_sent = False

    def on_agent(self, agent):
        if 'auto_start' in self.options and self.options['auto_start']:
            self.on_internet_available(agent)

    def register_command_handlers(self, agent, dispatcher):
        dispatcher.add_handler(MessageHandler(Filters.regex('^/start$'), lambda update, context: self.start(agent, update, context)))
        dispatcher.add_handler(CallbackQueryHandler(lambda update, context: self.button_handler(agent, update, context)))

    def start(self, agent, update, context):
        keyboard = [
            [InlineKeyboardButton("Reboot", callback_data='reboot'),
             InlineKeyboardButton("Shutdown", callback_data='shutdown'),
             InlineKeyboardButton("Uptime", callback_data='uptime')],
            [InlineKeyboardButton("Handshake Count", callback_data='handshake_count'),
             InlineKeyboardButton("Read WPA-Sec Cracked", callback_data='read_wpa_sec_cracked'),
             InlineKeyboardButton("Fetch Pwngrid Inbox", callback_data='fetch_pwngrid_inbox')],
            [InlineKeyboardButton("Read Memory & Temp", callback_data='read_memtemp')]
        ]
        
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
        elif query.data == 'handshake_count':
            self.handshake_count(agent, update, context)
        elif query.data == 'fetch_pwngrid_inbox':
            self.handle_pwngrid_inbox(agent, update, context)
        elif query.data == 'read_memtemp':
            self.handle_memtemp(agent, update, context)

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

        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def read_handshake_pot_files(self, file_path):
        try:
            content = subprocess.check_output(['sudo', 'cat', file_path])
            content = content.decode('utf-8')
            matches = re.findall(r'\w+:\w+:(?P<essid>[\w\s-]+):(?P<password>.+)', content)
            formatted_output = [f"{match[0]}:{match[1]}" for match in matches]
            chunk_size = 5
            chunks = [formatted_output[i:i + chunk_size] for i in range(0, len(formatted_output), chunk_size)]
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

        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def handshake_count(self, agent, update, context):
        handshake_dir = "/root/handshakes/"
        count = len([name for name in os.listdir(handshake_dir) if os.path.isfile(os.path.join(handshake_dir, name))])

        response = f"Total handshakes captured: {count}"
        update.effective_message.reply_text(response)

        self.completed_tasks += 1
        if self.completed_tasks == self.num_tasks:
            self.terminate_program()

    def fetch_inbox(self):
        command = "sudo pwngrid -inbox"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        lines = output.split("\n")
        formatted_output = []
        for line in lines:
            if "│" in line:
                message = line.split("│")[1:4]
                formatted_message = "ID: " + message[0].strip().replace('\x1b[2m', '').replace('\x1b[0m', '') + "\n" + \
                                    "Date: " + message[1].strip().replace('\x1b[2m', '').replace('\x1b[0m', '') + "\n" + \
                                    "Sender: " + message[2].strip().replace('\x1b[2m', '').replace('\x1b[0m', '')
                formatted_output.append(formatted_message)

        if len(formatted_output) > 0:
            formatted_output.pop(0)

        return "\n".join(formatted_output)

    def handle_pwngrid_inbox(self, agent, update, context):
        reply = self.fetch_inbox()
        if reply:
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No messages found in Pwngrid inbox.")

    def on_internet_available(self, agent):
        if hasattr(self, 'telegram_connected') and self.telegram_connected:
            return

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
                keyboard = [
                    [InlineKeyboardButton("Reboot", callback_data='reboot'),
                     InlineKeyboardButton("Shutdown", callback_data='shutdown'),
                     InlineKeyboardButton("Uptime", callback_data='uptime')],
                    [InlineKeyboardButton("Handshake Count", callback_data='handshake_count'),
                     InlineKeyboardButton("Read WPA-Sec Cracked", callback_data='read_wpa_sec_cracked'),
                     InlineKeyboardButton("Fetch Pwngrid Inbox", callback_data='fetch_pwngrid_inbox')],
                    [InlineKeyboardButton("Read Memory & Temp", callback_data='read_memtemp')]
                ]
                response = "Welcome to Pwnagotchi!\n\nPlease select an option:"
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(chat_id=self.options['chat_id'], text=response, reply_markup=reply_markup)
                self.start_menu_sent = True

            self.telegram_connected = True

        except Exception as e:
            self.logger.error("Error while sending on Telegram")
            self.logger.error(str(e))

        if last_session.is_new() and last_session.handshakes > 0:
            msg = f"Session started at {last_session.started_at()} and captured {last_session.handshakes} new handshakes"
            self.send_notification(msg)

            if last_session.is_new() and last_session.handshakes > 0:
                message = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
                if self.options['send_message'] is True:
                    bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                    self.logger.info("telegram: message sent: %s" % message)

                picture = '/root/pwnagotchi.png'
                display.on_manual_mode(last_session)
                display.image().save(picture, 'png')
                display.update(force=True)

                if self.options['send_picture'] is True:
                    bot.sendPhoto(chat_id=self.options['chat_id'], photo=open(picture, 'rb'))
                    self.logger.info("telegram: picture sent")

                last_session.save_session_id()
                display.set('status', 'Telegram notification sent!')
                display.update(force=True)

    def handle_memtemp(self, agent, update, context):
        reply = f"Memory Usage: {int(pwnagotchi.mem_usage() * 100)}%\n\nCPU Load: {int(pwnagotchi.cpu_load() * 100)}%\n\nCPU Temp: {pwnagotchi.temperature()}c"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

    def on_handshake(self, agent, filename, access_point, client_station):
        config = agent.config()
        display = agent.view()

        try:
            self.logger.info("Connecting to Telegram...")

            bot = telegram.Bot(self.options['bot_token'])

            message = f"New handshake captured: {access_point['hostname']} - {client_station['mac']}"
            if self.options['send_message'] is True:
                bot.sendMessage(chat_id=self.options['chat_id'], text=message, disable_web_page_preview=True)
                self.logger.info("telegram: message sent: %s" % message)

            display.set('status', 'Telegram notification sent!')
            display.update(force=True)
        except Exception:
            self.logger.exception("Error while sending on Telegram")

    def terminate_program(self):
        logging.info("All tasks completed. Terminating program.")

if __name__ == "__main__":
    plugin = Telegram()
    plugin.on_loaded()