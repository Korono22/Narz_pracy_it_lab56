import argparse
import os
import sys
import json  # Dodajemy wbudowaną bibliotekę do JSON

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

# --- NOWA FUNKCJA DLA TASK 2 ---
def load_json(file_path):
    """Wczytuje plik JSON i weryfikuje poprawność jego składni."""
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

def main():
    input_path, output_path = parse_arguments()
    input_ext, output_ext = validate_extensions(input_path, output_path)
    
    # Słownik, w którym będziemy przechowywać sparsowane dane
    parsed_data = None
    
    # Jeśli plik wejściowy to JSON, wczytujemy go
    if input_ext == '.json':
        parsed_data = load_json(input_path)
        print(f"Wczytane dane: {parsed_data}")
    else:
        print(f"Format wejściowy {input_ext} zostanie obsłużony w kolejnych krokach.")

if __name__ == "__main__":
    main()