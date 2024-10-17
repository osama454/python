import os
import zipfile

def archive_selection(selection):
    """
    Creates a zip archive of the selected items with maximum compression.
    """

    # Prompt for output file path
    output_path = ask_user_for_path("Save Zip Archive", "archive.zip")
    if not output_path:
        return  # User canceled

    # Create the zip archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for item in selection:
            if item.is_file:
                zip_file.write(item.path, os.path.basename(item.path))
            elif item.is_folder:
                for root, _, files in os.walk(item.path):
                    for file in files:
                        zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), item.path))

# Get the selected items
selection = get_selected_items()

# Execute the action
archive_selection(selection)