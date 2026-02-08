# iOS Shortcuts Automation for Journal OCR

## Method 1: iCloud Photos + Shortcuts + SSH

This method uses iOS Shortcuts to automatically upload photos to your computer via SSH.

### Setup Steps:

1. **On your computer:**
   - Enable SSH (macOS: System Settings → General → Sharing → Remote Login)
   - Note your computer's IP address and username

2. **On your iPhone:**
   - Open the Shortcuts app
   - Create a new Automation (not a shortcut)
   - Trigger: "When I take a photo" or "When photos are added to album"
   - Add actions:
     ```
     If [Photo] is [Screenshot] → Do Nothing
     Otherwise:
       → Get Latest Photos (limit: 1)
       → Run Script Over SSH
         Host: your-computer-ip
         User: your-username
         Script: python3 /path/to/journal_ocr.py /tmp/journal_photo.jpg
       → Save to iCloud Drive/Journal Photos/
     ```

### Pros:
- Immediate processing when you take photos
- Native iOS automation
- No manual uploads

### Cons:
- Requires your computer to be on and accessible
- SSH setup can be tricky

---

## Method 2: Dedicated Journal Photos Album

Simpler approach - use a specific album:

1. **On your iPhone:**
   - Create an album called "Journal Entries"
   - After taking a journal photo, add it to this album

2. **On your computer:**
   - Set up iCloud Photos sync
   - Run the folder watcher pointing to that album's folder:
   ```bash
   python auto_ocr_watcher.py "~/Pictures/Journal Entries"
   ```

### Pros:
- Simple and reliable
- No SSH required
- Works offline (syncs when connected)

### Cons:
- Small delay (iCloud sync time)
- Requires manual album assignment

---

## Method 3: AirDrop + Folder Watcher

For maximum privacy (no cloud):

1. **On your iPhone:**
   - Take journal photo
   - AirDrop to your Mac/computer
   - Photos land in Downloads

2. **On your computer:**
   ```bash
   python auto_ocr_watcher.py ~/Downloads
   ```

### Pros:
- No cloud storage
- Fast transfer
- Maximum privacy

### Cons:
- Requires being near your computer
- Manual AirDrop each time

---

## Method 4: Dedicated iOS App (Advanced)

You could build a simple iOS app using:
- SwiftUI for the camera interface
- Vision framework for on-device OCR
- CloudKit or your own API for sync

This is overkill for a personal project but gives you complete control.

---

## Recommended Setup

**For ease + automation:** Method 2 (Album + Folder Watcher)

**Setup instructions:**
1. Create "Journal Entries" album on iPhone
2. Enable iCloud Photos on computer
3. Install watcher dependencies:
   ```bash
   pip install watchdog
   ```
4. Start the watcher:
   ```bash
   python auto_ocr_watcher.py "~/Pictures/Journal Entries"
   ```
5. Leave it running (or set it as a startup service)

Now whenever you:
1. Take a photo of your journal
2. Add it to "Journal Entries" album
3. Wait for iCloud sync (~30 seconds)
4. OCR processes automatically ✨

---

## Making the Watcher Run on Startup (macOS)

Create a Launch Agent to run the watcher automatically:

1. Create file: `~/Library/LaunchAgents/com.journal.ocr.watcher.plist`
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.journal.ocr.watcher</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/path/to/auto_ocr_watcher.py</string>
           <string>/Users/yourname/Pictures/Journal Entries</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/tmp/journal-ocr-watcher.log</string>
       <key>StandardErrorPath</key>
       <string>/tmp/journal-ocr-watcher-error.log</string>
   </dict>
   </plist>
   ```

2. Load it:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.journal.ocr.watcher.plist
   ```

Now the watcher starts automatically when you log in!

---

## Making the Watcher Run on Startup (Linux)

Create a systemd service:

1. Create file: `/etc/systemd/system/journal-ocr-watcher.service`
   ```ini
   [Unit]
   Description=Journal OCR Watcher
   After=network.target

   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/home/yourusername
   ExecStart=/usr/bin/python3 /path/to/auto_ocr_watcher.py /path/to/watch/folder
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start:
   ```bash
   sudo systemctl enable journal-ocr-watcher
   sudo systemctl start journal-ocr-watcher
   ```

Check status: `sudo systemctl status journal-ocr-watcher`
