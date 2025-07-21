#!/usr/bin/env python3

import sys
import re
import time
import subprocess
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QHBoxLayout, QStackedWidget,
    QGridLayout, QComboBox, QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QAbstractTableModel, Qt


class DataModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.parent = None

    def rowCount(self, index=None):
        return self._data.shape[0]

    def columnCount(self, index=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        if role == Qt.CheckStateRole and index.column() == self.columnCount() - 1:
            return Qt.Checked if self._data.iloc[index.row(), -1] else Qt.Unchecked
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == self.columnCount() - 1:
            is_favorite = value == Qt.Checked
            game_name = self._data.iloc[index.row()]["Name"]
            self._data.iloc[index.row(), -1] = is_favorite
            if self.parent:
                if is_favorite:
                    self.parent.favorites.add(game_name)
                else:
                    self.parent.favorites.discard(game_name)
                self.parent.save_favorites()
                self.parent.update_favorites_view(dynamic=False)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return False

    def flags(self, index):
        if index.column() == self.columnCount() - 1:
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Name", "Category", "Source", "Filename", "Favorite"][section]
            else:
                return section + 1
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Games Hub")
        self.setGeometry(200, 200, 1200, 800)

        self.favorites_file = "favorites.txt"
        self.favorites = self.load_favorites()

        from PyQt5.QtCore import QTimer
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setInterval(300)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.views = QStackedWidget()

        self.data = None
        self.roms = []
        self.create_main_menu()
        self.create_list_view()
        self.create_favorites_view()
        self.create_edit_view()

        self.main_layout.addWidget(self.views)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def create_main_menu(self):
        menu_widget = QWidget()
        menu_layout = QGridLayout()

        self.list_games_button = QPushButton("List All Games")
        self.list_games_button.clicked.connect(self.show_list_view)
        self.list_games_button.setFixedSize(150, 150)
        menu_layout.addWidget(self.list_games_button, 0, 0)

        self.favorites_button = QPushButton("Favorites")
        self.favorites_button.clicked.connect(self.show_favorites_view)
        self.favorites_button.setFixedSize(150, 150)
        menu_layout.addWidget(self.favorites_button, 0, 1)

        self.edit_menu_button = QPushButton("Add Game")
        self.edit_menu_button.clicked.connect(self.show_edit_view)
        self.edit_menu_button.setFixedSize(150, 150)
        menu_layout.addWidget(self.edit_menu_button, 0, 2)

        menu_widget.setLayout(menu_layout)
        self.views.addWidget(menu_widget)

    def create_edit_view(self):
        edit_widget = QWidget()
        edit_layout = QVBoxLayout()

        form_layout = QGridLayout()  # Use a grid layout for better alignment

        # Input areas for adding new entries with labels
        name_label = QLabel("Game Name:")
        self.new_game_name_input = QLineEdit()
        self.new_game_name_input.setPlaceholderText("Enter new game name...")
        self.new_game_name_input.setFixedHeight(40)
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.new_game_name_input, 0, 1)

        categories_label = QLabel("Categories:")
        self.new_game_categories_input = QLineEdit()
        self.new_game_categories_input.setPlaceholderText("Enter categories (comma-separated)...")
        self.new_game_categories_input.setFixedHeight(40)
        form_layout.addWidget(categories_label, 1, 0)
        form_layout.addWidget(self.new_game_categories_input, 1, 1)

        source_label = QLabel("Source:")
        self.new_game_source_input = QLineEdit()
        self.new_game_source_input.setPlaceholderText("Enter source...")
        self.new_game_source_input.setFixedHeight(40)
        form_layout.addWidget(source_label, 2, 0)
        form_layout.addWidget(self.new_game_source_input, 2, 1)

        filename_label = QLabel("File:")
        self.new_game_filename_button = QPushButton("Select File")
        self.new_game_filename_button.clicked.connect(self.select_new_game_file)
        self.new_game_filename_button.setFixedHeight(40)
        form_layout.addWidget(filename_label, 3, 0)
        form_layout.addWidget(self.new_game_filename_button, 3, 1)

        edit_layout.addLayout(form_layout)

        # Buttons with spacing for aesthetics
        button_layout = QHBoxLayout()
        self.new_game_add_button = QPushButton("Add New Game")
        self.new_game_add_button.clicked.connect(self.add_new_game)
        self.new_game_add_button.setFixedSize(200, 60)
        self.back_button_edit = QPushButton("Back to Main Menu")
        self.back_button_edit.clicked.connect(self.show_main_menu)
        self.back_button_edit.setFixedSize(200, 60)

        # Add some spacing
        button_layout.addStretch()
        button_layout.addWidget(self.new_game_add_button)
        button_layout.addWidget(self.back_button_edit)
        button_layout.addStretch()

        edit_layout.addLayout(button_layout)

        # Finalize the widget
        edit_widget.setLayout(edit_layout)
        self.views.addWidget(edit_widget)

    def select_new_game_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("All Files (*.*)")

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]  # Get the selected file path
            self.new_game_filename_button.setText(selected_file)  # Update button text with the file path

    def add_new_game(self):
        import os
        # Get data from the input fields
        name = self.new_game_name_input.text()
        categories = self.new_game_categories_input.text()
        source = self.new_game_source_input.text()
        filename = self.new_game_filename_button.text()

        if not all([name, categories, source, filename]):
            QMessageBox.warning(self, "Error", "Please fill in all fields before adding a new game.")
            return

        # Read 'cross_referenced_games.txt' to a string
        try:
            with open("cross_referenced_games.txt", "r") as file:
                cross_referenced_data = file.read()
                print("File content read successfully.")  # Debugging message
                cross_referenced_data += "name: "+name+", categories: ["+categories+"], source: "+source+", filename: " + os.path.basename(filename)+"\n"
            try:
                with open("cross_referenced_games.txt", "w") as f:
                    f.write(cross_referenced_data)
                    f.close()
            except:
                print("Error writing file")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "The file 'cross_referenced_games.txt' was not found.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while reading the file: {e}")

        # Copy the selected file to the program's directory
        try:
            import shutil
            import os

            program_dir = os.path.dirname(os.path.abspath(__file__))
            destination_path = os.path.join(program_dir, os.path.basename(filename))
            shutil.copy(filename, destination_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to copy file: {e}")
            return

        QMessageBox.information(self, "Success", f"New game '{name}' added successfully.")
        

    def create_list_view(self):
        list_widget = QWidget()
        list_layout = QVBoxLayout()

        self.data = self.filter_existing_files(self.load_data("cross_referenced_games.txt"))
        self.list_view = QTableView()
        self.model = DataModel(self.data)
        self.model.parent = self
        self.list_view.setModel(self.model)
        self.list_view.setSortingEnabled(True)
        self.list_view.resizeColumnsToContents()
        self.list_view.horizontalHeader().setStretchLastSection(True)
        self.list_view.setColumnWidth(1, 300)
        self.list_view.setColumnWidth(2, 200)  # Adjust category column width

        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by name or category...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)

        self.source_filter = QComboBox()
        self.source_filter.setEditable(True)
        self.source_filter.addItem("All Sources")
        self.source_filter.addItems(sorted(self.data["Source"].unique()))
        self.source_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.source_filter)

        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.clicked.connect(self.show_main_menu)

        list_layout.addLayout(filter_layout)
        list_layout.addWidget(self.list_view)
        list_layout.addWidget(self.back_button)
        list_widget.setLayout(list_layout)
        self.views.addWidget(list_widget)
        self.list_view.setColumnHidden(3, True)
        self.list_view.doubleClicked.connect(self.open_game)

    def create_favorites_view(self):
        fav_widget = QWidget()
        fav_layout = QVBoxLayout()

        self.favorites_view = QTableView()
        self.update_favorites_view()
        self.favorites_view.setSortingEnabled(True)
        self.back_button_fav = QPushButton("Back to Main Menu")
        self.back_button_fav.clicked.connect(self.show_main_menu)

        fav_layout.addWidget(self.favorites_view)
        fav_layout.addWidget(self.back_button_fav)
        fav_widget.setLayout(fav_layout)
        self.views.addWidget(fav_widget)
        self.favorites_view.setColumnHidden(3, True)
        self.favorites_view.doubleClicked.connect(self.open_game)
        self.favorites_view.horizontalHeader().setStretchLastSection(True)

    
    def open_game(self, index):
        current_model = self.list_view.model() if self.views.currentIndex() == 1 else self.favorites_view.model()
        game_name = current_model._data.iloc[index.row()]["Name"]

        # Check if 'Filename' column exists
        if "Filename" not in self.data.columns:
            print("Error: 'Filename' column is missing.")
            return

        # Retrieve the filename
        try:
            filename = self.data.loc[self.data["Name"] == game_name, "Filename"].values[0]
            if filename:
                # Check the file extension and decide which program to use
                if filename.endswith(".exe"):
                    # Run .exe files directly on Windows
                    subprocess.Popen(["wine", filename])
                elif filename.endswith(".swf"):
                    # Run with Flash Player for .swf files (ensure flashplayer is installed)
                    subprocess.Popen(["wine", 'Open With/flashplayer_11_sa.exe', filename])
                else:
                    # For any other file types, try opening with the default application
                    subprocess.Popen(['start', '', filename], shell=True)
            else:
                print(f"No executable filename found for {game_name}.")
        except IndexError:
            print(f"Error: No matching record found for {game_name}.")

    def normalize_turkish(self, text):
        from unicodedata import normalize
        return normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    def apply_filter(self):
        filter_text = self.normalize_turkish(self.filter_input.text().lower())
        selected_source = self.source_filter.currentText()

        filtered_data = self.data[self.data.apply(
            lambda row: filter_text in self.normalize_turkish(
                str(row["Name"]).lower()) or filter_text in self.normalize_turkish(str(row["Category"]).lower()), axis=1
        )]

        if selected_source != "All Sources":
            filtered_data = filtered_data[filtered_data["Source"] == selected_source]

        self.model = DataModel(filtered_data)
        self.model.parent = self
        self.list_view.setModel(self.model)

    def update_favorites_view(self, dynamic=False):
        # Filter the DataFrame to show only games from the favorites set
        self.data = self.filter_existing_files(self.load_data("cross_referenced_games.txt"))
        favorites_data = self.data[self.data["Name"].isin(self.favorites)].reset_index(drop=True)
        self.favorites_model = DataModel(favorites_data)
        self.favorites_model.parent = self
        self.favorites_view.setModel(self.favorites_model)
        if dynamic:
            self.favorites_view.resizeColumnsToContents()
            self.favorites_view.setColumnWidth(1, 300)
            self.favorites_view.horizontalHeader().setStretchLastSection(True)


    def update_list_view(self):
        self.model.layoutChanged.emit()
        self.data = self.filter_existing_files(self.load_data("cross_referenced_games.txt"))
        self.model = DataModel(self.data)
        self.model.parent = self
        self.list_view.setModel(self.model)
        # Automatically resize columns based on the content
        self.list_view.resizeColumnsToContents()

        # Manually set fixed widths for specific columns
        self.list_view.setColumnWidth(1, 300)  # Adjust 'Category' column width
        self.list_view.setColumnWidth(2, 200)  # Adjust 'Source' column width
        self.list_view.horizontalHeader().setStretchLastSection(True)  # Stretch last column

        # Optional: Apply filters or any pre-defined sorting
        self.apply_filter()



    def filter_existing_files(self, df):
        return df[df["Filename"].apply(lambda f: os.path.isfile(os.path.join(os.path.dirname(__file__), f)))]


    def load_data(self, file_path, encoding="utf-8"):
            self.favorites_set = {self.normalize_turkish(fav) for fav in self.favorites}
            data = []
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    for line in file:
                        match = re.match(
                            r"name: (.*?), categories: (.*?), source: (.*?), filename: (.*)", line.strip()
                        )
                        if match:
                            name, categories, source, filename = match.groups()
                            categories = categories.replace("'", "").replace("[", "").replace("]", "")
                            source = source.strip() if source.strip() else "unknown"
                            data.append([name.strip(), categories.strip(), source, filename.strip(), False])
            except FileNotFoundError:
                print(f"Error: The file '{file_path}' was not found.")
                return pd.DataFrame()  # Return an empty DataFrame if the file is not found.

            if not data:
                print(f"Warning: The file '{file_path}' is empty or data could not be parsed.")
                return pd.DataFrame()  # Return an empty DataFrame if no valid data is parsed.

            df = pd.DataFrame(data, columns=["Name", "Category", "Source", "Filename", "Favorite"])
            df["Favorite"] = df["Name"].apply(lambda x: self.normalize_turkish(x) in self.favorites_set)

            # Debugging: Ensure the Filename column exists
            if "Filename" not in df.columns:
                raise ValueError("Filename column is missing in the DataFrame.")

            return df


    def load_favorites(self, encoding="utf-8"):
        # Load favorites from the favorites.txt file and maintain them as a set
        try:
            with open(self.favorites_file, "r", encoding=encoding) as file:
                self.favorites = set(line.strip() for line in file)
                return self.favorites
        except FileNotFoundError:
            self.favorites = set()
            return self.favorites

    def save_favorites(self, encoding="utf-8"):
        # Save the updated favorites set to the favorites.txt file
        with open(self.favorites_file, "w", encoding=encoding) as file:
            file.writelines(f"{fav}\n" for fav in sorted(self.favorites))

    def show_main_menu(self):
        self.debounce_timer.stop()
        self.views.setCurrentIndex(0)
        self.views.setCurrentIndex(0)

    def show_list_view(self):
        self.update_list_view()
        self.views.setCurrentIndex(1)

    def show_favorites_view(self):
        self.update_favorites_view(dynamic=False)
        self.favorites_view.resizeColumnsToContents()
        self.favorites_view.resizeColumnsToContents()
        self.favorites_view.setColumnWidth(1, 300)  # Adjust category column width
        self.favorites_view.horizontalHeader().setStretchLastSection(True)
        self.views.setCurrentIndex(2)

    def show_edit_view(self):
        self.views.setCurrentIndex(3)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
