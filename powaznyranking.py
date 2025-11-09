import gi
import os
import json

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Player:
    def __init__(self, name, points, min_points, races=0):
        # Inicjalizacja atrybutów gracza
        self.name = name
        self.points = points
        self.min_points = min_points
        self.races = races
        self.points_after = points
        self.outcome = 0

RankNames = [
    "Drewno 1", "Drewno 2", "Drewno 3", "Brąz 1", "Brąz 2", "Brąz 3",
    "Srebro 1", "Srebro 2", "Srebro 3", "Złoto 1", "Złoto 2", "Złoto 3",
    "Platyna 1", "Platyna 2", "Platyna 3", "Szmaragd 1", "Szmaragd 2", "Szmaragd 3",
    "Diament 1", "Diament 2", "Diament 3", "Szafir 1", "Szafir 2", "Szafir 3",
    "Rubin 1", "Rubin 2", "Rubin 3", "Legenda"
]

RankThresholds = [
    # Progi punktowe dla każdej rangi
    0, 75, 150, 250, 325, 400, 525, 625, 725, 875, 1000, 1125,
    1300, 1450, 1600, 1800, 1975, 2150, 2375, 2575, 2775, 3050,
    3325, 3625, 3950, 4400, 5000, 999999
]

# TARCZA: Współczynnik straty, rosnący co 3 rangi, używana do zmniejszenia utraty punktów
Shields = [0.1] * 3 + [0.2] * 3 + [0.3] * 3 + [0.4] * 3 + [0.5] * 3 + [0.6] * 3 + [0.7] * 3 + [0.8] * 3 + [0.9] * 3 + [1.0]

WorseWin = [50, 46, 42, 39, 36, 33, 31, 29, 27, 26, 25]  # Punkty za wygraną z gorszym graczem
BetterWin = [50, 55, 60, 65, 70, 75, 85, 95, 105, 115, 125]  # Punkty za wygraną z lepszym graczem
BetterLose = [-50, -55, -60, -65, -70, -75, -85, -95, -105, -115, -125]  # Punkty stracone przy przegranej z lepszym graczem
WorseLose = [-50, -45, -40, -35, -30, -25, -22, -19, -16, -13, -10]  # Punkty stracone przy przegranej z gorszym graczem

DBPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liga.json")  # Ścieżka do pliku bazy danych JSON

def get_player_rank(points):
    # Określa rangę gracza na podstawie jego punktów
    for i, threshold in enumerate(RankThresholds):
        if points < threshold:
            return i
    return len(RankThresholds) - 1

def calculate_points(players, racers, multiplier):
    # Obliczanie punktów dla wszystkich graczy na podstawie wyników wyścigu
    def adjust_points_for_no_outcome(player, rank):
        # DECAY: Odjęcie punktów graczom, którzy nie brali udziału w wyścigu, ale skończyli placementy
        deductions = [1, 2, 3, 4, 5]
        thresholds = [6, 12, 18, 24, 28]
        for deduction, threshold in zip(deductions, thresholds):
            if rank <= threshold:
                player.points_after = max(player.points - deduction, player.min_points, 0)
                return

    def calculate_rank_difference_points(player, opponent, rank_diff, my_rank, his_rank):
        # Obliczanie punktów na podstawie różnicy rang i wyniku wyścigu
        if my_rank < his_rank:
            return BetterWin[rank_diff] if player.outcome < opponent.outcome else WorseLose[rank_diff]
        return WorseWin[rank_diff] if player.outcome < opponent.outcome else BetterLose[rank_diff]

    for player in players:
        my_rank = get_player_rank(player.points)
        if player.outcome == 0:
            # Gracze którzy nie przeszli placementy, są zwolnieni z kar
            if player.races >= 5:
                adjust_points_for_no_outcome(player, my_rank)
            else:
                player.points_after = player.points
        else:
            change = sum(
                calculate_rank_difference_points(player, opponent, min(abs(get_player_rank(opponent.points) - my_rank), 10), my_rank, get_player_rank(opponent.points))
                for opponent in players if opponent.outcome != 0 and player.outcome != opponent.outcome
            )
            if racers > 1:
                change /= (racers - 1)  # Obliczanie średniej punktów
            change *= multiplier * (2 if player.races < 5 else 1)  # Zastosowanie mnożnika i bonusu w trakcie placementów
            if change < 0 and player.races >= 5:
                change *= Shields[my_rank - 1]  # Zastosowanie tarczy po placementach w przypadku straty punktów
            player.points_after = max(player.points + int(change), player.min_points, 0)  # punkty nie spadają poniżej minimum

def load_players_from_json(filepath):
    # Wczytanie graczy z pliku JSON
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Player(entry["name"], entry["points"], entry["min_points"], entry.get("races", 0)) for entry in data]

# Okno dialogowe do edycji wyników wyścigu
class OutcomeEditDialog(Gtk.Dialog):
    def __init__(self, parent, players, current_multiplier):
        super().__init__(title="Wpisz zajęte miejsca w wyścigu", transient_for=parent, modal=True)
        self.set_default_size(400, 300)
        self.players = players
        self.selected_players = []
        self.entries = []
        self.multiplier = current_multiplier

        # Widget: Zapełnianie pozycji graczy
        content_area = self.get_content_area()
        self.grid = Gtk.Grid(column_spacing=4, row_spacing=4)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        content_area.add(self.grid)

        self.add_player_row()

        # Widget od mnożnika
        multiplier_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        multiplier_label = Gtk.Label(label="Mnożnik:")
        self.multiplier_spin = Gtk.SpinButton()
        self.multiplier_spin.set_range(1, 5) # Max mnożnik 5
        self.multiplier_spin.set_increments(1, 1)
        self.multiplier_spin.set_value(current_multiplier)
        multiplier_box.pack_start(multiplier_label, False, False, 0)
        multiplier_box.pack_start(self.multiplier_spin, False, False, 0)
        content_area.pack_end(multiplier_box, False, False, 10)  # Przypięcie mnożnika na dół okna

        self.add_buttons("OK", Gtk.ResponseType.OK, "Anuluj", Gtk.ResponseType.CANCEL)
        self.show_all()

    # Funkcja dodaje nowy wiersz z wyborem gracza i miejscem
    def add_player_row(self):
        row = len(self.selected_players)  
        player_combo = Gtk.ComboBoxText()
        player_combo.set_hexpand(True) 
        player_combo.append_text("Wybierz gracza")
        for player in self.players:
            if player not in self.selected_players:
                player_combo.append_text(player.name)
        player_combo.set_active(0)
        player_combo.connect("changed", self.on_player_selection_changed)

        outcome_spin = Gtk.SpinButton()
        outcome_spin.set_range(0, 100)
        outcome_spin.set_increments(1, 5)
        outcome_spin.set_value(row + 1) 

        add_button = Gtk.Button(label="+")
        add_button.set_sensitive(False) 
        add_button.connect("clicked", self.on_add_player_clicked, player_combo, outcome_spin)

        remove_button = Gtk.Button(label="-")
        remove_button.set_sensitive(False)
        remove_button.connect("clicked", self.on_remove_player_clicked, player_combo, outcome_spin, row)

        self.grid.attach(player_combo, 0, row, 1, 1)
        self.grid.attach(outcome_spin, 1, row, 1, 1)
        self.grid.attach(add_button, 2, row, 1, 1)
        self.grid.attach(remove_button, 3, row, 1, 1)
        self.show_all()

    # Po zmianie parametrów w wierszu, aktualizuje stan przycisków "+" i "-"
    def on_player_selection_changed(self, combo):
        row = self.grid.child_get_property(combo, "top-attach")
        add_button = self.grid.get_child_at(2, row)  
        remove_button = self.grid.get_child_at(3, row)
        if combo.get_active_text() == "Wybierz gracza":
            add_button.set_sensitive(False)
            remove_button.set_sensitive(False)
        else:
            add_button.set_sensitive(True)
            remove_button.set_sensitive(True)

    # Po kliknięciu przycisku "+" dodaje wybranego gracza do listy i tworzy nowy wiersz
    def on_add_player_clicked(self, button, player_combo, outcome_spin):
        player_name = player_combo.get_active_text()
        if player_name == "Wybierz gracza" or not player_name:
            return

        selected_player = next((p for p in self.players if p.name == player_name), None)
        if not selected_player:
            return

        self.selected_players.append(selected_player)
        self.entries.append((selected_player, outcome_spin))

        self.add_player_row()

    # Po kliknięciu przycisku "-" usuwa gracza z listy
    def on_remove_player_clicked(self, button, player_combo, outcome_spin, row):
        player_name = player_combo.get_active_text()
        if player_name == "Wybierz gracza" or not player_name:
            return 

        selected_player = next((p for p in self.players if p.name == player_name), None)
        if not selected_player:
            return

        if selected_player in self.selected_players:
            self.selected_players.remove(selected_player)
        self.entries = [(p, spin) for p, spin in self.entries if p != selected_player]

        self.grid.remove_row(row)
        self.rebuild_grid()

    # Sync siatki/listy po usunięciu wiersza
    def rebuild_grid(self):
        self.grid.foreach(lambda widget: self.grid.remove(widget))
        for i, (player, spin) in enumerate(self.entries):
            player_combo = Gtk.ComboBoxText()
            player_combo.append_text(player.name)
            player_combo.set_active(0)

            add_button = Gtk.Button(label="+")
            add_button.connect("clicked", self.on_add_player_clicked, player_combo, spin)

            remove_button = Gtk.Button(label="-")
            remove_button.connect("clicked", self.on_remove_player_clicked, player_combo, spin, i)

            self.grid.attach(player_combo, 0, i, 1, 1)
            self.grid.attach(spin, 1, i, 1, 1)
            self.grid.attach(add_button, 2, i, 1, 1)
            self.grid.attach(remove_button, 3, i, 1, 1)
        self.add_player_row()
        self.show_all()

    # Pobiera wyniki
    def get_outcomes(self):
        outcomes = [0] * len(self.players)

        for player, spin in self.entries:
            outcomes[self.players.index(player)] = spin.get_value_as_int()

        if self.grid.get_children():
            last_row = len(self.entries) 
            player_combo = self.grid.get_child_at(0, last_row) 
            outcome_spin = self.grid.get_child_at(1, last_row) 
            if player_combo and outcome_spin:
                player_name = player_combo.get_active_text()
                if player_name and player_name != "Wybierz gracza":
                    selected_player = next((p for p in self.players if p.name == player_name), None)
                    if selected_player and selected_player not in self.selected_players:
                        outcomes[self.players.index(selected_player)] = outcome_spin.get_value_as_int()

        return outcomes

    # Pobiera mnożnik
    def get_multiplier(self):
        return self.multiplier_spin.get_value_as_int()
    
# Okno dialogowe do symulacji wyników wyścigu
class ResultSimulationDialog(Gtk.Dialog):
    def __init__(self, parent, players, multiplier):
        super().__init__(title="Symulacja wyników", transient_for=parent, modal=True)
        self.set_default_size(700, 400)

        # Obliczanie punktów na podstawie symulacji
        racers = sum(1 for p in players if p.outcome > 0)
        calculate_points(players, racers, multiplier)

        # Utworzenie pamięci do przechowywania symulacji
        self.liststore = Gtk.ListStore(str, str, int, str, int, str, int, str)
        for player in players:
            old_rank = RankNames[get_player_rank(player.points) - 1]
            new_rank = RankNames[get_player_rank(player.points_after) - 1]
            diff = player.points_after - player.points
            if diff != 0:  # Wykluczenie graczy którym się nic nie zmienia
                diff_str = f"+{diff}" if diff >= 0 else str(diff)

                # Obliczanie punktów potrzebnych do awansu
                next_rank_threshold = RankThresholds[get_player_rank(player.points_after)]
                points_to_promotion = max(0, next_rank_threshold - player.points_after)

                # Określenie statusu
                if get_player_rank(player.points_after) > get_player_rank(player.points):
                    status = "AWANS"
                elif get_player_rank(player.points_after) < get_player_rank(player.points):
                    status = "SPADEK"
                else:
                    status = ""

                self.liststore.append([
                    player.name, old_rank, player.points, new_rank, player.points_after, diff_str, points_to_promotion, status
                ])

        # Utworzenie tabelki do wyświetlania wyników
        treeview = Gtk.TreeView(model=self.liststore)

        # Definiowanie kolumn tabelki
        columns = [
            ("Nick", 0),
            ("Stara ranga", 1),
            ("Stare punkty", 2),
            ("Nowa ranga", 3),
            ("Nowe punkty", 4),
            ("Postęp", 5),
            ("Do Awansu", 6),
            ("Status", 7)
        ]
        for col_title, col_idx in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title=col_title, cell_renderer=renderer, text=col_idx)
            treeview.append_column(column)

        # Dodanie Tabelki do okna dialogowego
        content_area = self.get_content_area()
        content_area.add(treeview)

        self.add_buttons("Zapisz do JSON", Gtk.ResponseType.OK, "Anuluj", Gtk.ResponseType.CANCEL)
        self.show_all()

# Główne okno aplikacji
class PlayerTable(Gtk.Window):
    def __init__(self, players, json_path):
        super().__init__(title="Poważny ranking")
        self.set_default_size(400, 400)
        self.players = players
        self.json_path = json_path
        self.multiplier = 1 # Zresetuj mnożnik do 1 przy starcie
        self.saved_state = [Player(p.name, p.points, p.min_points, p.races) for p in players]

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.liststore = Gtk.ListStore(str, int, int, str, int)
        for p in self.players:
            rank_name = RankNames[get_player_rank(p.points) - 1]
            self.liststore.append([p.name, p.points, p.min_points, rank_name, p.races])

        self.treeview = Gtk.TreeView(model=self.liststore)
        columns = [
            ("Nick", 0),
            ("Punkty", 1),
            ("Minimum", 2),
            ("Ranga", 3),
            ("Wyścigów", 4)
        ]
        for col_title, col_idx in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title=col_title, cell_renderer=renderer, text=col_idx)
            column.set_sort_column_id(col_idx)
            self.treeview.append_column(column)

        # Dodaj Scroll jeżeli wszystko nie mieści się w tabeli
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.treeview) 
        vbox.pack_start(scrolled_window, True, True, 0)

        # Poprawne podłączenie sygnału do podwójnego kliknięcia
        self.treeview.connect("row-activated", self.on_treeview_row_activated)

        button = Gtk.Button(label="Nowy wyścig")
        button.connect("clicked", self.on_new_race_clicked)
        vbox.pack_start(button, False, False, 0)

        add_button = Gtk.Button(label="Dodaj gracza do bazy")
        add_button.connect("clicked", self.on_add_player_clicked)
        vbox.pack_start(add_button, False, False, 0)

        self.revert_button = Gtk.Button(label="Cofnij zmiany symulacji")
        self.revert_button.connect("clicked", self.on_revert_changes_clicked)
        self.revert_button.set_sensitive(False)
        vbox.pack_start(self.revert_button, False, False, 0)

    # Kliknięcie "Nowy wyścig"
    def on_new_race_clicked(self, button):
        dialog = OutcomeEditDialog(self, self.players, self.multiplier)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            outcomes = dialog.get_outcomes()
            self.multiplier = dialog.get_multiplier()
            for i, player in enumerate(self.players):
                player.outcome = outcomes[i]
            dialog.destroy()

            sim_dialog = ResultSimulationDialog(self, self.players, self.multiplier)
            sim_response = sim_dialog.run()
            if sim_response == Gtk.ResponseType.OK:
                # Dodaj +1 do liczby wyścigów dla graczy, którzy brali udział w symulacji
                for player in self.players:
                    if player.outcome > 0:
                        player.races += 1
                self.update_points()
                self.save_to_json()
                self.revert_button.set_sensitive(True)
            sim_dialog.destroy()
        else:
            dialog.destroy()

    # Aktualizacja punktów i rang w tabeli
    def update_points(self):
        racers = sum(1 for p in self.players if p.outcome > 0)
        calculate_points(self.players, racers, self.multiplier)
        for i, row in enumerate(self.liststore):
            player = self.players[i]
            row[1] = player.points_after
            row[3] = RankNames[get_player_rank(player.points_after) - 1]
            player.points = player.points_after

    # Zapis zmian do pliku JSON
    def save_to_json(self):
        self.saved_state = [Player(p.name, p.points, p.min_points, p.races) for p in self.players]
        data = [
            {
                "name": row[0],
                "points": row[1],
                "min_points": row[2],
                "races": row[4]
            }
            for row in self.liststore
        ]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.revert_button.set_sensitive(False)

        # Odśwież tabelę po zapisie
        self.liststore.clear()
        for p in self.players:
            rank_name = RankNames[get_player_rank(p.points)-1]
            self.liststore.append([p.name, p.points, p.min_points, rank_name, p.races])

    # Kliknięcie "Cofnij zmiany symulacji"
    def on_revert_changes_clicked(self, button):
        self.players = [Player(p.name, p.points, p.min_points, p.races) for p in self.saved_state]
        self.liststore.clear()
        for p in self.players:
            rank_name = RankNames[get_player_rank(p.points) - 1]
            self.liststore.append([p.name, p.points, p.min_points, rank_name, p.races])
        self.revert_button.set_sensitive(False)

    # Kliknięcie "Dodaj gracza do bazy"
    def on_add_player_clicked(self, button):
        dialog = Gtk.Dialog(title="Dodaj nowego gracza", transient_for=self, modal=True)
        dialog.set_default_size(300, 100)
        content_area = dialog.get_content_area()

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        content_area.add(grid)

        name_label = Gtk.Label(label="Nick:")
        name_entry = Gtk.Entry()
        grid.attach(name_label, 0, 0, 1, 1)
        grid.attach(name_entry, 1, 0, 1, 1)

        dialog.add_buttons("Dodaj", Gtk.ResponseType.OK, "Anuluj", Gtk.ResponseType.CANCEL)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = name_entry.get_text().strip()
            if name:
                new_player = Player(name, 250, 0, 0)
                self.players.append(new_player)
                rank_name = RankNames[get_player_rank(new_player.points) - 1]
                self.liststore.append([new_player.name, new_player.points, new_player.min_points, rank_name, new_player.races])
        dialog.destroy()

    # Zastępuje menu kontekstowe - podwójne kliknięcie otwiera okno edycji
    def on_treeview_row_activated(self, treeview, path, column):
        # Otwiera okno edycji po podwójnym kliknięciu na wiersz
        self.on_edit_player(None, path)

    # Kliknięcie "Edytuj" w menu kontekstowym lub podwójne kliknięcie
    def on_edit_player(self, menu_item, path):
        tree_iter = self.liststore.get_iter(path)
        player_data = self.liststore[path]

        dialog = Gtk.Dialog(title="Edytuj gracza", transient_for=self, modal=True)
        dialog.set_default_size(300, 200)
        content_area = dialog.get_content_area()

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        content_area.add(grid)

        # Dodaj pola do edycji z wartościami
        name_label = Gtk.Label(label="Nick:")
        name_entry = Gtk.Entry()
        name_entry.set_text(player_data[0])
        name_entry.set_editable(True)
        grid.attach(name_label, 0, 0, 1, 1)
        grid.attach(name_entry, 1, 0, 1, 1)

        points_label = Gtk.Label(label="Punkty:")
        points_entry = Gtk.Entry()
        points_entry.set_text(str(player_data[1]))
        points_entry.set_editable(True)
        points_entry.connect("changed", self.on_numeric_input)
        grid.attach(points_label, 0, 1, 1, 1)
        grid.attach(points_entry, 1, 1, 1, 1)

        min_points_label = Gtk.Label(label="Minimum:")
        min_points_entry = Gtk.Entry()
        min_points_entry.set_text(str(player_data[2]))
        min_points_entry.set_editable(True)
        min_points_entry.connect("changed", self.on_numeric_input)
        grid.attach(min_points_label, 0, 2, 1, 1)
        grid.attach(min_points_entry, 1, 2, 1, 1)

        races_label = Gtk.Label(label="Wyścigów:")
        races_entry = Gtk.Entry()
        races_entry.set_text(str(player_data[4]))
        races_entry.set_editable(True)
        races_entry.connect("changed", self.on_numeric_input)
        grid.attach(races_label, 0, 3, 1, 1)
        grid.attach(races_entry, 1, 3, 1, 1)

        # Usuń przycisk z siatki, dodaj go obok przycisków dialogowych
        delete_button = Gtk.Button(label="Usuń gracza")
        delete_button.connect("clicked", lambda btn: self._delete_player_and_close_dialog(dialog, path))

        # Dodaj przyciski na dole okna
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_halign(Gtk.Align.END)
        action_box.pack_start(delete_button, False, False, 0)

        # Dodaj przyciski Zapisz i Anuluj
        save_button = Gtk.Button(label="Zapisz")
        cancel_button = Gtk.Button(label="Anuluj")
        action_box.pack_start(save_button, False, False, 0)
        action_box.pack_start(cancel_button, False, False, 0)
        content_area.pack_end(action_box, False, False, 10)

        save_button.connect("clicked", lambda btn: dialog.response(Gtk.ResponseType.OK))
        cancel_button.connect("clicked", lambda btn: dialog.response(Gtk.ResponseType.CANCEL))

        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.liststore[path] = [
                name_entry.get_text(),
                int(points_entry.get_text()),
                int(min_points_entry.get_text()),
                RankNames[get_player_rank(int(points_entry.get_text())) - 1],
                int(races_entry.get_text())
            ]
            self.save_to_json()
        dialog.destroy()

    def _delete_player_and_close_dialog(self, dialog, path):
        tree_iter = self.liststore.get_iter(path)
        self.liststore.remove(tree_iter)
        self.save_to_json()
        dialog.destroy()

    # Sprawdzanie czy wpisana jest liczba
    def on_numeric_input(self, entry):
        text = entry.get_text()
        if not text.isdigit():
            entry.set_text("".join(filter(str.isdigit, text)))

# Generowanie przykładowego pliku JSON jeśli nie istnieje
def generate_example_json(filepath):
    example_data = [{"name": "Gracz", "points": 250, "min_points": 0, "races": 0}]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(example_data, f, ensure_ascii=False, indent=2)

# Główna pętla programu
def main():
    json_path = DBPath
    if not os.path.isfile(json_path):
        generate_example_json(json_path)
    players = load_players_from_json(json_path)
    win = PlayerTable(players, json_path) # Utworzenie głównego okna
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()