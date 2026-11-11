import os 

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        # Turn the fence's short name ("calculator") into a full address starting from "/"
        absolute_working_dir = os.path.abspath(working_directory)
        # Glue the agent's request onto the fence, then tidy it ("." and ".." resolved)
        # so we see where it REALLY points (catches tricks like "../" and "/bin/cat")
        target_file = os.path.normpath(os.path.join(absolute_working_dir, file_path))
        # True if the file is inside the fence: the shared start of both paths
        # must be the whole fence path, otherwise the file is outside it
        valid_target_file = os.path.commonpath([absolute_working_dir, target_file]) == absolute_working_dir
        # If the file is outside the fence: refuse and tell the agent why
        if valid_target_file == False:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        # If the path points at a folder, refuse: you can only write text into a file
        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        # Make sure every folder above the file exists, creating any that are missing
        # (exist_ok=True means "don't complain if they're already there")
        os.makedirs(os.path.dirname(target_file),exist_ok=True)
        # Open the file for writing ("w" creates it if it's new, and ERASES it if it exists),
        # and close it automatically when the block ends
        with open(target_file, "w") as f:
            # Put the agent's text into the file
            f.write(content)
        # Report success, including how many characters were written
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    # Something unexpected broke: turn the error into text the agent can read
    except Exception as e:
        return f"Error: {e}"
schema_write_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Opens the file for writing inside working directory, creates it and new folders if it's new, and replaces it if it exists",
        "parameters": {
            "type": "object",
            "required": ["file_path","content"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write, relative to the working directory",
                },
                "content":{
                    "type": "string",
                    "description": "The full text to write to the file; replaces any existing contents"
                }
            },
        },
    }
}