import argparse
import os

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"File '{filename}' not found."

def write_file(filename, content):
    try:
        with open(filename, 'w') as file:
            file.write(content)
            return f"File '{filename}' written successfully."
    except Exception as e:
        return f"Error writing to '{filename}': {str(e)}"

def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        return f"Directory '{directory}' created successfully."
    except Exception as e:
        return f"Error creating directory '{directory}': {str(e)}"

def check_existence(path):
    if os.path.exists(path):
        return f"'{path}' exists."
    else:
        return f"'{path}' does not exist."

def main():
    parser = argparse.ArgumentParser(description="File System Operations")
    parser.add_argument("--read", help="Read the contents of a file")
    parser.add_argument("--write", nargs=2, metavar=("filename", "content"), help="Write content to a file")
    parser.add_argument("--create-directory", help="Create a directory")
    parser.add_argument("--check-existence", help="Check if a file or directory exists")

    args = parser.parse_args()

    if args.read:
        result = read_file(args.read)
        print(result)

    if args.write:
        filename, content = args.write
        result = write_file(filename, content)
        print(result)

    if args.create_directory:
        result = create_directory(args.create_directory)
        print(result)

    if args.check_existence:
        result = check_existence(args.check_existence)
        print(result)

if __name__ == "__main__":
    main()

