#!/bin/bash

# Get the currently selected items in AnchorPoint
selected_items=$(osascript -e 'tell application "AnchorPoint" to get selection as list')

# Check if there are any selected items
if [[ -z "$selected_items" ]]; then
  osascript -e 'tell application "AnchorPoint" to display alert "No items selected." message "Please select the project files or folders you want to archive."'
  exit 1
fi

# Prompt the user for the archive name and location
save_path=$(osascript -e 'tell application "AnchorPoint" to choose file name default name "Project Archive.zip"')
if [[ -z "$save_path" ]]; then
  exit 1
fi

# Create the zip archive with maximum compression
zip -9 -r "$save_path" $selected_items

# Display a notification that the archive has been created
osascript -e 'display notification "Project archived successfully." with title "AnchorPoint"'