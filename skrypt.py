import argparse
import os
import sys
import json
import yaml
import xml.etree.ElementTree as ET

# Importujemy komponenty PyQt6 do zbudowania okna
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Program do konwersji danych między formatami XML, JSON i YAML."
    )
    parser.add_argument("input_file", nargs="?", default=None, help="Ścieżka do pliku wejściowego (opcjonalna przy GUI)")
    parser.add_argument("output_file", nargs="?", default=None, help="Ścieżka do pliku wyjściowego (opcjonalna przy GUI)")
    args = parser.parse_args()
    return args.input_file, args.output_file

def validate_extensions(input_path, output_path):
    allowed_extensions = {'.json', '.xml', '.yml', '.yaml'}
    _, input_ext = os.path.splitext(input_path.lower())
    _, output_ext = os.path.splitext(output_path.lower())
    
    if input_ext not in allowed_extensions or output_ext not in allowed_extensions:
        return False, f"Nieobsługiwany format pliku. Dozwolone: .json, .xml, .yml, .yaml"
        
    return True, (input_ext, output_ext)

def load_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Plik wejściowy '{file_path}' nie istnieje.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_yaml(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Plik wejściowy '{file_path}' nie istnieje.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.load(file, Loader=yaml.SafeLoader)

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
        raise FileNotFoundError(f"Plik wejściowy '{file_path}' nie istnieje.")
    tree = ET.parse(file_path)
    root = tree.getroot()
    return {root.tag: xml_to_dict(root)}

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def save_yaml(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

def dict_to_xml(tag, d):
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
    root_tag = list(data.keys())[0]
    root_data = data[root_tag]
    root_element = dict_to_xml(root_tag, root_data)
    tree = ET.ElementTree(root_element)
    ET.indent(tree, space="    ", level=0)
    with open(file_path, 'wb') as file:
        tree.write(file, encoding='utf-8', xml_declaration=True)

def convert_files(input_path, output_path):
    """Główny silnik konwersji wywoływany zarówno przez konsolę, jak i GUI."""
    success, res = validate_extensions(input_path, output_path)
    if not success:
        return False, res
        
    input_ext, output_ext = res
    
    try:
        # Odczyt
        if input_ext == '.json':
            parsed_data = load_json(input_path)
        elif input_ext in {'.yml', '.yaml'}:
            parsed_data = load_yaml(input_path)
        elif input_ext == '.xml':
            parsed_data = load_xml(input_path)
            
        # Zapis
        if output_ext == '.json':
            save_json(parsed_data, output_path)
        elif output_ext in {'.yml', '.yaml'}:
            save_yaml(parsed_data, output_path)
        elif output_ext == '.xml':
            save_xml(parsed_data, output_path)
            
        return True, "Konwersja zakończona sukcesem!"
    except json.JSONDecodeError as e:
        return False, f"Błąd składni JSON: {e}"
    except yaml.YAMLError as e:
        return False, f"Błąd składni YAML: {e}"
    except ET.ParseError as e:
        return False, f"Błąd składni XML: {e}"
    except Exception as e:
        return False, f"Błąd: {e}"

# --- KLASA INTERFEJSU GRAFICZNEGO ---
class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file_path = ""
        self.output_file_path = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Konwerter XML / JSON / YAML")
        self.resize(500, 200)
        
        layout = QVBoxLayout()
        
        # Sekcja pliku wejściowego
        input_layout = QHBoxLayout()
        self.lbl_input = QLabel("Nie wybrano pliku wejściowego")
        btn_select_input = QPushButton("Wybierz plik wejściowy")
        btn_select_input.clicked.connect(self.select_input_file)
        input_layout.addWidget(btn_select_input)
        input_layout.addWidget(self.lbl_input)
        layout.addLayout(input_layout)
        
        # Sekcja pliku wyjściowego
        output_layout = QHBoxLayout()
        self.lbl_output = QLabel("Nie wybrano pliku docelowego")
        btn_select_output = QPushButton("Ustaw plik wyjściowy")
        btn_select_output.clicked.connect(self.select_output_file)
        output_layout.addWidget(btn_select_output)
        output_layout.addWidget(self.lbl_output)
        layout.addLayout(output_layout)
        
        # Przycisk konwersji
        self.btn_convert = QPushButton("Konwertuj dane")
        self.btn_convert.clicked.connect(self.execute_conversion)
        layout.addWidget(self.btn_convert)
        
        self.setLayout(layout)
        
    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik wejściowy", "", "Wszystkie obsługiwane (*.json *.xml *.yml *.yaml);;JSON (*.json);;XML (*.xml);;YAML (*.yml *.yaml)"
        )
        if file_path:
            self.input_file_path = file_path
            self.lbl_input.setText(os.path.basename(file_path))
            
    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Ustaw miejsce zapisu pliku docelowego", "", "JSON (*.json);;XML (*.xml);;YAML (*.yml *.yaml)"
        )
        if file_path:
            self.output_file_path = file_path
            self.lbl_output.setText(os.path.basename(file_path))
            
    def execute_conversion(self):
        if not self.input_file_path or not self.output_file_path:
            QMessageBox.warning(self, "Brak danych", "Musisz wybrać plik wejściowy oraz docelowy!")
            return
            
        success, message = convert_files(self.input_file_path, self.output_file_path)
        if success:
            QMessageBox.information(self, "Sukces", message)
        else:
            QMessageBox.critical(self, "Błąd", message)

def main():
    input_path, output_path = parse_arguments()
    
    # Tryb GUI - jeśli nie podano parametrów startowych w konsoli
    if input_path is None and output_path is None:
        app = QApplication(sys.argv)
        window = ConverterApp()
        window.show()
        sys.exit(app.exec())
    # Tryb konsolowy - jeśli podano ścieżki jako argumenty
    else:
        if not input_path or not output_path:
            print("Błąd: Musisz podać dwie ścieżki plików w trybie konsolowym.")
            sys.exit(1)
        success, message = convert_files(input_path, output_path)
        print(message)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()