import json
import gi
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class Player:
    def __init__(self, name, points, min_points, outcome, is_placement):
        self.name = name
        self.points = points
        self.min_points = min_points
        self.outcome = outcome
        self.is_placement = is_placement
        self.points_after = points

RankNames = ["Drewno 1", "Drewno 2", "Drewno 3", "Brąz 1", "Brąz 2", "Brąz 3",
    "Srebro 1", "Srebro 2", "Srebro 3", "Złoto 1", "Złoto 2", "Złoto 3",
    "Platyna 1", "Platyna 2", "Platyna 3", "Szmaragd 1", "Szmaragd 2", "Szmaragd 3",
    "Diament 1", "Diament 2", "Diament 3", "Szafir 1", "Szafir 2", "Szafir 3",
    "Rubin 1", "Rubin 2", "Rubin 3", "Legenda"]
RankThresholds = [0,75,150,250,325,400,
    525,625,725,875,1000,1125,
    1300,1450,1600,1800,1975,2150,
    2375,2575,2775,3050,3325,3625,
    3950,4400,5000,999999]
Shields = [0.1,0.1,0.1,0.2,0.2,0.2,
    0.3,0.3,0.3,0.4,0.4,0.4,
    0.5,0.5,0.5,0.6,0.6,0.6,
    0.7,0.7,0.7,0.8,0.8,0.8,
    0.9,0.9,0.9,1.0]
WorseWin = [50,46,42,39,36,33,31,29,27,26,25]
BetterWin = [50,55,60,65,70,75,85,95,105,115,125]
BetterLose = [-50,-55,-60,-65,-70,-75,-85,-95,-105,-115,-125]
WorseLose = [-50,-45,-40,-35,-30,-25,-22,-19,-16,-13,-10]
DBPath = "/mnt/share/STREAM/liga.json"
multiplier = 1

def get_player_rank(points):
    for i, threshold in enumerate(RankThresholds):
        if points < threshold:
            return i
    return len(RankThresholds) - 1

def calculate_points(players, racers, multiplier):
    #print("// Obliczenia //")
    for player in players:
        my_rank = get_player_rank(player.points)
        if player.outcome == 0 and not player.is_placement:
            if my_rank <= 6:
                player.points_after = player.points - 1
            elif my_rank > 6 and my_rank <= 12:
                player.points_after = player.points - 2
            elif my_rank > 12 and my_rank <= 18:
                player.points_after = player.points - 3
            elif my_rank > 18 and my_rank <= 24:
                player.points_after = player.points - 4
            elif my_rank > 24 and my_rank <= 28:
                player.points_after = player.points - 5
            if player.points_after < 0:
                player.points_after = 0
            if player.points_after < player.min_points:
                player.points_after = player.min_points
        elif player.outcome == 0 and player.is_placement:
            player.points_after = player.points
        else:
            change = 0
            for opponent in players:
                if player.outcome < opponent.outcome and opponent.outcome != 0:
                    his_rank = get_player_rank(opponent.points)
                    rankdiff = abs(his_rank - my_rank)
                    if rankdiff >= 10:
                        rankdiff = 10
                    if my_rank < his_rank:
                        change += BetterWin[rankdiff]
                        #print(f"{player.name} pokonał {opponent.name}. {rankdiff} lvl różnicy, +{BetterWin[rankdiff]}pp")
                    else:
                        change += WorseWin[rankdiff]
                        #print(f"{player.name} pokonał {opponent.name}. {rankdiff} lvl różnicy, +{WorseWin[rankdiff]}pp")
                elif player.outcome > opponent.outcome and opponent.outcome != 0:
                    his_rank = get_player_rank(opponent.points)
                    rankdiff = abs(his_rank - my_rank)
                    if rankdiff >= 10:
                        rankdiff = 10
                    if my_rank < his_rank:
                        change += WorseLose[rankdiff]
                        #print(f"{player.name} przegrał z {opponent.name}. {rankdiff} lvl różnicy, {WorseLose[rankdiff]}pp")
                    else:
                        change += BetterLose[rankdiff]
                        #print(f"{player.name} przegrał z {opponent.name}. {rankdiff} lvl różnicy, {BetterLose[rankdiff]}pp")
            if racers > 1:
                change /= (racers - 1)
            change *= multiplier
            if player.is_placement:
                change *= 2
            if change < 0 and not player.is_placement:
                change = change * Shields[my_rank - 1]
            changeint = int(change // 1)
            player.points_after = player.points + changeint
            if player.points_after < 0:
                player.points_after = 0
            if player.points_after < player.min_points:
                player.points_after = player.min_points
            #if change > 0:
                #print(f"{player.name} zdobył {changeint} pp")
            #elif change < 0:
                #print(f"{player.name} stracił {changeint} pp")

def print_results(players):
    #print("")
    #print("// Ranking po wyścigu //")
    for player in players:
        rank = get_player_rank(player.points_after)
        needed = RankThresholds[rank] - player.points_after
        difference = player.points_after - player.points
        diff_str = f"+{difference}pp" if difference >= 0 else f"{difference}pp"
        #print(f"[{RankNames[rank - 1]}] {player.name}    {player.points_after}pp ({diff_str}).    Awans za {needed}pp")

def load_players_from_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    players = []
    for entry in data:
        players.append(Player(
            entry["name"],
            entry["points"],
            entry["min_points"],
            entry["outcome"],
            entry["is_placement"]
        ))
    return players

def show_file_not_found_dialog(parent):
    dialog = Gtk.MessageDialog(
        parent,
        0,
        Gtk.MessageType.ERROR,
        Gtk.ButtonsType.OK,
        "Nie znaleziono pliku JSON!"
    )
    dialog.format_secondary_text(
        "Wybierz plik JSON ręcznie."
    )
    dialog.run()
    dialog.destroy()

def pick_json_file():
    import subprocess
    try:
        result = subprocess.run(
            ["xdg-file-picker", "--file", "--mime-type", "application/json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        path = result.stdout.strip()
        if path and os.path.isfile(path):
            return path
    except Exception:
        pass
    return None

class OutcomeEditDialog(Gtk.Dialog):
    def __init__(self, parent, players, current_multiplier):
        Gtk.Dialog.__init__(self, "Rejestracja nowego wyścigu", parent, 0)
        self.set_default_size(700, 400)
        self.players = players
        box = self.get_content_area()
        self.entries = []
        self.multiplier = current_multiplier

        count = len(players)
        columns = 1
        if count > 8 and count <= 16:
            columns = 2

        grid = Gtk.Grid(column_spacing=4, row_spacing=4)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)

        if count > 16:
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_height(350)
            scrolled.add(grid)
            box.pack_start(scrolled, True, True, 0)
        else:
            box.pack_start(grid, True, True, 0)

        for idx, player in enumerate(players):
            col = idx % columns
            row = idx // columns
            label = Gtk.Label(label=player.name)
            entry = Gtk.SpinButton()
            entry.set_range(0, 100)
            entry.set_increments(1, 5)
            entry.set_value(player.outcome)
            grid.attach(label, col * 2, row, 1, 1)
            grid.attach(entry, col * 2 + 1, row, 1, 1)
            self.entries.append(entry)

        # Multiplier control at the bottom left
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        multiplier_label = Gtk.Label(label="Mnożnik:")
        self.multiplier_spin = Gtk.SpinButton()
        self.multiplier_spin.set_range(1, 5)
        self.multiplier_spin.set_increments(1, 1)
        self.multiplier_spin.set_value(current_multiplier)
        hbox.pack_start(multiplier_label, False, False, 0)
        hbox.pack_start(self.multiplier_spin, False, False, 0)
        box.pack_start(hbox, False, False, 10)

        self.add_button("OK", Gtk.ResponseType.OK)
        self.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        self.show_all()

    def get_outcomes(self):
        return [entry.get_value_as_int() for entry in self.entries]

    def get_multiplier(self):
        return self.multiplier_spin.get_value_as_int()

class ResultSimulationDialog(Gtk.Dialog):
    def __init__(self, parent, players, multiplier):
        Gtk.Dialog.__init__(self, "Symulacja wyników", parent, 0)
        self.set_default_size(700, 400)
        box = self.get_content_area()

        # Calculate results
        racers = sum(1 for p in players if p.outcome > 0)
        calculate_points(players, racers, multiplier)

        # Prepare grid for results
        grid = Gtk.Grid(column_spacing=6, row_spacing=6)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        box.pack_start(grid, True, True, 0)

        # Header
        headers = ["Nick", "Nowa ranga", "Nowe punkty", "Zmiana punktów"]
        for col, header in enumerate(headers):
            grid.attach(Gtk.Label(label=f"<b>{header}</b>", use_markup=True), col, 0, 1, 1)

        # Fill rows
        for idx, player in enumerate(players):
            rank = get_player_rank(player.points_after)
            rank_name = RankNames[rank-1]
            diff = player.points_after - player.points
            diff_str = f"+{diff}" if diff >= 0 else str(diff)
            grid.attach(Gtk.Label(label=player.name), 0, idx+1, 1, 1)
            grid.attach(Gtk.Label(label=rank_name), 1, idx+1, 1, 1)
            grid.attach(Gtk.Label(label=str(player.points_after)), 2, idx+1, 1, 1)
            grid.attach(Gtk.Label(label=diff_str), 3, idx+1, 1, 1)

        # Buttons
        self.add_button("Zapisz do JSON", Gtk.ResponseType.OK)
        self.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        self.show_all()

class AddPlayerDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Dodaj nowego gracza", parent, 0)
        self.set_default_size(300, 100)
        box = self.get_content_area()

        name_label = Gtk.Label(label="Nick:")
        self.name_entry = Gtk.Entry()
        self.name_entry.set_activates_default(True)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.attach(name_label, 0, 0, 1, 1)
        grid.attach(self.name_entry, 1, 0, 1, 1)
        box.pack_start(grid, True, True, 10)

        self.add_button("Dodaj", Gtk.ResponseType.OK)
        self.add_button("Anuluj", Gtk.ResponseType.CANCEL)
        self.set_default_response(Gtk.ResponseType.OK)
        self.show_all()

    def get_player_name(self):
        return self.name_entry.get_text().strip()

class PlayerTable(Gtk.Window):
    def __init__(self, players, json_path):
        Gtk.Window.__init__(self, title="Poważny ranking")
        self.set_default_size(400, 500)
        self.players = players
        self.json_path = json_path
        self.multiplier = 1

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Create ListStore for player data (add rank_name column)
        self.liststore = Gtk.ListStore(str, int, int, bool, str)
        for p in self.players:
            rank_name = RankNames[get_player_rank(p.points)-1]
            self.liststore.append([p.name, p.points, p.min_points, p.is_placement, rank_name])

        # Create TreeView (add rank column)
        treeview = Gtk.TreeView(model=self.liststore)
        columns = [
            ("Nick", 0, Gtk.CellRendererText(), "text"),
            ("Punkty", 1, Gtk.CellRendererText(), "text"),
            ("Minimum", 2, Gtk.CellRendererText(), "text"),
            ("Placementy", 3, Gtk.CellRendererToggle(), "active"),
            ("Ranga", 4, Gtk.CellRendererText(), "text")
        ]
        for col_title, col_idx, renderer, prop in columns:
            column = Gtk.TreeViewColumn(col_title, renderer, **{prop: col_idx})
            treeview.append_column(column)

        vbox.pack_start(treeview, True, True, 0)

        # New Race button
        button = Gtk.Button(label="Nowy wyścig")
        button.connect("clicked", self.on_new_race_clicked)
        vbox.pack_start(button, False, False, 0)

        # Add New Player button
        add_button = Gtk.Button(label="Dodaj nowego gracza")
        add_button.connect("clicked", self.on_add_player_clicked)
        vbox.pack_start(add_button, False, False, 0)

    def on_outcome_edited(self, widget, path, value, col):
        value = int(float(value))
        self.liststore[path][col] = value

    def on_new_race_clicked(self, button):
        dialog = OutcomeEditDialog(self, self.players, self.multiplier)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            outcomes = dialog.get_outcomes()
            self.multiplier = dialog.get_multiplier()
            for i, player in enumerate(self.players):
                player.outcome = outcomes[i]
            # Update rank column if points changed
            for i, row in enumerate(self.liststore):
                row[4] = RankNames[get_player_rank(row[1])-1]
            dialog.destroy()

            # Show result simulation popup
            sim_dialog = ResultSimulationDialog(self, self.players, self.multiplier)
            sim_response = sim_dialog.run()
            if sim_response == Gtk.ResponseType.OK:
                # Save outcomes and new points to JSON
                data = []
                for i, row in enumerate(self.liststore):
                    data.append({
                        "name": row[0],
                        "points": self.players[i].points_after,
                        "min_points": row[2],
                        "outcome": 0,  # Reset outcome after saving
                        "is_placement": row[3]
                    })
                    # Update points in table for next race
                    row[1] = self.players[i].points_after
                    row[4] = RankNames[get_player_rank(row[1])-1]
                    self.players[i].points = self.players[i].points_after
                    self.players[i].outcome = 0  # Reset outcome in memory
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # Abandon changes, restore points and outcomes
                for i, player in enumerate(self.players):
                    player.outcome = 0
                    player.points_after = player.points
            sim_dialog.destroy()
        else:
            dialog.destroy()

    def on_add_player_clicked(self, button):
        dialog = AddPlayerDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.get_player_name()
            if name:
                # Add new player to data
                new_player = Player(name, 250, 0, 0, True)
                self.players.append(new_player)
                rank_name = RankNames[get_player_rank(new_player.points)-1]
                self.liststore.append([new_player.name, new_player.points, new_player.min_points, new_player.is_placement, rank_name])
                # Save to JSON
                data = []
                for i, row in enumerate(self.liststore):
                    data.append({
                        "name": row[0],
                        "points": row[1],
                        "min_points": row[2],
                        "outcome": self.players[i].outcome,
                        "is_placement": row[3]
                    })
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        dialog.destroy()

def main():
    json_path = DBPath
    players = None
    if not os.path.isfile(json_path):
        # Show popup and let user pick file
        win = Gtk.Window(title="Ranking Liga")
        win.set_default_size(250, 100)
        show_file_not_found_dialog(win)
        json_path = pick_json_file()
        if not json_path or not os.path.isfile(json_path):
            # Show error and exit
            err_dialog = Gtk.MessageDialog(
                win,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.CLOSE,
                "Nie wybrano pliku JSON. Program zostanie zamknięty."
            )
            err_dialog.run()
            err_dialog.destroy()
            return
    players = load_players_from_json(json_path)
    racers = sum(1 for p in players if p.outcome > 0)
    calculate_points(players, racers, multiplier)
    print_results(players)

    win = PlayerTable(players, json_path)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
