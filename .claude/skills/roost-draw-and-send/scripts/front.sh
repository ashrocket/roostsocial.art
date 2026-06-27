#!/bin/zsh
# Bring the Roost (Rookery) app to the front so mouse events land on its canvas,
# NOT on the cmux / terminal window that hosts this Claude Code session (that
# window raises itself over Roost while the session is active). Run this at the
# start of EVERY action batch -- clicks and strokes are useless otherwise.
osascript -e 'tell application id "com.rookery.courier" to activate' 2>/dev/null \
  || open -b com.rookery.courier
sleep 0.7
