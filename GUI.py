import flet as ft
import fitness_tracker as ft_tracker
from datetime import date

def main(page: ft.Page):
    page.title = "Fitness Tracker"
    page.window_width = 600
    page.window_height = 500

    # Carica profilo
    profile = ft_tracker.load_profile()
    if profile is None:
        profile = ft_tracker.input_profile()

    # --- Input Profilo ---
    name = ft.TextField(label="Nome", value=profile.get('name'))
    age = ft.TextField(label="Età", value=str(profile.get('age')))
    sex = ft.TextField(label="Sesso (M/F)", value=profile.get('sex'))
    height = ft.TextField(label="Altezza (cm)", value=str(profile.get('height_cm')))
    weight = ft.TextField(label="Peso (kg)", value=str(profile.get('weight_kg')))
    goal = ft.TextField(label="Obiettivo peso", value=str(profile.get('goal_weight') or 0))
    activity = ft.TextField(label="Attività", value=profile.get('activity'))

    def save_profile_click(e):
        profile.update({
            'name': name.value,
            'age': int(age.value),
            'sex': sex.value,
            'height_cm': float(height.value),
            'weight_kg': float(weight.value),
            'goal_weight': float(goal.value),
            'activity': activity.value
        })
        ft_tracker.save_profile(profile)
        page.snack_bar = ft.SnackBar(ft.Text("Profilo salvato!"))
        page.snack_bar.open = True
        page.update()

    save_btn = ft.ElevatedButton("Salva Profilo", on_click=save_profile_click)

    # --- Input Log ---
    log_weight = ft.TextField(label="Peso (kg)")
    cal_in = ft.TextField(label="Calorie in")
    cal_out = ft.TextField(label="Calorie out")
    notes = ft.TextField(label="Note")

    def add_log_click(e):
        w = float(log_weight.value) if log_weight.value else None
        c_in_val = float(cal_in.value) if cal_in.value else 0
        c_out_val = float(cal_out.value) if cal_out.value else 0
        ft_tracker.add_log_entry(weight=w, calories_in=c_in_val, calories_burned=c_out_val, notes=notes.value)
        if w:
            profile['weight_kg'] = w
            ft_tracker.save_profile(profile)
        page.snack_bar = ft.SnackBar(ft.Text("Log aggiunto!"))
        page.snack_bar.open = True
        page.update()
        log_weight.value = ""
        cal_in.value = ""
        cal_out.value = ""
        notes.value = ""
        page.update()

    add_log_btn = ft.ElevatedButton("Aggiungi Log", on_click=add_log_click)

    # Layout
    profile_col = ft.Column([
        ft.Text("Profilo", weight="bold"),
        name, age, sex, height, weight, goal, activity, save_btn,
        ft.Divider(),
        ft.Text("Aggiungi Log", weight="bold"),
        log_weight, cal_in, cal_out, notes, add_log_btn
    ], spacing=10, expand=True)

    page.add(profile_col)

ft.app(target=main, view=ft.WEB_BROWSER)
