#!/usr/bin/env bash

INSTALLATION_DIRECTORY="/usr/local/share/pwnagotchi/custom-plugins"
CONFIG_FILE="/etc/pwnagotchi/config.toml"

function user_sleep() {
	sleep 0.5
}

function is_bookworm() {
	is_bookworm=$(grep "bookworm" /etc/os-release)
	if [ -z "$is_bookworm" ]; then
		return 1
	else
		return 0
	fi
}

function remove_dependencies() {
	pip3 uninstall telegram python-telegram-bot
}

function install_dependencies() {
	pip3 uninstall telegram python-telegram-bot

	if is_bookworm; then
		pip3 install python-telegram-bot==13.15 --break-system-packages
	else
		pip3 install python-telegram-bot==13.15
	fi
}

function check_toml_key_exists() {
	local key="$1"
	local config_file="$2"

	if grep -q "^${key}" "$config_file"; then
		echo "The '$key' already exists on $config_file."
	else
		echo "Creating '$key' on $config_file."
		echo "${key} = true " >>"$config_file"
	fi
}

function edit_configuration_values() {
	local key="$1"
	local value="$2"
	local config_file="$3"

	# Escape slashes and dots in the value to avoid issues with sed
	value=$(echo "$value" | sed 's/\//\\\//g')
	value=$(echo "$value" | sed 's/\./\\\./g')
	# Use sed to insert or replace the configuration value
	sed -i "/^${key}/c ${key} = \"${value}\"" "$config_file"
}

function modify_config_files() {
	# TODO If you know a simple method to write on toml files, please submit a change
	echo "Please enter the following details:"
	read -rp "Bot Token: " botid
	read -rp "Bot Name: " botname
	read -rp "Chat ID: " chatid

	check_toml_key_exists "main.plugins.telegram.enabled" "$CONFIG_FILE"
	check_toml_key_exists "main.plugins.telegram.bot_token" "$CONFIG_FILE"
	check_toml_key_exists "main.plugins.telegram.bot_name" "$CONFIG_FILE"
	check_toml_key_exists "main.plugins.telegram.chat_id" "$CONFIG_FILE"
	check_toml_key_exists "main.plugins.telegram.send_picture" "$CONFIG_FILE"
	check_toml_key_exists "main.plugins.telegram.send_message" "$CONFIG_FILE"

	# Set the configuration values
	edit_configuration_values "main.plugins.telegram.enabled" "true" "$CONFIG_FILE"
	edit_configuration_values "main.plugins.telegram.bot_token" "$botid" "$CONFIG_FILE"
	edit_configuration_values "main.plugins.telegram.bot_name" "$botname" "$CONFIG_FILE"
	edit_configuration_values "main.plugins.telegram.chat_id" "$chatid" "$CONFIG_FILE"
	edit_configuration_values "main.plugins.telegram.send_picture" "true" "$CONFIG_FILE"
	edit_configuration_values "main.plugins.telegram.send_message" "true" "$CONFIG_FILE"
}

# Main

# Check that the script is running as root

if [ "$EUID" -ne 0 ]; then
	echo "[ ! ] This script need to be run as root"
	exit 0
fi
echo "[ - ] Removing old dependencies..."
# remove_dependencies
echo "[ + ] Installing new dependencies..."
# install_dependencies
echo "[ + ] Creating symbolic link to ${INSTALLATION_DIRECTORY}"
# ln -sf "$(pwd)/telegram.py" "${INSTALLATION_DIRECTORY}/telegram-py"
echo "[ + ] Backing up configuration files..."
# cp "${CONFIG_FILE}" "${CONFIG_FILE}.bak"
echo "[ ~ ] Modifying configuration files..."
modify_config_files
echo "[ * ] Done! Please restart your pwnagotchi daemon to apply changes"
echo "[ * ] You can do so with:"
echo "[ > ] sudo systemctl restart pwnagotchi"

