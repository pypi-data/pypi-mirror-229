import argparse
import msgpack
import yaml

def load_translation(translations_path):
    try:
        with open(translations_path, 'rb') as f:
            return msgpack.load(f, raw=False)
    except FileNotFoundError:
        return None
    except Exception as e:
        return f"Error loading translation: {str(e)}"

def translate(key, translation):
    if key in translation:
        return translation[key]
    else:
        return f"Translation not found for key: {key}"

def main():
    parser = argparse.ArgumentParser(description="Localization Operations")
    parser.add_argument("--load-translation", help="Load a binary YAML translation file")

    args = parser.parse_args()

    if args.load_translation:
        translation = load_translation(args.load_translation)
        if translation:
            while True:
                key = input("Enter a translation key (or 'q' to quit): ")
                if key == 'q':
                    break
                result = translate(key, translation)
                print(result)
        else:
            print(f"Translation file '{args.load_translation}' not found or invalid.")

if __name__ == "__main__":
    main()

