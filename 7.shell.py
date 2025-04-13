# 7.shell.py
import sys
import os
import subprocess
import shlex

def execute_single_command(args, stdin_target=None, stdout_target=None, cwd=None):
    """Executes a single command, handling stdin/stdout redirection."""
    stderr_target = subprocess.PIPE
    try:
        result = subprocess.run(args,
                                stdin=stdin_target,
                                stdout=stdout_target,
                                stderr=stderr_target,
                                text=True,
                                check=False,
                                cwd=cwd)
        # Print stderr if captured
        if result.stderr:
            print(result.stderr, file=sys.stderr, end='')
        # Return stdout if captured
        if stdout_target == subprocess.PIPE and result.stdout:
            return result.stdout
        return "" # Return empty if redirected or no output
    except FileNotFoundError:
        print(f"shell: {args[0]}: command not found", file=sys.stderr)
    except PermissionError:
         print(f"shell: {args[0]}: Permission denied", file=sys.stderr)
    except Exception as e:
        print(f"shell: Error executing command '{args[0]}': {e}", file=sys.stderr)
    return None # Indicate error

def main():
    while True:
        try:
            cwd = os.getcwd()
            prompt = f"{cwd}$ "
            command_line = input(prompt)
            command_line = command_line.strip()

            if not command_line: continue
            if command_line == "exit": break

            # --- Handle built-in 'cd' first ---
            # Using shlex now for consistency even before checking builtins
            try:
                 initial_args = shlex.split(command_line)
            except ValueError as e:
                 print(f"shell: Error parsing command near quotes: {e}", file=sys.stderr)
                 continue

            if not initial_args: continue

            if initial_args[0] == "cd":
                if len(initial_args) > 1:
                    target_dir = initial_args[1]
                    try: os.chdir(target_dir)
                    except FileNotFoundError: print(f"shell: cd: {target_dir}: No such file or directory", file=sys.stderr)
                    except NotADirectoryError: print(f"shell: cd: {target_dir}: Not a directory", file=sys.stderr)
                    except Exception as e: print(f"shell: cd: Error changing directory: {e}", file=sys.stderr)
                else:
                    try: os.chdir(os.path.expanduser("~"))
                    except Exception as e: print(f"shell: cd: Error changing to home directory: {e}", file=sys.stderr)
                continue # Skip rest for cd

            # --- Parse for Pipes ---
            pipe_commands = [cmd.strip() for cmd in command_line.split('|')]

            # --- Process Pipeline ---
            previous_process = None
            input_stream = None # Initially stdin comes from shell (keyboard or < file)
            output_stream = None # Initially stdout goes to shell (console or > file)

            input_fileobj = None
            output_fileobj = None

            last_command_index = len(pipe_commands) - 1

            for i, command_segment in enumerate(pipe_commands):

                command_part = command_segment
                current_input_file = None
                current_output_file = None

                # --- Parse Redirection for *this segment* ---
                # Input redirection only makes sense for the *first* command
                if i == 0 and '<' in command_part:
                     parts = command_part.split('<', 1)
                     command_part = parts[0].strip()
                     current_input_file = parts[1].strip()
                     # Open the input file
                     try:
                         input_fileobj = open(current_input_file, 'r', encoding='utf-8')
                         input_stream = input_fileobj # Use this file as stdin for the first process
                     except FileNotFoundError:
                          print(f"shell: Error opening input file '{current_input_file}': No such file or directory", file=sys.stderr)
                          # Clean up any previously opened process? Difficult state. Break pipeline?
                          previous_process = None # Invalidate pipeline
                          break # Stop processing pipeline
                     except IOError as e:
                           print(f"shell: Error opening input file '{current_input_file}': {e}", file=sys.stderr)
                           previous_process = None
                           break

                # Output redirection only makes sense for the *last* command
                if i == last_command_index and '>' in command_part:
                     parts = command_part.split('>', 1)
                     command_part = parts[0].strip()
                     current_output_file = parts[1].strip()
                     # Open the output file
                     try:
                          output_fileobj = open(current_output_file, 'w', encoding='utf-8')
                          output_stream = output_fileobj # Use this file as stdout for the last process
                     except IOError as e:
                          print(f"shell: Error opening output file '{current_output_file}': {e}", file=sys.stderr)
                          previous_process = None
                          break # Stop processing pipeline

                # Parse the actual command arguments for this segment
                try:
                    args = shlex.split(command_part)
                except ValueError as e:
                    print(f"shell: Error parsing command segment '{command_part}': {e}", file=sys.stderr)
                    previous_process = None
                    break

                if not args: # Skip empty segments in pipeline
                    continue

                # Determine stdout for the current process
                current_stdout = None
                if i < last_command_index:
                    current_stdout = subprocess.PIPE # Pipe to next command
                elif output_stream: # Last command with output redirection
                    current_stdout = output_stream
                else: # Last command, output to console (capture it)
                    current_stdout = subprocess.PIPE

                # --- Execute command segment using Popen ---
                try:
                    process = subprocess.Popen(args,
                                               stdin=input_stream, # Use previous stdout or initial input file
                                               stdout=current_stdout,
                                               stderr=subprocess.PIPE, # Always capture stderr
                                               text=True,
                                               cwd=cwd)

                    # Important for pipelines: close the writing end of the pipe in the parent
                    # If the previous process piped its stdout to us, close that pipe now.
                    if previous_process and previous_process.stdout:
                        previous_process.stdout.close()

                    # The current process's stdout becomes the next process's stdin
                    input_stream = process.stdout
                    previous_process = process # Remember this process for the next iteration

                except FileNotFoundError:
                    print(f"shell: {args[0]}: command not found", file=sys.stderr)
                    previous_process = None # Break pipeline on error
                    break
                except PermissionError:
                     print(f"shell: {args[0]}: Permission denied", file=sys.stderr)
                     previous_process = None
                     break
                except Exception as e:
                    print(f"shell: Error starting command '{args[0]}': {e}", file=sys.stderr)
                    previous_process = None
                    break

            # --- After the loop, handle the last process's output ---
            if previous_process:
                try:
                    # Get final output and error from the *last* command in the pipeline
                    final_stdout, final_stderr = previous_process.communicate() # Waits for process to finish

                    if final_stderr:
                         print(final_stderr, file=sys.stderr, end='')
                    # Print final stdout only if it wasn't redirected to a file
                    if not output_stream and final_stdout:
                         print(final_stdout, end='')

                except Exception as e:
                    print(f"shell: Error communicating with last process: {e}", file=sys.stderr)

            # --- Cleanup file handles ---
            if output_fileobj:
                output_fileobj.close()
            if input_fileobj:
                input_fileobj.close()

        except EOFError:
            print("\nexit")
            break
        except KeyboardInterrupt:
            # TODO: Handle Ctrl+C during subprocess execution (more complex, involves sending signals)
            print()
            continue

if __name__ == "__main__":
    main()