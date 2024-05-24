#!/usr/bin/env bash

set -e

CONFIG_FILE="/etc/pwnagotchi/config.toml"

function user_sleep() {
	sleep 0.5
}

function verify_internet_connection() {
	# https://stackoverflow.com/questions/929368/how-to-test-an-internet-connection-with-bash
	if wget -q --spider http://google.com; then
		echo "[ + ] You have internet connection, continue with the installation"
	else
		echo "[ - ] You don't have internet connection, please connect to the internet and try again."
		echo "[ ~ ] Refer to https://pwnagotchi.org/getting-started"
		echo "[ ~ ] Also, feel free to chat with us on Discord: https://discord.gg/PgaU3Vp"
		echo "[ ~ ] If you feel that this is an error, please open an issue on https://github.com/wpa-2/telegram.py/issues/new/choose"
		echo "[ ! ] Exiting..."
		exit 0
	fi
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
	if [ "$test_mode" = true ]; then
		return
	fi
	if is_bookworm; then
		pip3 uninstall telegram python-telegram-bot --break-system-packages
	else
		pip3 uninstall telegram python-telegram-bot
	fi
}

function install_dependencies() {
	if [ "$test_mode" = true ]; then
		return
	fi
	if is_bookworm; then
		pip3 install python-telegram-bot==13.15 --break-system-packages
  		sudo apt install python3-qrcode
	else
		pip3 install python-telegram-bot==13.15
  		pip3 install qrcode
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
	if [ "$value" = "true" ]; then
		sed -i "s/^${key} = .*/${key} = ${value}/" "$config_file"
	else
		# Use sed to insert or replace the configuration value
		sed -i "/^${key}/c ${key} = \"${value}\"" "$config_file"
	fi
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

function get_installation_path() {
	check_toml_key_exists "main.custom_plugins" "$CONFIG_FILE"
	installation_dir=$(awk '/^main.custom_plugins = / {print $3}' "$CONFIG_FILE")
	if [ -z "${installation_dir//\"/}" ] || [ "$installation_dir" = true ]; then
		echo "[ ! ] The installation directory was not found in the configuration file"
		read -r -p "Please enter the installation directory, press Enter to set '/usr/local/share/pwnagotchi/custom-plugins' or specify yours with absolute path: " installation_dir
		if [ -z "${installation_dir//\"/}" ]; then
			installation_dir="/usr/local/share/pwnagotchi/custom-plugins"
		fi
		edit_configuration_values "main.custom_plugins" "${installation_dir}" "$CONFIG_FILE"
	fi
}

# Main

# Check that the script is running as root
# If the -t flag is used, the script will be run in test mode
# In test mode, the script will not need to run as root, and will not perform the remove and installation of dependencies.

# Capture user arguments

while getopts "t" options; do
	case $options in
	t)
		test_mode=true
		;;
	\?)
		echo "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	esac
done

if [ "$test_mode" = true ]; then
	echo "[ * ] Running in test mode"
	echo "[ * ] Dependencies will not be removed or installed"
	CONFIG_FILE="config.toml"
elif [ "$EUID" -ne 0 ]; then
	echo "[ ! ] This script need to be run as root"
	exit 0
fi

user_sleep
echo "[ + ] Welcome to the installation script of telegram.py!"
user_sleep
echo "[ + ] Verifying internet connection..."
verify_internet_connection
user_sleep
echo "[ + ] Getting installation path..."
get_installation_path
user_sleep
echo "[ - ] Removing old dependencies..."
remove_dependencies
echo "[ + ] Installing new dependencies..."
install_dependencies
echo "[ + ] Creating symbolic link to ${installation_dir}"
ln -sf "$(pwd)/telegram.py" "${installation_dir//\"/}/telegram.py"
user_sleep
echo "[ + ] Backing up configuration files..."
cp "${CONFIG_FILE}" "${CONFIG_FILE}.bak"
user_sleep
echo "[ ~ ] Modifying configuration files..."
modify_config_files
user_sleep
echo "[ * ] Done! Please restart your pwnagotchi daemon to apply changes"
user_sleep
echo "[ * ] You can do so with:"
user_sleep
echo "[ > ] sudo systemctl restart pwnagotchi"
