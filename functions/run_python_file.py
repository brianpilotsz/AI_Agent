import os
import subprocess


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
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
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        # Refuse if the file doesn't exist, or if it's a folder rather than a file
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        # Only run Python files: the name must end in ".py"
        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        # Build the terminal command as a list, like typing: python /full/path/main.py
        command = ["python", target_file]
        # If the agent passed extra arguments (e.g. "3 + 5"), add them to the end of the command
        if args:
            command.extend(args)
        # Run the command and wait for it to finish:
        # cwd            = run it from inside the fence folder
        # capture_output = keep what it prints instead of showing it on screen
        # text=True      = give us that output as normal strings, not raw bytes
        # timeout=30     = stop it if it runs longer than 30 seconds
        # The result ("report card") holds the exit code, stdout and stderr
        file_object = subprocess.run(command,cwd=absolute_working_dir,capture_output=True,text=True,timeout=30)
        # Start an empty string and add each piece of the report to it
        output = ""
        # An exit code other than 0 means the script failed: say which code it gave
        if file_object.returncode != 0:
            output += f"Process exited with code {file_object.returncode}"
        # If the script printed nothing at all (normal or error output), say so
        if file_object.stderr == "" and file_object.stdout =="":
            output += f"\nNo output produced"
        # Otherwise include both: STDOUT is normal printed output, STDERR is error/warning output
        else:
            output += f"\nSTDOUT:{file_object.stdout}\nSTDERR:{file_object.stderr}"
        # Hand the whole report back to the agent as one string
        return output
    # Something unexpected broke (including the 30-second timeout): turn it into text the agent can read
    except Exception as e:
            return f"Error: executing Python file: {e}" 
schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "runs python file limited to working directory, times out at 30 seconds and returns output",
        "parameters": {
            "type": "object",
            "required": ["file_path"],
            "properties": {
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "optional arguments passed to the python script file (e.g. ['3+5'] )"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the python file to run, relative to the working directory",
                },
            },
        },
    },
}