import argparse
import requests
import socket

def http_get(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"HTTP Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"HTTP Request Error: {str(e)}"

def download_file(url, destination):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination, 'wb') as file:
                file.write(response.content)
            return f"File downloaded to {destination}"
        else:
            return f"HTTP Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"HTTP Request Error: {str(e)}"

def get_ip_address(host):
    try:
        ip_address = socket.gethostbyname(host)
        return f"IP Address for {host}: {ip_address}"
    except socket.gaierror as e:
        return f"Error resolving {host}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Networking Operations")
    parser.add_argument("--http-get", help="Make an HTTP GET request to a URL")
    parser.add_argument("--resolve-host", help="Resolve a hostname to its IP address")
    parser.add_argument("--download-file", nargs=2, metavar=("url", "destination"), help="Download a file from a URL")

    args = parser.parse_args()

    if args.http_get:
        result = http_get(args.http_get)
        print(result)

    if args.resolve_host:
        result = get_ip_address(args.resolve_host)
        print(result)

    if args.download_file:
        url, destination = args.download_file
        result = download_file(url, destination)
        print(result)

if __name__ == "__main__":
    main()

