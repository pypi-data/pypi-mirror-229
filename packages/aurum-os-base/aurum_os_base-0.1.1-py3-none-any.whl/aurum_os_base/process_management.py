import argparse
import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

def terminate_process(process_id):
    try:
        subprocess.run(["kill", "-9", str(process_id)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"Process {process_id} terminated."
    except Exception as e:
        return f"Error terminating process {process_id}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Process Management")
    parser.add_argument("--run", help="Run a command as a new process")
    parser.add_argument("--terminate", type=int, help="Terminate a process by its ID")

    args = parser.parse_args()

    if args.run:
        result = run_command(args.run)
        print(result)

    if args.terminate:
        result = terminate_process(args.terminate)
        print(result)

if __name__ == "__main__":
    main()

