from fitness_tracker import (
    load_logs, load_profile, input_profile, calculate_bmi, bmi_category, bmr_mifflin, tdee, ensure_data_dir, 
    ensure_logs_file, add_log_entry, plot_weekly_weight, show_profile_and_stats, clean_logs_file
)
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox, QFormLayout
)
from datetime import date, datetime
try:
    import pandas as pd
except Exception:
    pd = None
import matplotlib.pyplot as plt

"""
--- GUI ---
"""

class FitnessTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness Tracker")
        self.setGeometry(100,100,400,500)
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("<h2>Fiteness Tracker</h2>"))

        profile_btn = QPushButton("Mostra Profilo")
        profile_btn.clicked.connect(self.show_profile)
        self.layout.addWidget(profile_btn)

        self.form_layout = QFormLayout()
        self.weight_input = QLineEdit()
        self.calories_input = QLineEdit()
        self.notes_input = QLineEdit()
        self.form_layout.addRow("Peso (kg):", self.weight_input)
        self.form_layout.addRow("Calorie:", self.calories_input)
        self.form_layout.addRow("Note:", self.notes_input)
        self.layout.addLayout(self.form_layout)

        add_log_btn = QPushButton("Aggiungi Log")
        add_log_btn.clicked.connect(self.add_log)
        self.layout.addWidget(add_log_btn)

        graph_btn = QPushButton("Mostra Grafico Peso")
        add_log_btn.clicked.connect(self.show_graph)
        self.layout.addWidget(graph_btn)

        self.setLayout(self.layout)

    def show_profile(self):
        profile = load_profile()
        if profile:
            info = (f"Nome: {profile.get('name', '')}\n"
                    f"Età: {profile.get('age','')}\n"
                    f"Sesso: {profile.get('sex','')}\n"
                    f"Peso: {profile.get('weight_kg','')}")
            QMessageBox.information(self, "Profilo", info)
        else:
            QMessageBox.information(self, "Profilo", "Nessun profilo salvato.")
    
    def add_log(self):
        try:
            w = float(self.weight_input.text())
            c = float(self.calories_input.text())
        except ValueError:
            QMessageBox.warning(self, "Errore", "Peso o calorie non validi")
            return
        notes = self.notes_input.text()
        add_log_entry(w,c, notes)
        QMessageBox.information(self, "Fatto", "Log aggiunto!")
        self.weight_input.clear()
        self.calories_input.clear()
        self.notes_input.clear()

    def show_graph(self):
        df = load_logs()
        if df.empty():
            QMessageBox.information(self, "Grafico", "Nessun dato da mostrare")
            return
        df = df.groupby(pd.Grouper(key='date', freq='W')).mean()
        plt.plot(df.index, df['weight_kg'])
        plt.title("Andamento Peso (media settimanale)")
        plt.xlabel("Data")
        plt.ylabel("Peso (kg)")
        plt.grid(True)
        plt.show()

app = QApplication(sys.argv)
window = FitnessTracker()
window.show()
sys.exit(app.exec_())
