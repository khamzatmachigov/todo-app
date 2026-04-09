import tkinter as tk
from tkinter import messagebox
import json
import os

DATEI = "aufgaben.json"

def aufgaben_laden():
    """Aufgaben aus der JSON-Datei laden."""
    if os.path.exists(DATEI):
        with open(DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def aufgaben_speichern(aufgaben):
    """Aufgaben in die JSON-Datei speichern."""
    with open(DATEI, "w", encoding="utf-8") as f:
        json.dump(aufgaben, f, ensure_ascii=False, indent=2)

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meine To-do-Liste")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Aufgaben als Liste von Dicts: {"text": ..., "erledigt": True/False}
        self.aufgaben = aufgaben_laden()

        self._ui_aufbauen()
        self._liste_aktualisieren()

    def _ui_aufbauen(self):
        """Alle UI-Elemente erstellen."""

        # --- Titel ---
        titel = tk.Label(
            self.root,
            text="To-do-Liste",
            font=("Helvetica", 22, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        )
        titel.pack(pady=(24, 8))

        untertitel = tk.Label(
            self.root,
            text="Deine Aufgaben im Überblick",
            font=("Helvetica", 11),
            bg="#1e1e2e",
            fg="#6c7086"
        )
        untertitel.pack()

        # --- Eingabebereich ---
        eingabe_frame = tk.Frame(self.root, bg="#1e1e2e")
        eingabe_frame.pack(fill="x", padx=24, pady=16)

        self.eingabe = tk.Entry(
            eingabe_frame,
            font=("Helvetica", 13),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            bd=0
        )
        self.eingabe.pack(side="left", fill="x", expand=True, ipady=10, ipadx=10)
        self.eingabe.bind("<Return>", lambda e: self.aufgabe_hinzufuegen())

        hinzufuegen_btn = tk.Button(
            eingabe_frame,
            text="+ Hinzufügen",
            font=("Helvetica", 12, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="#1e1e2e",
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2",
            command=self.aufgabe_hinzufuegen
        )
        hinzufuegen_btn.pack(side="left", padx=(8, 0))

        # --- Filter-Buttons ---
        filter_frame = tk.Frame(self.root, bg="#1e1e2e")
        filter_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.filter_var = tk.StringVar(value="alle")

        for text, wert in [("Alle", "alle"), ("Offen", "offen"), ("Erledigt", "erledigt")]:
            btn = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=wert,
                font=("Helvetica", 11),
                bg="#1e1e2e",
                fg="#a6adc8",
                selectcolor="#313244",
                activebackground="#1e1e2e",
                activeforeground="#cdd6f4",
                cursor="hand2",
                command=self._liste_aktualisieren
            )
            btn.pack(side="left", padx=(0, 12))

        # --- Aufgabenliste (Canvas + Scrollbar) ---
        liste_frame = tk.Frame(self.root, bg="#1e1e2e")
        liste_frame.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.canvas = tk.Canvas(liste_frame, bg="#1e1e2e", highlightthickness=0)
        scrollbar = tk.Scrollbar(liste_frame, orient="vertical", command=self.canvas.yview)

        self.scroll_frame = tk.Frame(self.canvas, bg="#1e1e2e")
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mausrad scrollen
        self.canvas.bind_all("<MouseWheel>", self._mausrad_scrollen)

        # --- Statuszeile ---
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 10),
            bg="#1e1e2e",
            fg="#6c7086"
        )
        self.status_label.pack(pady=(0, 16))

    def _mausrad_scrollen(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def aufgabe_hinzufuegen(self):
        """Neue Aufgabe aus dem Eingabefeld hinzufügen."""
        text = self.eingabe.get().strip()
        if not text:
            messagebox.showwarning("Hinweis", "Bitte eine Aufgabe eingeben!")
            return

        self.aufgaben.append({"text": text, "erledigt": False})
        aufgaben_speichern(self.aufgaben)
        self.eingabe.delete(0, tk.END)
        self._liste_aktualisieren()

    def aufgabe_umschalten(self, index):
        """Aufgabe als erledigt / offen markieren."""
        self.aufgaben[index]["erledigt"] = not self.aufgaben[index]["erledigt"]
        aufgaben_speichern(self.aufgaben)
        self._liste_aktualisieren()

    def aufgabe_loeschen(self, index):
        """Aufgabe löschen (mit Bestätigungsdialog)."""
        antwort = messagebox.askyesno(
            "Löschen?",
            f'Aufgabe "{self.aufgaben[index]["text"]}" wirklich löschen?'
        )
        if antwort:
            self.aufgaben.pop(index)
            aufgaben_speichern(self.aufgaben)
            self._liste_aktualisieren()

    def _liste_aktualisieren(self):
        """Aufgabenliste neu aufbauen (nach Filter)."""
        # Alte Einträge entfernen
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        filter_wert = self.filter_var.get()

        # Gefilterte Einträge mit Original-Index
        sichtbare = []
        for i, aufgabe in enumerate(self.aufgaben):
            if filter_wert == "alle":
                sichtbare.append((i, aufgabe))
            elif filter_wert == "offen" and not aufgabe["erledigt"]:
                sichtbare.append((i, aufgabe))
            elif filter_wert == "erledigt" and aufgabe["erledigt"]:
                sichtbare.append((i, aufgabe))

        if not sichtbare:
            leer_label = tk.Label(
                self.scroll_frame,
                text="Keine Aufgaben vorhanden",
                font=("Helvetica", 12),
                bg="#1e1e2e",
                fg="#585b70"
            )
            leer_label.pack(pady=30)
        else:
            for orig_index, aufgabe in sichtbare:
                self._aufgaben_zeile(orig_index, aufgabe)

        # Statuszeile aktualisieren
        gesamt = len(self.aufgaben)
        erledigt = sum(1 for a in self.aufgaben if a["erledigt"])
        self.status_label.config(
            text=f"{erledigt} von {gesamt} Aufgaben erledigt"
        )

    def _aufgaben_zeile(self, index, aufgabe):
        """Eine einzelne Aufgaben-Zeile erstellen."""
        bg_farbe = "#313244" if not aufgabe["erledigt"] else "#1e1e2e"
        text_farbe = "#cdd6f4" if not aufgabe["erledigt"] else "#585b70"

        zeile = tk.Frame(
            self.scroll_frame,
            bg=bg_farbe,
            pady=2
        )
        zeile.pack(fill="x", pady=4, padx=2)

        # Checkbox
        var = tk.BooleanVar(value=aufgabe["erledigt"])
        checkbox = tk.Checkbutton(
            zeile,
            variable=var,
            bg=bg_farbe,
            activebackground=bg_farbe,
            fg="#89b4fa",
            selectcolor="#313244",
            cursor="hand2",
            command=lambda i=index: self.aufgabe_umschalten(i)
        )
        checkbox.pack(side="left", padx=(8, 0))

        # Aufgabentext
        font_stil = ("Helvetica", 12, "overstrike") if aufgabe["erledigt"] else ("Helvetica", 12)
        text_label = tk.Label(
            zeile,
            text=aufgabe["text"],
            font=font_stil,
            bg=bg_farbe,
            fg=text_farbe,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=8, pady=10)

        # Löschen-Button
        loeschen_btn = tk.Button(
            zeile,
            text="✕",
            font=("Helvetica", 11),
            bg=bg_farbe,
            fg="#f38ba8",
            activebackground=bg_farbe,
            activeforeground="#f38ba8",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda i=index: self.aufgabe_loeschen(i)
        )
        loeschen_btn.pack(side="right", padx=8)


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
