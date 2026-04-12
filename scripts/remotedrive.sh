#!/bin/bash

# --- CONFIGURATION ---
CONF_FILE="$(dirname "$0")/drives.conf" # Looks for drives.conf in the same folder
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

# This executes if you pass "list" as the first argument to the script
if [ "$1" = "list" ]; then
    echo "Fetching mounted drives from $SSH_TARGET (filtered by drives.conf)..."
    
    # Extract all drive names from the config file and join them with the pipe (|) operator for regex matching
    DRIVE_LIST=$(grep "^DRIVE:" "$CONF_FILE" | cut -d':' -f2 | paste -sd '|' -)
    
    if [ -z "$DRIVE_LIST" ]; then
        echo "No drives are configured in $CONF_FILE."
        exit 0
    fi
    
    # Run the remote command and store the output in a variable
    MOUNTED_DRIVES=$(ssh "$SSH_TARGET" "df -h | grep '/Volumes/' | grep -E '$DRIVE_LIST'")
    
    # Check if the output is empty and print the appropriate message
    if [ -z "$MOUNTED_DRIVES" ]; then
        echo "0 drives matching configuration are currently mounted on the remote host."
    else
        echo "$MOUNTED_DRIVES"
    fi
    
    exit 0
fi

# 3. Validate that a drive name argument was provided
if [ -z "$1" ]; then
    echo "Error: No drive name provided."
    echo "Usage: $0 <DRIVE_NAME>"
    echo "Available drives:"
    grep "^DRIVE:" "$CONF_FILE" | cut -d':' -f2 | sed 's/^/  - /'
    exit 1
fi

DRIVE_NAME="$1"

# 4. Lookup the UUID from the configuration file
# This searches for lines starting with DRIVE:DRIVE_NAME:
DRIVE_UUID=$(grep "^DRIVE:$DRIVE_NAME:" "$CONF_FILE" | cut -d':' -f3)

if [ -z "$DRIVE_UUID" ]; then
    echo "Error: Drive '$DRIVE_NAME' is not configured in $CONF_FILE."
    echo "Available drives:"
    grep "^DRIVE:" "$CONF_FILE" | cut -d':' -f2 | sed 's/^/  - /'
    exit 1
fi

# High-speed scannability menu
echo "========================================="
echo " Remote Mac Drive Manager: $DRIVE_NAME"
echo " Target: $SSH_TARGET"
echo "========================================="
echo "1) Mount & Unlock Drive"
echo "2) Unmount & Lock Drive"
echo "3) Check Drive Status"
echo "========================================="
read -p "Select an option [1-3]: " CHOICE

case $CHOICE in
    1)
        echo -n "Enter the encryption password for $DRIVE_NAME: "
        # Read the password without echoing it to the terminal screen
        read -s DRIVE_PASS
        echo ""
        
        echo "Connecting to $SSH_TARGET to unlock $DRIVE_NAME..."
        
        # Pass the password over standard input to 'diskutil' on the remote Mac
        ssh "$SSH_TARGET" "
            # Try APFS unlocking first
            if diskutil apfs list | grep -q '$DRIVE_UUID'; then
                echo '$DRIVE_PASS' | diskutil apfs unlockVolume $DRIVE_UUID -stdinpassphrase
            # Fallback to older CoreStorage (HFS+ Encrypted) if APFS fails
            else
                echo '$DRIVE_PASS' | diskutil coreStorage unlockVolume $DRIVE_UUID -stdinpassphrase
            fi
        "
        ;;
        
    2)
        echo "Connecting to $SSH_TARGET to unmount $DRIVE_NAME..."
        ssh "$SSH_TARGET" "
            diskutil unmount $DRIVE_UUID
        "
        ;;
        
    3)
        echo "Fetching status for $DRIVE_NAME from $SSH_TARGET..."
        ssh "$SSH_TARGET" "
            diskutil info $DRIVE_UUID | grep -E 'Volume Name|Mounted|Locked'
        "
        ;;
        
    *)
        echo "Invalid selection. Exiting."
        exit 1
        ;;
esac
