import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os

DB_FILE = 'games_db.json'

DARK_BG = '#181a1b'
DARK_PANEL = '#23272a'
DARK_ROW1 = '#23272a'
DARK_ROW2 = '#202225'
DARK_TEXT = '#f1f1f1'
DARK_HEADING = '#00bcd4'
DARK_BTN = '#2d333b'
DARK_BTN_HOVER = '#00bcd4'

class GameManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Manajemen Game HDD')
        self.geometry('800x550')
        self.resizable(False, False)
        self.configure(bg=DARK_BG)
        self.set_theme()
        self.hdds = []
        self.games = []
        self.create_widgets()
        self.load_game_data()

    def set_theme(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=DARK_PANEL)
        style.configure('TLabel', background=DARK_BG, foreground=DARK_TEXT, font=('Segoe UI', 11))
        style.configure('Treeview',
                        font=('Segoe UI', 11),
                        rowheight=28,
                        background=DARK_ROW1,
                        fieldbackground=DARK_ROW1,
                        foreground=DARK_TEXT,
                        bordercolor='#222',
                        borderwidth=1)
        style.configure('TEntry', fieldbackground=DARK_PANEL, foreground=DARK_TEXT, background=DARK_PANEL, bordercolor=DARK_HEADING)
        style.configure('TMenubutton', background=DARK_PANEL, foreground=DARK_TEXT)

    def create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self, bg=DARK_PANEL, fg=DARK_TEXT, activebackground=DARK_HEADING, activeforeground=DARK_BG, bd=0, relief='flat')
        kelola_menu = tk.Menu(menubar, tearoff=0, bg=DARK_PANEL, fg=DARK_TEXT, activebackground=DARK_HEADING, activeforeground=DARK_BG)
        kelola_menu.add_command(label='Kelola HDD & Game', command=self.open_manage_window)
        menubar.add_cascade(label='Kelola', menu=kelola_menu)
        self.config(menu=menubar)

        # Header
        title = ttk.Label(self, text='Manajemen Game HDD', font=('Segoe UI', 22, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        title.pack(pady=(28, 10))

        # Frame utama horizontal
        main_frame = ttk.Frame(self, padding=10, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 20))
        # Frame Customer (kiri)
        customer_frame = ttk.Frame(main_frame, style='TFrame')
        customer_frame.pack(side='left', fill='both', expand=True, padx=(0, 8))
        search_frame = ttk.Frame(customer_frame, padding=10, style='TFrame')
        search_frame.pack()
        self.search_text = tk.Text(search_frame, width=38, height=6, relief='flat', borderwidth=2)
        self.search_text.configure(font=('Segoe UI', 12), bg=DARK_PANEL, fg=DARK_TEXT, insertbackground=DARK_HEADING)
        self.search_text.pack(side='left', padx=(0, 10), ipady=4)
        search_btn = ttk.Button(search_frame, text='Cari', command=self.search_games, width=10, style='TButton')
        search_btn.pack(side='left')
        info = ttk.Label(customer_frame, text='Masukkan nama game customer (bisa copy-paste list, pisahkan dengan enter/koma/tab)', font=('Segoe UI', 10), background=DARK_BG, foreground='#b0b0b0')
        info.pack(pady=(0, 8))
        self.result_frame = ttk.Frame(customer_frame, padding=10, style='TFrame')
        self.result_frame.pack(fill='both', expand=True)
        self.result_tree = ttk.Treeview(self.result_frame, columns=('No', 'Game', 'HDD', 'Status'), show='headings', height=14, style='Treeview')
        self.result_tree.heading('No', text='No')
        self.result_tree.heading('Game', text='Nama Game')
        self.result_tree.heading('HDD', text='HDD')
        self.result_tree.heading('Status', text='Status')
        self.result_tree.column('No', width=40, anchor='center')
        self.result_tree.column('Game', width=320, anchor='w')
        self.result_tree.column('HDD', width=200, anchor='center')
        self.result_tree.column('Status', width=100, anchor='center')
        self.result_tree.pack(fill='both', expand=True, side='left')
        self.result_tree.tag_configure('oddrow', background=DARK_ROW2, foreground=DARK_TEXT)
        self.result_tree.tag_configure('evenrow', background=DARK_ROW1, foreground=DARK_TEXT)
        scrollbar = ttk.Scrollbar(self.result_frame, orient='vertical', command=self.result_tree.yview)
        self.result_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        # Frame List Game (kanan)
        list_frame = ttk.Frame(main_frame, style='TFrame')
        list_frame.pack(side='left', fill='both', expand=True, padx=(8, 0))
        list_info = ttk.Label(list_frame, text='List game yang tersedia di database:', font=('Segoe UI', 10), background=DARK_BG, foreground='#b0b0b0')
        list_info.pack(pady=(10, 8))
        self.list_frame = ttk.Frame(list_frame, padding=10, style='TFrame')
        self.list_frame.pack(fill='both', expand=True)
        self.list_tree = ttk.Treeview(self.list_frame, columns=('No', 'Game', 'HDD'), show='headings', height=18, style='Treeview')
        self.list_tree.heading('No', text='No')
        self.list_tree.heading('Game', text='Nama Game')
        self.list_tree.heading('HDD', text='HDD')
        self.list_tree.column('No', width=40, anchor='center')
        self.list_tree.column('Game', width=320, anchor='w')
        self.list_tree.column('HDD', width=200, anchor='center')
        self.list_tree.pack(fill='both', expand=True, side='left')
        self.list_tree.tag_configure('oddrow', background=DARK_ROW2, foreground=DARK_TEXT)
        self.list_tree.tag_configure('evenrow', background=DARK_ROW1, foreground=DARK_TEXT)
        list_scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.list_tree.yview)
        self.list_tree.configure(yscroll=list_scrollbar.set)
        list_scrollbar.pack(side='right', fill='y')
        self.refresh_list_game()

    def open_manage_window(self):
        ManageWindow(self)

    def search_games(self):
        import re
        raw_input = self.search_text.get('1.0', 'end').strip()
        lines = []
        for part in raw_input.split('\n'):
            for subpart in part.split(','):
                for subsub in subpart.split('\t'):
                    lines.append(subsub.strip())
        input_games = []
        for line in lines:
            if not line:
                continue
            if line[0].isdigit():
                line = line.lstrip('0123456789.\t- ').strip()
            if line:
                input_games.append(line)
        self.result_tree.delete(*self.result_tree.get_children())
        if not input_games:
            sorted_games = sorted(self.games, key=lambda g: g['name'].lower())
            for idx, g in enumerate(sorted_games):
                hdd_name = self.get_hdd_name(g['hdd_id'])
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.result_tree.insert('', 'end', values=(idx+1, g['name'], hdd_name, 'ADA'), tags=(tag,))
            return
        row_idx = 0
        for i, game in enumerate(input_games):
            game_words = set(re.findall(r'\w+', game.lower()))
            best_matches = []
            best_score = 0
            for g in self.games:
                db_words = set(re.findall(r'\w+', g['name'].lower()))
                if not game_words:
                    continue
                overlap = len(game_words & db_words)
                score = overlap / max(len(game_words), 1)
                if score > best_score:
                    best_score = score
                    best_matches = [g]
                elif score == best_score and score > 0:
                    best_matches.append(g)
            # Threshold: minimal 85% kata sama
            if best_score >= 0.85:
                for g in best_matches:
                    hdd_name = self.get_hdd_name(g['hdd_id'])
                    tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                    self.result_tree.insert('', 'end', values=(i+1, g['name'], hdd_name, 'ADA'), tags=(tag,))
                    row_idx += 1
            else:
                tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                self.result_tree.insert('', 'end', values=(i+1, game, '-', 'TIDAK ADA'), tags=(tag,))
                row_idx += 1

    def refresh_list_game(self):
        self.list_tree.delete(*self.list_tree.get_children())
        sorted_games = sorted(self.games, key=lambda g: g['name'].lower())
        for idx, g in enumerate(sorted_games):
            hdd_name = self.get_hdd_name(g['hdd_id'])
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.list_tree.insert('', 'end', values=(idx+1, g['name'], hdd_name), tags=(tag,))

    def get_hdd_name(self, hdd_id):
        for h in self.hdds:
            if h['id'] == hdd_id:
                return h['name']
        return '-'

    def load_game_data(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.hdds = data.get('hdds', [])
                self.games = data.get('games', [])
        else:
            self.hdds = []
            self.games = []

    def save_game_data(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({'hdds': self.hdds, 'games': self.games}, f, ensure_ascii=False, indent=2)

class ManageWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Kelola HDD & Game')
        self.geometry('700x420')
        self.resizable(False, False)
        self.configure(bg=DARK_BG)
        self.master = master
        self.selected_hdd_id = None
        self.create_widgets()
        self.refresh_hdd_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        # Daftar HDD
        hdd_frame = ttk.Frame(main_frame, style='TFrame')
        hdd_frame.grid(row=0, column=0, sticky='ns', padx=(0,16))
        ttk.Label(hdd_frame, text='Daftar HDD', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING).grid(row=0, column=0, pady=(2,4))
        self.hdd_listbox = tk.Listbox(hdd_frame, width=25, height=16, font=('Segoe UI', 11), bg=DARK_ROW1, fg=DARK_TEXT, selectbackground=DARK_HEADING, selectforeground=DARK_BG, highlightbackground=DARK_PANEL, relief='flat', borderwidth=0)
        self.hdd_listbox.grid(row=1, column=0, sticky='nsew')
        self.hdd_listbox.bind('<<ListboxSelect>>', self.on_hdd_select)
        btn_hdd_frame = ttk.Frame(hdd_frame, style='TFrame')
        btn_hdd_frame.grid(row=2, column=0, pady=(8,0))
        ttk.Button(btn_hdd_frame, text='Tambah', width=8, command=self.add_hdd, style='TButton').pack(side='left', padx=2)
        ttk.Button(btn_hdd_frame, text='Edit', width=8, command=self.edit_hdd, style='TButton').pack(side='left', padx=2)
        ttk.Button(btn_hdd_frame, text='Hapus', width=8, command=self.delete_hdd, style='TButton').pack(side='left', padx=2)
        hdd_frame.grid_rowconfigure(1, weight=1)
        hdd_frame.grid_columnconfigure(0, weight=1)
        # Daftar Game
        game_frame = ttk.Frame(main_frame, style='TFrame')
        game_frame.grid(row=0, column=1, sticky='ns')
        ttk.Label(game_frame, text='Daftar Game di HDD', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING).grid(row=0, column=0, pady=(2,4))
        self.game_listbox = tk.Listbox(game_frame, width=40, height=16, font=('Segoe UI', 11), bg=DARK_ROW1, fg=DARK_TEXT, selectbackground=DARK_HEADING, selectforeground=DARK_BG, highlightbackground=DARK_PANEL, relief='flat', borderwidth=0)
        self.game_listbox.grid(row=1, column=0, sticky='nsew')
        btn_game_frame = ttk.Frame(game_frame, style='TFrame')
        btn_game_frame.grid(row=2, column=0, pady=(8,0))
        ttk.Button(btn_game_frame, text='Tambah', width=8, command=self.add_game, style='TButton').pack(side='left', padx=2)
        ttk.Button(btn_game_frame, text='Edit', width=8, command=self.edit_game, style='TButton').pack(side='left', padx=2)
        ttk.Button(btn_game_frame, text='Hapus', width=8, command=self.delete_game, style='TButton').pack(side='left', padx=2)
        ttk.Button(btn_game_frame, text='Scan Folder', width=12, command=self.scan_folder, style='TButton').pack(side='left', padx=8)
        game_frame.grid_rowconfigure(1, weight=1)
        game_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def refresh_hdd_list(self):
        self.hdd_listbox.delete(0, tk.END)
        for hdd in self.master.hdds:
            self.hdd_listbox.insert(tk.END, hdd['name'])
        self.selected_hdd_id = None
        self.refresh_game_list()

    def on_hdd_select(self, event=None):
        idx = self.hdd_listbox.curselection()
        if idx:
            hdd = self.master.hdds[idx[0]]
            self.selected_hdd_id = hdd['id']
        else:
            self.selected_hdd_id = None
        self.refresh_game_list()

    def refresh_game_list(self):
        self.game_listbox.delete(0, tk.END)
        if not self.selected_hdd_id:
            return
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        games = sorted(games, key=lambda g: g['name'].lower())
        for game in games:
            self.game_listbox.insert(tk.END, game['name'])

    def add_hdd(self):
        name = simpledialog.askstring('Tambah HDD', 'Nama HDD:')
        if name:
            hdd_id = self._generate_id()
            self.master.hdds.append({'id': hdd_id, 'name': name})
            self.master.save_game_data()
            self.refresh_hdd_list()

    def edit_hdd(self):
        idx = self.hdd_listbox.curselection()
        if not idx:
            return
        hdd = self.master.hdds[idx[0]]
        name = simpledialog.askstring('Edit HDD', 'Nama HDD:', initialvalue=hdd['name'])
        if name:
            hdd['name'] = name
            self.master.save_game_data()
            self.refresh_hdd_list()

    def delete_hdd(self):
        idx = self.hdd_listbox.curselection()
        if not idx:
            return
        hdd = self.master.hdds[idx[0]]
        if messagebox.askyesno('Konfirmasi', f'Hapus HDD "{hdd['name']}" dan semua game di dalamnya?'):
            self.master.hdds.pop(idx[0])
            self.master.games = [g for g in self.master.games if g['hdd_id'] != hdd['id']]
            self.master.save_game_data()
            self.refresh_hdd_list()

    def add_game(self):
        if not self.selected_hdd_id:
            messagebox.showinfo('Info', 'Pilih HDD terlebih dahulu.')
            return
        name = simpledialog.askstring('Tambah Game', 'Nama Game:')
        if name:
            self.master.games.append({'name': name, 'hdd_id': self.selected_hdd_id})
            self.master.save_game_data()
            self.refresh_game_list()

    def edit_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        game = games[idx[0]]
        name = simpledialog.askstring('Edit Game', 'Nama Game:', initialvalue=game['name'])
        if name:
            game['name'] = name
            self.master.save_game_data()
            self.refresh_game_list()

    def delete_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        game = games[idx[0]]
        if messagebox.askyesno('Konfirmasi', f'Hapus game "{game['name']}"?'):
            self.master.games.remove(game)
            self.master.save_game_data()
            self.refresh_game_list()

    def scan_folder(self):
        if not self.selected_hdd_id:
            if len(self.master.hdds) == 1:
                self.selected_hdd_id = self.master.hdds[0]['id']
                self.hdd_listbox.selection_set(0)
            else:
                self.on_hdd_select()
        if not self.selected_hdd_id:
            messagebox.showinfo('Info', 'Pilih HDD terlebih dahulu.')
            return
        folder = filedialog.askdirectory(title='Pilih Folder HDD untuk Scan')
        if not folder:
            return
        try:
            subfolders = [f.name for f in os.scandir(folder) if f.is_dir()]
        except Exception as e:
            messagebox.showerror('Error', f'Gagal scan folder: {e}')
            return
        added = 0
        for name in subfolders:
            if not any(g['name'].lower() == name.lower() and g['hdd_id'] == self.selected_hdd_id for g in self.master.games):
                self.master.games.append({'name': name, 'hdd_id': self.selected_hdd_id})
                added += 1
        self.master.save_game_data()
        self.refresh_game_list()
        messagebox.showinfo('Scan Selesai', f'{added} game baru ditambahkan dari folder.')

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

if __name__ == '__main__':
    app = GameManagerApp()
    app.mainloop() 