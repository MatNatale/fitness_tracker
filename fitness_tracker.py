"""
fitness_tracker.py - semplice tracker CLI per BMI, peso, calorie e frafico settimanale.
Salva dati in ~/fitness_tracker/profile.json e ~/fitness_tracker/logs.csv
"""
import os
import json
import csv
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
from tkinter import messagebox

"""Contiene il percorso espanso /Users/matteonatale/fitness_tracker"""

DATA_DIR = os.path.expanduser('~/fitness_tracker')

"""
PROFILE_PATH è una stringa che contiene il percorso completo del file profile.json, il quale
è un file JSON che contiene i dati del profilo dell'utente. In sostanza, PROFILE_PATH contiene il percorso
/Users/matteonatale/fitness_tracker/profile.json
"""
PROFILE_PATH = os.path.join(DATA_DIR, 'profile.json')

"""
LOGS_PATH è il percorso assoluto del file CSV che terrà tutte le registrazioni (log) dell'utente
/Users/matteonatale/fitness_tracker/logs.csv
"""

LOGS_PATH = os.path.join(DATA_DIR, 'logs.csv')

"""
ensure_data_dir è una funzione che si assicura che la cartella dovere salveremo i file
profile.json e logs.csv sia presente; se non lo è, la crea, se lo è, non fa nulla
"""

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

"""
save_profile è una funzione che prende i dati dell'utente, li trasforma in JSON e li salva nel file
profile.json dentro la cartella dei dati
"""

def save_profile(profile: dict):
    ensure_data_dir()
    with open(PROFILE_PATH, 'w') as f:
        return json.dump(profile, f, indent=2)
    print("Profilo salvato in", PROFILE_PATH)

"""
load_profile è una funzione che controlla se esiste profile.json e, se esiste, legge il file e 
lo trasforma in dizionario python, altrimenti ritorna None
"""

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH) as f:
            return json.load(f)
    return None

"""
input_profile è una funzione che chiede all'utente tutte le informazioni del profilo, 
valida l'input(età, perso, sesso, ecc.)
crea un dizionario profile
salva tale dizionario su file (profile.json)
restituisce il profilo pronto per essere usato dal programma
"""

def input_profile():
    print("Crea / aggiorna profilo")
    name = input("Nome: ").strip() or "Utente"
    while True:
        try:
            age = int(input("Età (anni): ").strip())
            break
        except Exception:
            print("Inserisci un numero intero valido per l'età.")
    sex = input("Sesso (M/F): ").strip().upper()[:1]
    while sex not in ('M', 'F'):
        sex = input("Sesso (M/F): ").strip().upper()[:1]
    while True:
        try:
            height_cm = float(input("Altezza (cm): ").strip())
            break
        except Exception:
            print("Inserisci un numero valido per l'altezza.")
    while True:
        try: 
            weight_kg = float(input("Peso attuale (kg): ").strip())
            break
        except Exception:
            print("Inserisci un numero valido per il peso.")
    gw = input("Obiettivo peso in kg (lascia vuoto se nessuno): ").strip()
    goal_weight = float(gw) if gw else None
    activity = input("Livello attività (sedentary/light/moderate/active/very_active) [moderate]: ").strip().lower()
    if activity not in ('sedentary', 'light', 'moderate', 'active', 'very_active'):
        activity = 'moderate'
    profile = {
        'name': name,
        'age': age,
        'sex': sex,
        'height_cm': height_cm,
        'weight_kg': weight_kg,
        'goal_weight': goal_weight,
        'activity': activity
    }
    save_profile(profile)
    return profile

"""
calculate_bmi è una funzione che calcola il BMI dell'utente come il rapporto tra il peso in kg e l'altezza
al quadrato espressa in metri
"""

def calculate_bmi(weight, height_cm):
    h = height_cm / 100.0
    if h <= 0:
        return None
    return weight / (h * h)

"""
bmi_category è una funzione che categorizza l'utente secondo il suo BMI in:
Sottopeso, Normale, Sovrappeso, Obeso di tipo I, II o III
"""

def bmi_category(bmi):
    if bmi is None:
        return "N/A"
    if bmi < 18.5:
        return "Sottopeso"
    if bmi < 25:
        return "Normale"
    if bmi < 30:
        return "Sovrappeso"
    if bmi < 35:
        return "Obesità I"
    if bmi < 49:
        return "Obesità II"
    return "Obesità III"

"""
bmr_mifflin è una funzione che calcola il metabolismo basale bmr dell'utente in base al peso, 
all'altezza, all'età e al sesso, secondo la formula di Mifflin-St Jeor
"""

def bmr_mifflin(weight, height_cm, age, sex):
    if sex.upper().startswith('M'):
        return 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height_cm - 5 * age - 161
    
ACTIVITY_FACTORS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9
}

"""
tdee è una funzione che calcola il fabbisogno calorico giornaliero (tdee) dell'utente, in base
al suo metabolismo basale (bmr) ed al livello di attività fisica (activity)
"""

def tdee(bmr, activity):
    factor = ACTIVITY_FACTORS.get(activity, 1.55)
    return bmr * factor

"""
ensure_logs_file è una funzione che garantisce che il file CSV dei log esista e sia pronto per l'uso
"""

def ensure_logs_file():
    ensure_data_dir()
    if not os.path.exists(LOGS_PATH):
        with open(LOGS_PATH, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['date', 'weight_kg', 'calories_in', 'calories_burned', 'notes'])

"""
add_log_enrtry è una funzione che si assicura che il file CSV esista,
imposta la data odierna se non specificata
apre il CSV in modalità append
scrive i dati della giornata (data, peso, calorie in/out, note)
conferma a video l'inserimento
"""

def add_log_entry(date_str=None, weight=None, calories_in=0, calories_burned=0, notes=''):
    ensure_logs_file()
    if date_str is None:
        date_str = date.today().isoformat()
    with open(LOGS_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date_str, weight or '', calories_in or 0, calories_burned or 0, notes or ''])
    print("Entry aggiunta:", date_str, weight)

"""
load_logs è una funzione che restituisce tutti i dati dei log. Questi vengono restituiti:
come lista di dizionari se pandas non è disponibile
come DataFrame pandas se è disponibile.
Converte automaticamente le date in oggetti date e i valori numerici in float
Gestisce eventuali errori e valori mancanti
"""

def load_logs():
    ensure_logs_file()
    if pd is None:
        rows = []
        with open(LOGS_PATH) as f:
            r = csv.DictReader(f)
            for row in r:
                try:
                    row['date'] = datetime.fromisoformrat(row['date']).date()
                except Exception:
                    row['date'] = row['date']
                for k in ('weight_kg', 'calories_in', 'calories_burned'):
                    try:
                        row[k] = float(row[k]) if row[k] != '' else None
                    except Exception:
                        row[k] = None
                rows.append(row)
            return rows
    else:
        df = pd.read_csv(LOGS_PATH, parse_dates=['date'])
        df['date'] = pd.to_datetime(df['date'], format="mixed", errors='coerce').dt.date
        df = df.dropna(subset=['date'])  # elimina righe senza data valida
        df = pd.read_csv(LOGS_PATH, parse_dates=['date'], dayfirst=False, on_bad_lines='skip')
        return df
    
"""
plot_weekly_weight è una funzione che controlla che pandas e matplotlib siano disponibili,
legge i log dal CSV,
trasforma le date e ordina i dati,
calcola la media settimanale del peso,
disegna un grafico a linee mostrando l'andamento del peso nel tempo,
gestisce casi senza dati mostrando messaggi appropriati
"""

def plot_weekly_weight():
    if pd is None:
        print("Per creare il grafico, installa pandas e matplotlib:")
        print("python3 -m pip install --user pandas matplotlib")
        return
    df = load_logs()
    if df.empty:
        print("Nessun dato da mostrare.")
        return
    df2 = df.copy()
    df2['date'] = pd.to_datetime(df2['date'], format="mixed", errors="coerce")
    df2 = df2.set_index('date').sort_index()
    weekly = df2['weight_kg'].resample('W').mean().dropna()
    if weekly.empty:
        print("Non ci sono pesi validi per calcolare la media settimanale.")
        return
    plt.figure()
    plt.plot(weekly.index.to_pydatetime(), weekly.values)
    plt.title('Andamento peso (media settimanale)')
    plt.xlabel('Data')
    plt.ylabel('Peso (kg)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.pause(0.1)

"""
show_profile_and_stats è una funzione che mostra informazioni base del profilo,
calcola e mostra il bMI e la susa categoria,
calcola e mostra il BMR,
calcola e mostra il TDEE stimato,
mostra l'obiettivo di peso e il delta rispetto al peso attuale
"""
def show_profile_and_stats(profile):
    print("\nProfilo:", profile.get('name'))
    print(f"Età : {profile.get('age')} Sesso: {profile.get('sex')} Altezza: {profile.get('height_cm')} cm Peso: {profile.get('weight_kg')} kg")
    bmi = calculate_bmi(profile['weight_kg'], profile['height_cm'])
    print(f"BMI: {bmi:.2f} ({bmi_category(bmi)})")
    bmr = bmr_mifflin(profile['weight_kg'], profile['height_cm'], profile['age'], profile['sex'])
    print(f"BMR (Mifflin-St Jeor): {bmr:.0f} kcal/giorno")
    t = tdee(bmr, profile.get('activity', 'moderate'))
    print(f"TDEE stimato: {t:.0f} kcal/giorno (livello attività: {profile.get('activity')})")
    if profile.get('goal_weight'):
        dw = profile['goal_weight'] - profile['weight_kg']
        print(f"Obiettivo peso: {profile['goal_weight']} kg (delta {dw:+.1f} kg)")

"""
clean_logs_file è una funzione che pulisce il file di log, scartando le righe con date non valide,
convertendo le colonne numeriche in float o mettendole a None e risalvando il CSV pulito
"""

def clean_logs_file():
    if not os.path.exists(LOGS_PATH):
        print("Nessun file di log trovato da pulire.")
        return
    try:
        df = pd.read_csv(LOGS_PATH)
        df['date'] = pd.to_datetime(df['date'], format="mixed", errors='coerce')
        before = len(df)
        df = df.dropna(subset=['date'])
        after = len(df)
        for col in ['weight_kg', 'calories_in', 'calories_burned']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df.to_csv(LOGS_PATH, index=False)
        print(f"File dei log ripulito: {before - after} righe scartate, {after} righe valide mantenute.")

    except Exception as e:
        print("Errore durante la pulizia dei log:", e)


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

"""
main è la funzione che gestisce tutta l'interazione con l'utente. Permette di:
mostrare profilo e statistiche,
aggiornare il profilo,
aggiungere log giornalieri,
mostrare grafico settimanale del peso
uscire dal programma
"""
"""
def main():
    ensure_data_dir()
    ensure_logs_file()
    clean_logs_file()
    profile = load_profile()
    if profile is None:
        print("Non c'è ancora un profilo. Creane uno.")
        profile = input_profile()
    while True:
        print("\n--- Menu ---")
        print("1) Mostra profilo e calorie")
        print("2) Aggiorna profilo")
        print("3) Aggiungi registrazione peso / kcal")
        print("4) Mostra grafico andamento perso (settimanale)")
        print("5) Esci")
        choice = input("Scegli: ").strip()
        if choice == '1':
            show_profile_and_stats(profile)
        elif choice == '2':
            profile = input_profile()
        elif choice == '3':
            d = input("Data (YYYY-MM-DD, invio = oggi): ").strip()
            d = d if d else date.today().isoformat()
            w = input("Peso (kg): ").strip()
            w = float(w) if w else None
            c_in = input("Calorie assunte (kcal): ").strip()
            c_in = float(c_in) if c_in else 0
            c_burn = input("Calorie bruciate (attività) (kcal): ").strip()
            c_burn = float(c_burn) if c_burn else 0
            notes = input("Note (opzionale): ").strip()
            add_log_entry(d, w, c_in, c_burn, notes)
            if w:
                profile['weight_kg'] = w
                save_profile(profile)
        elif choice == '4':
            plot_weekly_weight()
        elif choice == '5':
            print("Ciao!")
            break
        else:
            print("Scelta non valida.")

if __name__ == '__main__':
    main()
"""