import argparse
import platform

def get_os_version():
    return platform.system()

def get_os_release():
    return platform.release()

def get_os_architecture():
    return platform.architecture()

def main():
    parser = argparse.ArgumentParser(description="Retrieve system information")
    parser.add_argument("--version", action="store_true", help="Get the operating system version")
    parser.add_argument("--release", action="store_true", help="Get the operating system release")
    parser.add_argument("--architecture", action="store_true", help="Get the operating system architecture")

    args = parser.parse_args()

    if args.version:
        print("Operating System Version:", get_os_version())

    if args.release:
        print("Operating System Release:", get_os_release())

    if args.architecture:
        print("Operating System Architecture:", get_os_architecture())

if __name__ == "__main__":
    main()

