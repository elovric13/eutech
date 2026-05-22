#!/bin/bash

USERS_FILE="/root/users.txt"
LOGFILE="/var/log/bash_script.log"
BACKUP_SOURCE="/home"
BACKUP_DEST="/backup"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOGFILE"
}

log "Script started"

# Add users

log "Starting user creation."

while read username
do
    if id "$username" &>/dev/null; then
        log "User $username already exists"
    else
        sudo useradd -m $username
        echo "$username:ChangePassword123" | sudo chpasswd
        log "User $username created"
    fi
done < $USERS_FILE

log "User creation finished."

# Create compressed backup of a directory

log "Starting backup"

mkdir -p "$BACKUP_DEST"
BACKUP_FILE="$BACKUP_DEST/backup_$DATE.tar.gz"
tar -czf "$BACKUP_FILE" "$BACKUP_SOURCE"

if [ $? -eq 0 ]; then
    log "Backup created successfully: $BACKUP_FILE"
else
    log "ERROR: Backup failed."
fi

log "Backup finished"