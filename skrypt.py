import argparse
import os
import sys
import json
import yaml
import xml.etree.ElementTree as ET

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

def load_yaml(file_path):
    if not os.path.exists(file_path):
        print(f"Błąd: Plik wejściowy '{file_path}' nie istnieje.")
        sys.exit(1)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            print("Składnia pliku YAML jest poprawna.")
            return data
    except yaml.YAMLError as e:
        print(f"Błąd składni w pliku YAML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd podczas odczytu pliku: {e}")
        sys.exit(1)

def xml_to_dict(element):
    result = {}
    if element.attrib:
        result["@attributes"] = element.attrib
    if element.text and element.text.strip():
        if len(element) == 0:
            return element.text.strip()
        else:
            result["#text"] = element.text.strip()
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data
    return result

def load_xml(file_path):
    if not os.path.exists(file_path):
        print(f"Błąd: Plik wejściowy '{file_path}' nie istnieje.")
        sys.exit(1)
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        print("Składnia pliku XML jest poprawna.")
        return {root.tag: xml_to_dict(root)}
    except ET.ParseError as e:
        print(f"Błąd składni w pliku XML: {e}")
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

def save_yaml(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            print(f"Pomyślnie zapisano dane do pliku YAML: {file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu do pliku YAML: {e}")
        sys.exit(1)

# --- NOWE FUNKCJE POMOCNICZE DLA TASK 7 ---
def dict_to_xml(tag, d):
    """Konwertuje słownik z powrotem na elementy struktury XML ElementTree."""
    elem = ET.Element(tag)
    if isinstance(d, dict):
        for key, value in d.items():
            if key == '@attributes' and isinstance(value, dict):
                elem.attrib.update(value)
            elif key == '#text':
                elem.text = str(value)
            elif isinstance(value, list):
                for item in value:
                    elem.append(dict_to_xml(key, item))
            else:
                elem.append(dict_to_xml(key, value))
    else:
        elem.text = str(d)
    return elem

def save_xml(data, file_path):
    """Zapisuje dane z obiektu do pliku XML zgodnie ze składnią."""
    try:
        # Nasz parser load_xml zawsze owija dane w słownik, gdzie jedynym kluczem głównym jest root tag.
        # Pobieramy ten tag i jego zawartość. Jeśli dane pochodzą z JSON/YAML, bierzemy pierwszy klucz słownika jako root.
        root_tag = list(data.keys())[0]
        root_data = data[root_tag]
        
        root_element = dict_to_xml(root_tag, root_data)
        
        # Tworzymy drzewo i dodajemy ładne wcięcia (dostępne od Pythona 3.9+)
        tree = ET.ElementTree(root_element)
        ET.indent(tree, space="    ", level=0)
        
        with open(file_path, 'wb') as file:
            tree.write(file, encoding='utf-8', xml_declaration=True)
            
        print(f"Pomyślnie zapisano dane do pliku XML: {file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu do pliku XML: {e}")
        sys.exit(1)

def main():
    input_path, output_path = parse_arguments()
    input_ext, output_ext = validate_extensions(input_path, output_path)
    
    parsed_data = None
    
    # 1. Odczyt danych
    if input_ext == '.json':
        parsed_data = load_json(input_path)
    elif input_ext in {'.yml', '.yaml'}:
        parsed_data = load_yaml(input_path)
    elif input_ext == '.xml':
        parsed_data = load_xml(input_path)
    else:
        print(f"Format wejściowy {input_ext} nie jest obsługiwany.")
        sys.exit(1)

    # 2. Zapis danych (Teraz w pełni obsługujemy wszystkie 3 formaty!)
    if output_ext == '.json':
        save_json(parsed_data, output_path)
    elif output_ext in {'.yml', '.yaml'}:
        save_yaml(parsed_data, output_path)
    elif output_ext == '.xml':
        save_xml(parsed_data, output_path)

if __name__ == "__main__":
    main()