import subprocess

def get_system_version():
    try:
        # Run the uname command to get system information
        result = subprocess.run(["uname", "-r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if the command executed successfully
        if result.returncode == 0:
            system_version = result.stdout.strip()
            return system_version
        else:
            return f"Error: {result.stderr.strip()}"

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    system_version = get_system_version()
    print(f"System Version: {system_version}")

