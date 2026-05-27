#!/bin/bash
set -euo pipefail

LABEL="com.tmy.azised"
APP_DIR="$HOME/.azised"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SCRIPT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/azised.py"
SCRIPT_DEST="$APP_DIR/azised.py"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$LABEL.plist"
LOG_DIR="$APP_DIR/logs"

if [[ ! -f "$SCRIPT_SRC" ]]; then
    echo "Cannot find azised.py next to this installer: $SCRIPT_SRC" >&2
    exit 1
fi

mkdir -p "$APP_DIR" "$APP_DIR/cache" "$LOG_DIR" "$LAUNCH_AGENTS_DIR"
cp "$SCRIPT_SRC" "$SCRIPT_DEST"
chmod 0644 "$SCRIPT_DEST"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DEST</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/azised.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_DIR/azised.err.log</string>
</dict>
</plist>
EOF

chmod 0644 "$PLIST_PATH"

if launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
    launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || true
fi

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$LABEL"

echo "Installed $LABEL"
echo "Script:  $SCRIPT_DEST"
echo "Logs:    $LOG_DIR/azised.log"
echo "         $LOG_DIR/azised.err.log"
echo
echo "First run: macOS may ask for Automation permission for Python -> System Events."
echo "Allow it once; it will not ask again."
