#Gives us os.path tools for working with file paths
import os

# The agent asks to look in `directory`; we only allow it inside `working_directory` (the fence). 
# #directory = . means to search current directory if none provided
def get_files_info(working_directory: str, directory: str = ".") -> str:
    #Here, try is used as a safety net: if anything below crashes
    #jump to `except` and return a string instead
    try:
        # Turn the fence's short name ("calculator") into a full address starting from "/"
        absolute_working_dir = os.path.abspath(working_directory)
        # Glue the agent's request onto the fence, then tidy it ("." and ".." resolved)
        # so we see where it REALLY points (catches tricks like "../" and "/bin")
        target_dir = os.path.normpath(os.path.join(absolute_working_dir, directory))
        # Returns True if the target is inside the fence: the shared start of both paths
        # must be the whole fence path, otherwise the target has wandered out
        valid_target_dir = os.path.commonpath([absolute_working_dir, target_dir]) == absolute_working_dir
        # If target is outside the fence: refuse and tell the agent why
        if valid_target_dir == False:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        # If target is inside the fence but is not a folder 
        # (e.g. a file like main.py): can't list it and returns error
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        # Passed both checks: get the names of everything inside the folder
        # (just bare names like "main.py", not full paths)
        files = os.listdir(target_dir)
        # Empty list to collect one finished line of text per item
        file_info = []
        # Visit each item in the folder one at a time
        for file in files:
            # Glue the folder onto the bare name so we get the item's real address
            # (a bare name alone would make Python look in the wrong folder)
            full_path = os.path.join(target_dir, file)
            # Build one complete line for this item: name, size in bytes,
            # and whether it's a folder, then add it to the list
            file_info.append(f"- {file}: file_size={os.path.getsize(full_path)} bytes, is_dir={os.path.isdir(full_path)}")
        # Stick all the lines together with a newline between each one,
        # so every item shows up on its own row, and hand it back to the agent
        return "\n".join(file_info)

    # Something unexpected broke: turn the error into text the agent can read
    except Exception as e:
        return f"Error: {e}"
schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}