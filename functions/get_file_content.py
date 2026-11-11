# Gives us os.path tools for working with file paths
import os
# The agent asks to read `file_path`; we only allow it inside `working_directory` (the fence).
def get_file_content(working_directory: str, file_path: str) -> str:
    # Safety net: if anything below crashes, jump to `except`
    # and return a string instead of breaking the agent
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
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        # If it's inside the fence but doesn't exist, or is a folder rather than
        # a regular file (e.g. "pkg"): there's nothing to read, so return an error
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        # Cap how much we read so a huge file can't flood the agent
        # (and burn through our token limit)
        MAX_CHARS = 10_000
        # Open the checked, fenced path (never the raw `file_path`) for reading;
        # `with` closes the file automatically when the block ends
        with open(target_file, "r") as f:
            # Read only up to the limit (or the whole file, if it's smaller)
            file_content_string = f.read(MAX_CHARS)
            # Peek at one more character: if we get anything back, the file
            # was longer than the limit, so tell the agent it was cut off.
            # (This has to happen inside `with`, while the file is still open)
            if f.read(1):
                file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        # Hand the contents (plus the truncation note, if any) back to the agent
        return file_content_string
    # Something unexpected broke: turn the error into text the agent can read
    except Exception as e:
        return f"Error: {e}"
schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": "Reads a file's content, only reads inside the working directory and truncates long files",
        "parameters": {
            "type": "object",
            "required": ["file_path"],
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory",
                },
            },
        },
    },
}