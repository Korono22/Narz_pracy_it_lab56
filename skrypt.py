import argparse
import os
import sys
import json
import yaml
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import QThread, QObject, pyqtSignal  # Dodajemy obsługę wątków i sygnałów

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Program do konwersji danych między formatami XML, JSON i YAML."
    )
    parser.add_argument("input_file", nargs="?", default=None, help="Ścieżka do pliku wejściowego")
    parser.add_argument("output_file", nargs="?", default=None, help="Ścieżka do pliku wyjściowego")
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
    success, res = validate_extensions(input_path, output_path)
    if not success:
        return False, res
    input_ext, output_ext = res
    try:
        if input_ext == '.json':
            parsed_data = load_json(input_path)
        elif input_ext in {'.yml', '.yaml'}:
            parsed_data = load_yaml(input_path)
        elif input_ext == '.xml':
            parsed_data = load_xml(input_path)
            
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

# --- NOWA KLASA WORKERA DLA ASYNCHRONICZNOŚCI (TASK 9) ---
class ConversionWorker(QObject):
    finished = pyqtSignal(bool, str)  # Sygnał zwracający stan (sukces, komunikat)

    def __init__(self, input_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        """Metoda uruchamiana w osobnym wątku."""
        success, message = convert_files(self.input_path, self.output_path)
        self.finished.emit(success, message)

class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file_path = ""
        self.output_file_path = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Konwerter XML / JSON / YAML (Async)")
        self.resize(500, 200)
        
        layout = QVBoxLayout()
        
        input_layout = QHBoxLayout()
        self.lbl_input = QLabel("Nie wybrano pliku wejściowego")
        btn_select_input = QPushButton("Wybierz plik wejściowy")
        btn_select_input.clicked.connect(self.select_input_file)
        input_layout.addWidget(btn_select_input)
        input_layout.addWidget(self.lbl_input)
        layout.addLayout(input_layout)
        
        output_layout = QHBoxLayout()
        self.lbl_output = QLabel("Nie wybrano pliku docelowego")
        btn_select_output = QPushButton("Ustaw plik wyjściowy")
        btn_select_output.clicked.connect(self.select_output_file)
        output_layout.addWidget(btn_select_output)
        output_layout.addWidget(self.lbl_output)
        layout.addLayout(output_layout)
        
        self.btn_convert = QPushButton("Konwertuj dane")
        self.btn_convert.clicked.connect(self.execute_conversion_async)
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
            self, "Ustaw miejsce zapisu", "", "JSON (*.json);;XML (*.xml);;YAML (*.yml *.yaml)"
        )
        if file_path:
            self.output_file_path = file_path
            self.lbl_output.setText(os.path.basename(file_path))
            
    # Zmodyfikowana funkcja uruchamiająca wątek w tle
    def execute_conversion_async(self):
        if not self.input_file_path or not self.output_file_path:
            QMessageBox.warning(self, "Brak danych", "Musisz wybrać oba pliki!")
            return
            
        self.btn_convert.setEnabled(False)  # Blokujemy przycisk na czas operacji
        
        # Tworzenie nowego wątku i workera
        self.thread = QThread()
        self.worker = ConversionWorker(self.input_file_path, self.output_file_path)
        self.worker.moveToThread(self.thread)
        
        # Łączenie zdarzeń
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Odbiór wyniku konwersji
        self.worker.finished.connect(self.on_conversion_finished)
        
        self.thread.start()
        
    def on_conversion_finished(self, success, message):
        self.btn_convert.setEnabled(True)  # Przywracamy przycisk
        if success:
            QMessageBox.information(self, "Sukces", message)
        else:
            QMessageBox.critical(self, "Błąd", message)

def main():
    input_path, output_path = parse_arguments()
    if input_path is None and output_path is None:
        app = QApplication(sys.argv)
        window = ConverterApp()
        window.show()
        sys.exit(app.exec())
    else:
        if not input_path or not output_path:
            print("Błąd: Musisz podać dwie ścieżki plików w trybie konsolowym.")
            sys.exit(1)
        success, message = convert_files(input_path, output_path)
        print(message)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()