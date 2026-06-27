import argparse
import os
import sys

def parse_arguments():
    # Tworzymy parser i definiujemy dwa wymagane argumenty
    parser = argparse.ArgumentParser(
        description="Program do konwersji danych między formatami XML, JSON i YAML."
    )
    parser.add_argument("input_file", help="Ścieżka do pliku wejściowego")
    parser.add_argument("output_file", help="Ścieżka do pliku wyjściowego")
    
    # Jeśli użytkownik nie poda argumentów, argparse sam wypisze pomoc i zakończy program
    args = parser.parse_args()
    return args.input_file, args.output_file

def validate_extensions(input_path, output_path):
    # Dozwolone rozszerzenia plików
    allowed_extensions = {'.json', '.xml', '.yml', '.yaml'}
    
    # Wyciągamy rozszerzenia i zamieniamy na małe litery
    _, input_ext = os.path.splitext(input_path.lower())
    _, output_ext = os.path.splitext(output_path.lower())
    
    # Sprawdzamy poprawność rozszerzeń
    if input_ext not in allowed_extensions:
        print(f"Błąd: Nieobsługiwany format pliku wejściowego '{input_ext}'.")
        print("Dozwolone formaty: .json, .xml, .yml, .yaml")
        sys.exit(1)
        
    if output_ext not in allowed_extensions:
        print(f"Błąd: Nieobsługiwany format pliku wyjściowego '{output_ext}'.")
        print("Dozwolone formaty: .json, .xml, .yml, .yaml")
        sys.exit(1)
        
    return input_ext, output_ext

def main():
    # Pobieramy argumenty
    input_path, output_path = parse_arguments()
    
    # Walidujemy rozszerzenia
    input_ext, output_ext = validate_extensions(input_path, output_path)
    
    print(f"Pomyślnie rozpoznano pliki:")
    print(f" - Wejście: {input_path} (Format: {input_ext})")
    print(f" - Wyjście: {output_path} (Format: {output_ext})")

if __name__ == "__main__":
    main()