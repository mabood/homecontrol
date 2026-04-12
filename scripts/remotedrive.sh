#!/bin/bash

# --- CONFIGURATION ---
CONF_FILE="$(dirname "$0")/drives.conf" # Looks for drives.conf in the same folder
# Create a unique socket file for this SSH session in a temporary directory
SSH_SOCKET="/tmp/ssh_mux_$(date +%s)_$$"
# ---------------------

# 1. Validate that the configuration file exists
if [ ! -f "$CONF_FILE" ]; then
    echo "Error: Configuration file '$CONF_FILE' not found."
    exit 1
fi

# 2. Extract the HOST connection string (user@ip)
SSH_TARGET=$(grep "^HOST:" "$CONF_FILE" | cut -d':' -f2)

if [ -z "$SSH_TARGET" ]; then
    echo "Error: No 'HOST:' line found in $CONF_FILE."
    echo "Please add a line like: HOST:username@192.168.1.50"
    exit 1
fi

# Function to safely close the shared SSH connection when exiting
cleanup() {
    # Only run cleanup if the socket actually exists to avoid looping errors
    if [ -S "$SSH_SOCKET" ]; then
        echo -e "\nClosing background SSH connection..."
        ssh -S "$SSH_SOCKET" -O exit "$SSH_TARGET" 2>/dev/null
        rm -f "$SSH_SOCKET"
    fi
    exit 0
}
# TRIGGER CLEANUP on normal exit, Ctrl+C (INT), or termination signals (TERM)
trap cleanup EXIT INT TERM

echo "Establishing persistent connection to $SSH_TARGET..."
echo "Please enter your SSH password when prompted (You will only need to do this once):"

# Start the shared master connection in the background
ssh -M -S "$SSH_SOCKET" -fN "$SSH_TARGET"

if [ $? -ne 0 ]; then
    echo "Failed to establish SSH connection. Exiting."
    exit 1
fi

# Define a standard function to use the shared SSH tunnel
run_ssh() {
    ssh -S "$SSH_SOCKET" "$SSH_TARGET" "$1"
}

# Infinite loop to keep the UI open
while true; do
    clear
    echo "========================================="
    echo " Remote Mac Drive Manager"
    echo " Target: $SSH_TARGET"
    echo "========================================="
    
    # --- LIST DRIVES ---
    echo "Fetching mounted drives..."
    DRIVE_LIST=$(grep "^DRIVE:" "$CONF_FILE" | cut -d':' -f2 | paste -sd '|' -)
    
    if [ -z "$DRIVE_LIST" ]; then
        echo "No drives are configured in $CONF_FILE."
    else
        MOUNTED_DRIVES=$(run_ssh "df -h | grep '/Volumes/' | grep -E '$DRIVE_LIST'")
        if [ -z "$MOUNTED_DRIVES" ]; then
            echo "-> 0 drives matching configuration are currently mounted."
        else
            echo "$MOUNTED_DRIVES"
        fi
    fi
    echo "========================================="
    
    # --- DISPLAY AVAILABLE DRIVES ---
    echo "Configured Drives:"
    grep "^DRIVE:" "$CONF_FILE" | cut -d':' -f2 | sed 's/^/  - /'
    echo "-----------------------------------------"
    
    # --- PROMPT AND PARSING ---
    echo "Commands: mount <drive>, unmount <drive>, exit"
    echo "-----------------------------------------"
    read -p "Command > " ACTION DRIVE_NAME

    # Handle empty input or exit
    if [ -z "$ACTION" ] || [ "$ACTION" = "exit" ]; then
        break
    fi

    # Ensure a drive name was provided for the command
    if [ -z "$DRIVE_NAME" ]; then
        echo "Error: You must specify a drive name. Example: mount MyDrive"
        sleep 2
        continue
    fi

    # Lookup the UUID from the configuration file
    DRIVE_UUID=$(grep "^DRIVE:$DRIVE_NAME:" "$CONF_FILE" | cut -d':' -f3)

    if [ -z "$DRIVE_UUID" ]; then
        echo "Error: Drive '$DRIVE_NAME' is not configured."
        sleep 2
        continue
    fi

    echo "-----------------------------------------"

    # --- EXECUTE COMMANDS ---
    case "$ACTION" in
        mount)
            # Loop indefinitely until the unlock is successful or the user aborts
            while true; do
                echo -n "Enter the encryption password for $DRIVE_NAME (or leave blank to abort): "
                read -s DRIVE_PASS
                echo ""
                
                # Allow user to break out of the password prompt
                if [ -z "$DRIVE_PASS" ]; then
                    echo "Aborting mount command."
                    break
                fi
                
                echo "Connecting to unlock $DRIVE_NAME..."
                
                # Execute the remote command
                run_ssh "
                    if diskutil apfs list | grep -q '$DRIVE_UUID'; then
                        echo '$DRIVE_PASS' | diskutil apfs unlockVolume $DRIVE_UUID -stdinpassphrase
                    else
                        echo '$DRIVE_PASS' | diskutil coreStorage unlockVolume $DRIVE_UUID -stdinpassphrase
                    fi
                "
                
                # Capture the exit status of the SSH command
                if [ $? -eq 0 ]; then
                    echo "Successfully unlocked $DRIVE_NAME!"
                    break
                else
                    echo -e "\nError: Incorrect password or failed to unlock. Please try again."
                fi
            done
            ;;
            
        unmount)
            echo "Connecting to unmount $DRIVE_NAME..."
            run_ssh "diskutil unmount $DRIVE_UUID"
            ;;
            
        *)
            echo "Error: Unknown command '$ACTION'."
            echo "Supported commands are: mount, unmount, exit"
            sleep 2
            continue
            ;;
    esac
    
    # Brief pause so you can see the result of the command before the screen clears
    echo "-----------------------------------------"
    echo "Command complete. Refreshing..."
    sleep 1.5
done
