import argparse
import os
import sys
import json
import yaml  # Dodajemy bibliotekę do obsługi YAML (z pakietu pyyaml)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Program do konwersji danych między formatami XML, JSON i YAML."
    )
    parser.add_argument("input_file", help="Ścieżka do pliku wejściowego")
    parser.add_argument("output_file", help="Ścieżka do pliku wyjściowego")
    args = parser.parse_args()
    return args.input_file, args.output_file

def validate_extensions(input_path, output_path):
    allowed_extensions = {'.json', '.xml', '.yml', '.yaml'}
    _, input_ext = os.path.splitext(input_path.lower())
    _, output_ext = os.path.splitext(output_path.lower())
    
    if input_ext not in allowed_extensions or output_ext not in allowed_extensions:
        print("Błąd: Nieobsługiwany format pliku.")
        sys.exit(1)
        
    return input_ext, output_ext

def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"Błąd: Plik wejściowy '{file_path}' nie istnieje.")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print("Składnia pliku JSON jest poprawna.")
            return data
    except json.JSONDecodeError as e:
        print(f"Błąd składni w pliku JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd podczas odczytu pliku: {e}")
        sys.exit(1)

# --- NOWA FUNKCJA DLA TASK 4 ---
def load_yaml(file_path):
    """Wczytuje plik YAML i weryfikuje poprawność jego składni."""
    if not os.path.exists(file_path):
        print(f"Błąd: Plik wejściowy '{file_path}' nie istnieje.")
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # SafeLoader zabezpiecza przed uruchomieniem niepożądanego kodu zaszytego w YAML
            data = yaml.load(file, Loader=yaml.SafeLoader)
            print("Składnia pliku YAML jest poprawna.")
            return data
    except yaml.YAMLError as e:
        print(f"Błąd składni w pliku YAML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd podczas odczytu pliku: {e}")
        sys.exit(1)

def save_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Pomyślnie zapisano dane do pliku JSON: {file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu do pliku JSON: {e}")
        sys.exit(1)

def main():
    input_path, output_path = parse_arguments()
    input_ext, output_ext = validate_extensions(input_path, output_path)
    
    parsed_data = None
    
    # 1. Odczyt danych (obsługujemy JSON oraz YAML)
    if input_ext == '.json':
        parsed_data = load_json(input_path)
    elif input_ext in {'.yml', '.yaml'}:
        parsed_data = load_yaml(input_path)
    else:
        print(f"Format wejściowy {input_ext} nie jest jeszcze obsługiwany jako źródło.")
        sys.exit(1)

    # 2. Zapis danych
    if output_ext == '.json':
        save_json(parsed_data, output_path)
    else:
        print(f"Format wyjściowy {output_ext} zostanie obsłużony w kolejnych krokach.")

if __name__ == "__main__":
    main()