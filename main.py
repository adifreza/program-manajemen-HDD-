import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import csv
from datetime import datetime

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
    def add_selected_to_table(self):
        messagebox.showinfo('Info', 'Fitur tambah ke tabel hanya tersedia di menu "Hitung Total Size Game".')
    
    def remove_selected_from_table(self):
        selected_items = self.selected_tree.selection()
        if not selected_items:
            messagebox.showinfo('Info', 'Pilih game dari tabel terlebih dahulu.')
            return
        
        for item in selected_items:
            values = self.selected_tree.item(item, 'values')
            game_name = values[1]  # Nama game ada di kolom kedua
            
            # Hapus dari treeview
            self.selected_tree.delete(item)
            
            # Hapus dari selected_games list
            self.selected_games = [g for g in self.selected_games if g['name'] != game_name]
        
        # Reorder nomor urut
        items = self.selected_tree.get_children()
        for i, item in enumerate(items):
            values = list(self.selected_tree.item(item, 'values'))
            values[0] = i + 1  # Update nomor urut
            self.selected_tree.item(item, values=values)
        
        self.update_total_size()

    def update_total_size(self):
        total = sum(game.get('size', 0) for game in self.selected_games)
        if total >= 1024**3:
            size_str = f"{total/(1024**3):.2f} GB"
        elif total >= 1024**2:
            size_str = f"{total/(1024**2):.2f} MB"
        elif total >= 1024:
            size_str = f"{total/1024:.2f} KB"
        else:
            size_str = f"{total} B"
        self.total_size_label.config(text=f'Total Size: {size_str}')

    def filter_game_list(self):
        search_text = self.search_var.get().strip().lower()
        self.game_listbox.delete(0, tk.END)
        filtered_games = [g for g in self.games if search_text in g['name'].lower()]
        for game in sorted(filtered_games, key=lambda g: g['name'].lower()):
            size_str = ''
            if 'size' in game:
                sz = game['size']
                if sz >= 1024**3:
                    size_str = f" ({sz/(1024**3):.2f} GB)"
                elif sz >= 1024**2:
                    size_str = f" ({sz/(1024**2):.2f} MB)"
                elif sz >= 1024:
                    size_str = f" ({sz/1024:.2f} KB)"
                else:
                    size_str = f" ({sz} B)"
            self.game_listbox.insert(tk.END, game['name'] + size_str)

    def reset_game_list(self):
        self.search_var.set('')
        self.refresh_game_list()

    def refresh_game_list(self):
        self.game_tree.delete(*self.game_tree.get_children())
        
        # Update HDD filter combo
        hdd_names = ['Semua HDD'] + [h['name'] for h in self.hdds]
        self.hdd_filter_combo['values'] = hdd_names
        
        # Filter games berdasarkan HDD dan search
        filtered_games = self.games.copy()
        
        # Filter berdasarkan HDD
        selected_hdd = self.hdd_filter_var.get()
        if selected_hdd and selected_hdd != 'Semua HDD':
            hdd_obj = next((h for h in self.hdds if h['name'] == selected_hdd), None)
            if hdd_obj:
                filtered_games = [g for g in filtered_games if g['hdd_id'] == hdd_obj['id']]
        
        # Filter berdasarkan search
        search_text = self.search_var.get().strip().lower()
        if search_text:
            filtered_games = [g for g in filtered_games if search_text in g['name'].lower()]
        
        # Sort games
        filtered_games = sorted(filtered_games, key=lambda g: g['name'].lower())
        
        # Insert ke treeview
        row_idx = 0
        total_size = 0
        for game in filtered_games:
            size_str = ''
            if 'size' in game:
                sz = game['size']
                total_size += sz
                if sz >= 1024**3:
                    size_str = f"{sz/(1024**3):.2f} GB"
                elif sz >= 1024**2:
                    size_str = f"{sz/(1024**2):.2f} MB"
                elif sz >= 1024:
                    size_str = f"{sz/1024:.2f} KB"
                else:
                    size_str = f"{sz} B"
            
            hdd_name = self.get_hdd_name(game['hdd_id'])
            tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
            self.game_tree.insert('', 'end', values=(row_idx + 1, game['name'], size_str, hdd_name), tags=(tag,))
            row_idx += 1
        
        # Update info labels
        self.total_games_label.config(text=f'Total Game: {len(filtered_games)}')
        
        if total_size >= 1024**3:
            total_size_str = f"{total_size/(1024**3):.2f} GB"
        elif total_size >= 1024**2:
            total_size_str = f"{total_size/(1024**2):.2f} MB"
        elif total_size >= 1024:
            total_size_str = f"{total_size/1024:.2f} KB"
        else:
            total_size_str = f"{total_size} B"
        self.total_size_label.config(text=f'Total Size: {total_size_str}')

    def __init__(self):
        super().__init__()
        self.title('Manajemen Game HDD')
        self.geometry('1100x600')
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
        kelola_menu.add_command(label='Scan Folder', command=self.scan_folder)
        kelola_menu.add_command(label='Hitung Total Size Game', command=self.open_size_window)
        menubar.add_cascade(label='Kelola', menu=kelola_menu)
        
        export_menu = tk.Menu(menubar, tearoff=0, bg=DARK_PANEL, fg=DARK_TEXT, activebackground=DARK_HEADING, activeforeground=DARK_BG)
        export_menu.add_command(label='Ekspor Semua Game ke Excel', command=self.export_all_games_to_excel)
        export_menu.add_command(label='Ekspor Game Terfilter ke Excel', command=self.export_filtered_games_to_excel)
        menubar.add_cascade(label='Ekspor', menu=export_menu)
        
        self.config(menu=menubar)

        # Header
        title = ttk.Label(self, text='Manajemen Game HDD', font=('Segoe UI', 22, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        title.pack(pady=(28, 10))

        # Frame utama
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Frame untuk kontrol
        control_frame = ttk.Frame(main_frame, style='TFrame')
        control_frame.pack(fill='x', pady=(0, 10))

        # HDD Filter
        hdd_label = ttk.Label(control_frame, text='Filter HDD:', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        hdd_label.pack(side='left', padx=(0, 10))
        
        self.hdd_filter_var = tk.StringVar(value='Semua HDD')
        self.hdd_filter_combo = ttk.Combobox(control_frame, textvariable=self.hdd_filter_var, width=20, state='readonly')
        self.hdd_filter_combo.pack(side='left', padx=(0, 20))
        self.hdd_filter_combo.bind('<<ComboboxSelected>>', self.on_hdd_filter_change)

        # Search frame
        search_label = ttk.Label(control_frame, text='Cari Game:', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        search_label.pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        clear_btn = ttk.Button(control_frame, text='Reset', command=self.reset_game_list, style='TButton')
        clear_btn.pack(side='left')

        # Frame untuk tabel game
        table_frame = ttk.Frame(main_frame, style='TFrame')
        table_frame.pack(fill='both', expand=True)

        # Label tabel
        table_label = ttk.Label(table_frame, text='Daftar Game:', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        table_label.pack(anchor='w', pady=(0, 8))

        # Tabel game dengan scrollbar
        table_container = ttk.Frame(table_frame, style='TFrame')
        table_container.pack(fill='both', expand=True)

        columns = ('No', 'Game', 'Size', 'HDD')
        self.game_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=20, style='Treeview')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.game_tree.yview)
        self.game_tree.configure(yscrollcommand=scrollbar.set)
        
        # Headings
        self.game_tree.heading('No', text='No')
        self.game_tree.heading('Game', text='Nama Game')
        self.game_tree.heading('Size', text='Size')
        self.game_tree.heading('HDD', text='HDD')
        
        # Columns
        self.game_tree.column('No', width=50, anchor='center')
        self.game_tree.column('Game', width=400, anchor='w')
        self.game_tree.column('Size', width=120, anchor='center')
        self.game_tree.column('HDD', width=150, anchor='w')
        
        # Tags untuk alternating row colors
        self.game_tree.tag_configure('oddrow', background=DARK_ROW2, foreground=DARK_TEXT)
        self.game_tree.tag_configure('evenrow', background=DARK_ROW1, foreground=DARK_TEXT)
        
        # Pack table dan scrollbar
        self.game_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Frame untuk info
        info_frame = ttk.Frame(main_frame, style='TFrame')
        info_frame.pack(fill='x', pady=(10, 0))
        
        # Info total game
        self.total_games_label = ttk.Label(info_frame, text='Total Game: 0', font=('Segoe UI', 10, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        self.total_games_label.pack(side='left')
        
        # Info total size
        self.total_size_label = ttk.Label(info_frame, text='Total Size: 0', font=('Segoe UI', 10, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        self.total_size_label.pack(side='right')

        # Refresh game list
        self.refresh_game_list()

    def on_hdd_filter_change(self, event=None):
        self.refresh_game_list()

    def on_search_change(self, event=None):
        self.refresh_game_list()

    def scan_folder(self):
        folder_path = filedialog.askdirectory(title='Pilih folder untuk scan game')
        if folder_path:
            self.scan_folder_for_games(folder_path)

    def scan_folder_for_games(self, folder_path):
        try:
            # Tampilkan progress dialog
            progress_window = tk.Toplevel(self)
            progress_window.title('Scanning Folder')
            progress_window.geometry('400x150')
            progress_window.configure(bg=DARK_BG)
            progress_window.transient(self)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text='Scanning folder...', background=DARK_BG, foreground=DARK_TEXT)
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            progress_bar.start()
            
            # Update UI
            progress_window.update()
            
            # Scan folder
            found_games = []
            for root, dirs, files in os.walk(folder_path):
                for dir_name in dirs:
                    # Skip system folders
                    if dir_name.startswith('.') or dir_name in ['$RECYCLE.BIN', 'System Volume Information']:
                        continue
                    
                    dir_path = os.path.join(root, dir_name)
                    try:
                        # Check if directory contains game files
                        game_files = []
                        for file in os.listdir(dir_path):
                            if file.lower().endswith(('.exe', '.bat', '.lnk')):
                                game_files.append(file)
                        
                        if game_files:
                            # Calculate folder size
                            total_size = 0
                            for root2, dirs2, files2 in os.walk(dir_path):
                                for file2 in files2:
                                    try:
                                        file_path = os.path.join(root2, file2)
                                        if os.path.isfile(file_path):
                                            total_size += os.path.getsize(file_path)
                                    except:
                                        continue
                            
                            found_games.append({
                                'name': dir_name,
                                'path': dir_path,
                                'size': total_size
                            })
                    except:
                        continue
            
            progress_window.destroy()
            
            if found_games:
                # Show results dialog
                self.show_scan_results(found_games, folder_path)
            else:
                messagebox.showinfo('Scan Result', 'Tidak ada game yang ditemukan di folder tersebut.')
                
        except Exception as e:
            messagebox.showerror('Error', f'Error saat scanning folder: {str(e)}')

    def show_scan_results(self, found_games, folder_path):
        # Create results window
        results_window = tk.Toplevel(self)
        results_window.title('Hasil Scan Folder')
        results_window.geometry('600x500')
        results_window.configure(bg=DARK_BG)
        results_window.transient(self)
        
        # Header
        header_label = ttk.Label(results_window, text=f'Game ditemukan di: {folder_path}', 
                                font=('Segoe UI', 12, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        header_label.pack(pady=10)
        
        # Frame untuk tabel
        table_frame = ttk.Frame(results_window, style='TFrame')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tabel hasil
        columns = ('No', 'Game', 'Size', 'Path')
        results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=results_tree.yview)
        results_tree.configure(yscrollcommand=scrollbar.set)
        
        # Headings
        results_tree.heading('No', text='No')
        results_tree.heading('Game', text='Nama Game')
        results_tree.heading('Size', text='Size')
        results_tree.heading('Path', text='Path')
        
        # Columns
        results_tree.column('No', width=50, anchor='center')
        results_tree.column('Game', width=200, anchor='w')
        results_tree.column('Size', width=100, anchor='center')
        results_tree.column('Path', width=200, anchor='w')
        
        # Tags
        results_tree.tag_configure('oddrow', background=DARK_ROW2, foreground=DARK_TEXT)
        results_tree.tag_configure('evenrow', background=DARK_ROW1, foreground=DARK_TEXT)
        
        # Insert data
        for i, game in enumerate(found_games):
            size_str = ''
            if game['size'] >= 1024**3:
                size_str = f"{game['size']/(1024**3):.2f} GB"
            elif game['size'] >= 1024**2:
                size_str = f"{game['size']/(1024**2):.2f} MB"
            elif game['size'] >= 1024:
                size_str = f"{game['size']/1024:.2f} KB"
            else:
                size_str = f"{game['size']} B"
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            results_tree.insert('', 'end', values=(i+1, game['name'], size_str, game['path']), tags=(tag,))
        
        # Pack table dan scrollbar
        results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = ttk.Frame(results_window, style='TFrame')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Buttons
        add_all_btn = ttk.Button(button_frame, text='Tambah Semua ke Database', 
                                command=lambda: self.add_games_to_database(found_games, results_window))
        add_all_btn.pack(side='left', padx=(0, 10))
        
        close_btn = ttk.Button(button_frame, text='Tutup', command=results_window.destroy)
        close_btn.pack(side='right')

    def add_games_to_database(self, found_games, results_window):
        # Ask user to select HDD
        hdd_names = [h['name'] for h in self.hdds]
        if not hdd_names:
            messagebox.showwarning('Warning', 'Tidak ada HDD yang tersedia. Silakan tambah HDD terlebih dahulu.')
            return
        
        # Create HDD selection dialog
        hdd_dialog = tk.Toplevel(results_window)
        hdd_dialog.title('Pilih HDD')
        hdd_dialog.geometry('300x150')
        hdd_dialog.configure(bg=DARK_BG)
        hdd_dialog.transient(results_window)
        hdd_dialog.grab_set()
        
        label = ttk.Label(hdd_dialog, text='Pilih HDD untuk menyimpan game:', 
                         background=DARK_BG, foreground=DARK_TEXT)
        label.pack(pady=20)
        
        hdd_var = tk.StringVar(value=hdd_names[0])
        hdd_combo = ttk.Combobox(hdd_dialog, textvariable=hdd_var, values=hdd_names, state='readonly')
        hdd_combo.pack(pady=10)
        
        def add_games():
            selected_hdd = hdd_var.get()
            hdd_obj = next((h for h in self.hdds if h['name'] == selected_hdd), None)
            
            if hdd_obj:
                # Add games to database
                for game in found_games:
                    game_id = self._generate_id()
                    self.games.append({
                        'id': game_id,
                        'name': game['name'],
                        'hdd_id': hdd_obj['id'],
                        'size': game['size'],
                        'path': game['path']
                    })
                
                self.save_game_data()
                self.refresh_game_list()
                messagebox.showinfo('Success', f'{len(found_games)} game berhasil ditambahkan ke database.')
                hdd_dialog.destroy()
                results_window.destroy()
        
        add_btn = ttk.Button(hdd_dialog, text='Tambah', command=add_games)
        add_btn.pack(pady=10)

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

    def export_all_games_to_excel(self):
        """Ekspor semua game ke file Excel (CSV)"""
        if not self.games:
            messagebox.showinfo('Info', 'Tidak ada game untuk diekspor.')
            return
        
        filename = filedialog.asksaveasfilename(
            title='Simpan File Excel',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=f'games_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['No', 'Nama Game', 'Size (Bytes)', 'Size (Formatted)', 'HDD', 'Path']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    # Sort games by name
                    sorted_games = sorted(self.games, key=lambda g: g['name'].lower())
                    
                    for i, game in enumerate(sorted_games, 1):
                        size_bytes = game.get('size', 0)
                        
                        # Format size
                        if size_bytes >= 1024**3:
                            size_formatted = f"{size_bytes/(1024**3):.2f} GB"
                        elif size_bytes >= 1024**2:
                            size_formatted = f"{size_bytes/(1024**2):.2f} MB"
                        elif size_bytes >= 1024:
                            size_formatted = f"{size_bytes/1024:.2f} KB"
                        else:
                            size_formatted = f"{size_bytes} B"
                        
                        hdd_name = self.get_hdd_name(game['hdd_id'])
                        game_path = game.get('path', '')
                        
                        writer.writerow({
                            'No': i,
                            'Nama Game': game['name'],
                            'Size (Bytes)': size_bytes,
                            'Size (Formatted)': size_formatted,
                            'HDD': hdd_name,
                            'Path': game_path
                        })
                
                messagebox.showinfo('Sukses', f'Berhasil mengekspor {len(sorted_games)} game ke:\n{filename}')
                
            except Exception as e:
                messagebox.showerror('Error', f'Gagal mengekspor file: {str(e)}')

    def export_filtered_games_to_excel(self):
        """Ekspor game yang terfilter ke file Excel (CSV)"""
        # Get current filtered games
        filtered_games = self.games.copy()
        
        # Filter berdasarkan HDD
        selected_hdd = self.hdd_filter_var.get()
        if selected_hdd and selected_hdd != 'Semua HDD':
            hdd_obj = next((h for h in self.hdds if h['name'] == selected_hdd), None)
            if hdd_obj:
                filtered_games = [g for g in filtered_games if g['hdd_id'] == hdd_obj['id']]
        
        # Filter berdasarkan search
        search_text = self.search_var.get().strip().lower()
        if search_text:
            filtered_games = [g for g in filtered_games if search_text in g['name'].lower()]
        
        if not filtered_games:
            messagebox.showinfo('Info', 'Tidak ada game yang terfilter untuk diekspor.')
            return
        
        filename = filedialog.asksaveasfilename(
            title='Simpan File Excel (Game Terfilter)',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=f'filtered_games_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['No', 'Nama Game', 'Size (Bytes)', 'Size (Formatted)', 'HDD', 'Path']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    # Sort games by name
                    sorted_games = sorted(filtered_games, key=lambda g: g['name'].lower())
                    
                    for i, game in enumerate(sorted_games, 1):
                        size_bytes = game.get('size', 0)
                        
                        # Format size
                        if size_bytes >= 1024**3:
                            size_formatted = f"{size_bytes/(1024**3):.2f} GB"
                        elif size_bytes >= 1024**2:
                            size_formatted = f"{size_bytes/(1024**2):.2f} MB"
                        elif size_bytes >= 1024:
                            size_formatted = f"{size_bytes/1024:.2f} KB"
                        else:
                            size_formatted = f"{size_bytes} B"
                        
                        hdd_name = self.get_hdd_name(game['hdd_id'])
                        game_path = game.get('path', '')
                        
                        writer.writerow({
                            'No': i,
                            'Nama Game': game['name'],
                            'Size (Bytes)': size_bytes,
                            'Size (Formatted)': size_formatted,
                            'HDD': hdd_name,
                            'Path': game_path
                        })
                
                messagebox.showinfo('Sukses', f'Berhasil mengekspor {len(sorted_games)} game terfilter ke:\n{filename}')
                
            except Exception as e:
                messagebox.showerror('Error', f'Gagal mengekspor file: {str(e)}')

    def open_size_window(self):
        SizeWindow(self)

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
            # Threshold: minimal 70% kata sama
            if best_score >= 0.70:
                for g in best_matches:
                    hdd_name = self.get_hdd_name(g['hdd_id'])
                    size_str = ''
                    if 'size' in g:
                        sz = g['size']
                        if sz >= 1024**3:
                            size_str = f"{sz/(1024**3):.2f} GB"
                        elif sz >= 1024**2:
                            size_str = f"{sz/(1024**2):.2f} MB"
                        elif sz >= 1024:
                            size_str = f"{sz/1024:.2f} KB"
                        else:
                            size_str = f"{sz} B"
                    tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                    self.result_tree.insert('', 'end', values=(i+1, g['name'], size_str, hdd_name, 'ADA'), tags=(tag,))
                    row_idx += 1
                tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                self.result_tree.insert('', 'end', values=(i+1, game, '', '-', 'TIDAK ADA'), tags=(tag,))
                row_idx += 1

    def refresh_list_game(self):
        # Method ini sudah tidak digunakan, diganti dengan refresh_game_list
        self.refresh_game_list()

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
        # Update combobox HDD filter jika sudah ada
        if hasattr(self, 'hdd_filter_combo'):
            hdd_names = ['Semua HDD'] + [h['name'] for h in self.hdds]
            self.hdd_filter_combo['values'] = hdd_names
            if self.hdd_filter_var.get() not in hdd_names:
                self.hdd_filter_var.set('Semua HDD')
            self.refresh_game_list()

    def save_game_data(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({'hdds': self.hdds, 'games': self.games}, f, ensure_ascii=False, indent=2)

class ManageWindow(tk.Toplevel):
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
            game_id = self._generate_id()
            self.master.games.append({'id': game_id, 'name': name, 'hdd_id': self.selected_hdd_id})
            self.master.save_game_data()
            self.refresh_game_list()

    def edit_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        games = sorted(games, key=lambda g: g['name'].lower())
        game = games[idx[0]]
        name = simpledialog.askstring('Edit Game', 'Nama Game:', initialvalue=game['name'])
        if name:
            for g in self.master.games:
                if g.get('id') == game.get('id'):
                    g['name'] = name
                    break
            self.master.save_game_data()
            self.refresh_game_list()

    def delete_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        games = sorted(games, key=lambda g: g['name'].lower())
        game = games[idx[0]]
        if messagebox.askyesno('Konfirmasi', f'Hapus game "{game['name']}"?'):
            self.master.games = [g for g in self.master.games if g.get('id') != game.get('id')]
            self.master.save_game_data()
            self.refresh_game_list()

    def scan_folder(self):
        import os
        if not self.selected_hdd_id:
                self.selected_hdd_id = self.master.hdds[0]['id']
                self.hdd_listbox.selection_set(0)
                self.on_hdd_select()
        if not self.selected_hdd_id:
            messagebox.showinfo('Info', 'Pilih HDD terlebih dahulu.')
            return
        folder = filedialog.askdirectory(title='Pilih Folder HDD untuk Scan')
        if not folder:
            return
        try:
            subfolders = [f for f in os.scandir(folder) if f.is_dir()]
        except Exception as e:
            messagebox.showerror('Error', f'Gagal scan folder: {e}')
            return
        def get_folder_size(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            return total
        added = 0
        updated = 0
        for f in subfolders:
            name = f.name
            full_path = f.path
            size_bytes = get_folder_size(full_path)
            found = None
            for g in self.master.games:
                if g['name'].lower() == name.lower() and g['hdd_id'] == self.selected_hdd_id:
                    found = g
                    break
            if found:
                if found.get('size') != size_bytes:
                    found['size'] = size_bytes
                    updated += 1
            else:
                game_id = self._generate_id()
                self.master.games.append({'id': game_id, 'name': name, 'hdd_id': self.selected_hdd_id, 'size': size_bytes})
                added += 1
        self.master.save_game_data()
        self.refresh_game_list()
        messagebox.showinfo('Scan Selesai', f'{added} game baru ditambahkan, {updated} size game diupdate.')

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())
    def __init__(self, master):
        super().__init__(master)
        self.title('Kelola HDD & Game')
        self.geometry('700x420')
        self.resizable(False, False)
        self.configure(bg=DARK_BG)
        self.master = master
        self.master.load_game_data()  # Pastikan data selalu terisi
        self.selected_hdd_id = None
        self.create_widgets()
        self.refresh_hdd_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        # Daftar HDD (kiri)
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
        # Daftar Game (kanan)
        game_frame = ttk.Frame(main_frame, style='TFrame')
        game_frame.grid(row=0, column=1, sticky='ns')
        ttk.Label(game_frame, text='Daftar Game di HDD', font=('Segoe UI', 11, 'bold'), background=DARK_BG, foreground=DARK_HEADING).grid(row=0, column=0, pady=(2,4))
        self.game_listbox = tk.Listbox(game_frame, width=40, height=16, font=('Segoe UI', 11), bg=DARK_ROW1, fg=DARK_TEXT, selectbackground=DARK_HEADING, selectforeground=DARK_BG, highlightbackground=DARK_PANEL, relief='flat', borderwidth=0, selectmode='browse')
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
    # def on_game_select(self, event=None):
    #     Tidak perlu lagi, label total size sudah dihapus

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
            size_str = ''
            if 'size' in game:
                sz = game['size']
                if sz >= 1024**3:
                    size_str = f" ({sz/(1024**3):.2f} GB)"
                elif sz >= 1024**2:
                    size_str = f" ({sz/(1024**2):.2f} MB)"
                elif sz >= 1024:
                    size_str = f" ({sz/1024:.2f} KB)"
                else:
                    size_str = f" ({sz} B)"
            self.game_listbox.insert(tk.END, game['name'] + size_str)
# Window baru untuk select game dan hitung total size
class SizeWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Hitung Total Size Game')
        self.geometry('1000x600')
        self.resizable(True, True)
        self.configure(bg=DARK_BG)
        self.master = master
        
        # Main container
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text='Hitung Total Size Game', 
                               font=('Segoe UI', 16, 'bold'), background=DARK_BG, foreground=DARK_HEADING)
        title_label.pack(side='left')
        
        # Control panel
        control_frame = ttk.Frame(main_frame, style='TFrame')
        control_frame.pack(fill='x', pady=(0, 10))
        
        # HDD Filter
        hdd_label = ttk.Label(control_frame, text='Filter HDD:', font=('Segoe UI', 10, 'bold'), 
                             background=DARK_BG, foreground=DARK_HEADING)
        hdd_label.pack(side='left', padx=(0, 5))
        
        self.hdd_filter_var = tk.StringVar(value='Semua HDD')
        self.hdd_filter_combo = ttk.Combobox(control_frame, textvariable=self.hdd_filter_var, 
                                           width=15, state='readonly')
        self.hdd_filter_combo.pack(side='left', padx=(0, 20))
        self.hdd_filter_combo.bind('<<ComboboxSelected>>', self.on_hdd_filter_change)
        
        # Search
        search_label = ttk.Label(control_frame, text='Cari Game:', font=('Segoe UI', 10, 'bold'), 
                                background=DARK_BG, foreground=DARK_HEADING)
        search_label.pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Buttons
        clear_btn = ttk.Button(control_frame, text='Reset', command=self.reset_game_list, style='TButton')
        clear_btn.pack(side='left', padx=(0, 10))
        
        add_all_btn = ttk.Button(control_frame, text='Tambah Semua', command=self.add_all_games, style='TButton')
        add_all_btn.pack(side='left')
        
        # Content area - 2 columns
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill='both', expand=True)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Available games
        left_frame = ttk.Frame(content_frame, style='TFrame')
        left_frame.grid(row=0, column=0, sticky='nswe', padx=(0, 10))
        
        left_label = ttk.Label(left_frame, text='Game Tersedia:', font=('Segoe UI', 12, 'bold'), 
                              background=DARK_BG, foreground=DARK_HEADING)
        left_label.pack(anchor='w', pady=(0, 8))
        
        # Game list with scrollbar
        list_container = ttk.Frame(left_frame, style='TFrame')
        list_container.pack(fill='both', expand=True)
        
        self.game_listbox = tk.Listbox(list_container, font=('Segoe UI', 10), 
                                      bg=DARK_ROW1, fg=DARK_TEXT, 
                                      selectbackground=DARK_HEADING, selectforeground=DARK_BG,
                                      highlightbackground=DARK_PANEL, relief='flat', 
                                      borderwidth=0, selectmode='extended')
        
        list_scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.game_listbox.yview)
        self.game_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.game_listbox.pack(side='left', fill='both', expand=True)
        list_scrollbar.pack(side='right', fill='y')
        
        # Add button
        add_btn = ttk.Button(left_frame, text='Tambah ke Tabel →', command=self.add_selected_to_table, style='TButton')
        add_btn.pack(pady=(8, 0))
        
        # Right panel - Selected games
        right_frame = ttk.Frame(content_frame, style='TFrame')
        right_frame.grid(row=0, column=1, sticky='nswe')
        
        right_label = ttk.Label(right_frame, text='Game yang Dihitung:', font=('Segoe UI', 12, 'bold'), 
                               background=DARK_BG, foreground=DARK_HEADING)
        right_label.pack(anchor='w', pady=(0, 8))
        
        # Selected games table
        table_container = ttk.Frame(right_frame, style='TFrame')
        table_container.pack(fill='both', expand=True)
        
        columns = ('No', 'Game', 'Size', 'HDD')
        self.selected_tree = ttk.Treeview(table_container, columns=columns, show='headings', style='Treeview')
        
        table_scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.selected_tree.yview)
        self.selected_tree.configure(yscrollcommand=table_scrollbar.set)
        
        # Headings
        self.selected_tree.heading('No', text='No')
        self.selected_tree.heading('Game', text='Nama Game')
        self.selected_tree.heading('Size', text='Size')
        self.selected_tree.heading('HDD', text='HDD')
        
        # Columns
        self.selected_tree.column('No', width=40, anchor='center')
        self.selected_tree.column('Game', width=200, anchor='w')
        self.selected_tree.column('Size', width=80, anchor='center')
        self.selected_tree.column('HDD', width=100, anchor='w')
        
        # Tags
        self.selected_tree.tag_configure('oddrow', background=DARK_ROW2, foreground=DARK_TEXT)
        self.selected_tree.tag_configure('evenrow', background=DARK_ROW1, foreground=DARK_TEXT)
        
        self.selected_tree.pack(side='left', fill='both', expand=True)
        table_scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        button_frame = ttk.Frame(right_frame, style='TFrame')
        button_frame.pack(fill='x', pady=(8, 0))
        
        del_btn = ttk.Button(button_frame, text='Hapus dari Tabel', command=self.remove_selected_from_table, style='TButton')
        del_btn.pack(side='left')
        
        clear_all_btn = ttk.Button(button_frame, text='Hapus Semua', command=self.clear_all_selected, style='TButton')
        clear_all_btn.pack(side='left', padx=(10, 0))
        
        export_btn = ttk.Button(button_frame, text='Ekspor ke Excel', command=self.export_selected_to_excel, style='TButton')
        export_btn.pack(side='right')
        
        # Info panel
        info_frame = ttk.Frame(main_frame, style='TFrame')
        info_frame.pack(fill='x', pady=(15, 0))
        
        self.total_games_label = ttk.Label(info_frame, text='Total Game: 0', 
                                          font=('Segoe UI', 10, 'bold'), 
                                          background=DARK_BG, foreground=DARK_HEADING)
        self.total_games_label.pack(side='left')
        
        self.total_size_label = ttk.Label(info_frame, text='Total Size: 0', 
                                         font=('Segoe UI', 12, 'bold'), 
                                         background=DARK_BG, foreground=DARK_HEADING)
        self.total_size_label.pack(side='right')
        
        # Initialize
        self.selected_games = []
        self.refresh_game_list()

    def refresh_game_list(self):
        self.game_listbox.delete(0, tk.END)
        
        # Update HDD filter combo
        hdd_names = ['Semua HDD'] + [h['name'] for h in self.master.hdds]
        self.hdd_filter_combo['values'] = hdd_names
        
        # Filter games berdasarkan HDD dan search
        filtered_games = self.master.games.copy()
        
        # Filter berdasarkan HDD
        selected_hdd = self.hdd_filter_var.get()
        if selected_hdd and selected_hdd != 'Semua HDD':
            hdd_obj = next((h for h in self.master.hdds if h['name'] == selected_hdd), None)
            if hdd_obj:
                filtered_games = [g for g in filtered_games if g['hdd_id'] == hdd_obj['id']]
        
        # Filter berdasarkan search
        search_text = self.search_var.get().strip().lower()
        if search_text:
            filtered_games = [g for g in filtered_games if search_text in g['name'].lower()]
        
        # Sort games
        filtered_games = sorted(filtered_games, key=lambda g: g['name'].lower())
        self._filtered_games = filtered_games.copy()
        
        # Insert ke listbox
        for game in filtered_games:
            size_str = ''
            if 'size' in game:
                sz = game['size']
                if sz >= 1024**3:
                    size_str = f" ({sz/(1024**3):.2f} GB)"
                elif sz >= 1024**2:
                    size_str = f" ({sz/(1024**2):.2f} MB)"
                elif sz >= 1024:
                    size_str = f" ({sz/1024:.2f} KB)"
                else:
                    size_str = f" ({sz} B)"
            self.game_listbox.insert(tk.END, game['name'] + size_str)
        
        self.update_total_size()

    def on_hdd_filter_change(self, event=None):
        self.refresh_game_list()

    def on_search_change(self, event=None):
        self.refresh_game_list()

    def add_all_games(self):
        if not self._filtered_games:
            messagebox.showinfo('Info', 'Tidak ada game yang tersedia.')
            return
        
        # Clear existing selections
        self.selected_tree.delete(*self.selected_tree.get_children())
        self.selected_games.clear()
        
        # Add all filtered games
        row_idx = 0
        for game in self._filtered_games:
            size_str = ''
            if 'size' in game:
                sz = game['size']
                if sz >= 1024**3:
                    size_str = f"{sz/(1024**3):.2f} GB"
                elif sz >= 1024**2:
                    size_str = f"{sz/(1024**2):.2f} MB"
                elif sz >= 1024:
                    size_str = f"{sz/1024:.2f} KB"
                else:
                    size_str = f"{sz} B"
            
            hdd_name = self.get_hdd_name(game['hdd_id'])
            tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
            self.selected_tree.insert('', 'end', values=(row_idx + 1, game['name'], size_str, hdd_name), tags=(tag,))
            self.selected_games.append(game)
            row_idx += 1
        
        self.update_total_size()

    def clear_all_selected(self):
        self.selected_tree.delete(*self.selected_tree.get_children())
        self.selected_games.clear()
        self.update_total_size()

    def get_hdd_name(self, hdd_id):
        for h in self.master.hdds:
            if h['id'] == hdd_id:
                return h['name']
        return '-'

    def add_selected_to_table(self):
        selected_indices = self.game_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo('Info', 'Pilih game terlebih dahulu.')
            return
        
        # Debug: print selected indices and filtered games
        print(f"Selected indices: {selected_indices}")
        print(f"Filtered games count: {len(self._filtered_games)}")
        
        row_idx = len(self.selected_tree.get_children())
        added_count = 0
        
        for idx in selected_indices:
            if idx < len(self._filtered_games):
                game = self._filtered_games[idx]
                
                # Check if game already exists in selected list by name (more reliable)
                if any(g['name'] == game['name'] for g in self.selected_games):
                    print(f"Game {game['name']} already exists, skipping...")
                    continue
                
                size_str = ''
                if 'size' in game:
                    sz = game['size']
                    if sz >= 1024**3:
                        size_str = f"{sz/(1024**3):.2f} GB"
                    elif sz >= 1024**2:
                        size_str = f"{sz/(1024**2):.2f} MB"
                    elif sz >= 1024:
                        size_str = f"{sz/1024:.2f} KB"
                    else:
                        size_str = f"{sz} B"
                
                hdd_name = self.get_hdd_name(game['hdd_id'])
                tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                self.selected_tree.insert('', 'end', values=(row_idx + 1, game['name'], size_str, hdd_name), tags=(tag,))
                self.selected_games.append(game)
                row_idx += 1
                added_count += 1
                print(f"Added game: {game['name']}")
        
        if added_count == 0:
            messagebox.showinfo('Info', 'Semua game yang dipilih sudah ada di tabel.')
        else:
            print(f"Total added: {added_count}")
        
        self.update_total_size()

    def remove_selected_from_table(self):
        selected_items = self.selected_tree.selection()
        if not selected_items:
            messagebox.showinfo('Info', 'Pilih game dari tabel terlebih dahulu.')
            return
        
        for item in selected_items:
            values = self.selected_tree.item(item, 'values')
            game_name = values[1]  # Nama game ada di kolom kedua
            
            # Hapus dari treeview
            self.selected_tree.delete(item)
            
            # Hapus dari selected_games list
            self.selected_games = [g for g in self.selected_games if g['name'] != game_name]
        
        # Reorder nomor urut
        items = self.selected_tree.get_children()
        for i, item in enumerate(items):
            values = list(self.selected_tree.item(item, 'values'))
            values[0] = i + 1  # Update nomor urut
            self.selected_tree.item(item, values=values)
        
        self.update_total_size()

    def update_total_size(self):
        total = sum(game.get('size', 0) for game in self.selected_games)
        if total >= 1024**3:
            size_str = f"{total/(1024**3):.2f} GB"
        elif total >= 1024**2:
            size_str = f"{total/(1024**2):.2f} MB"
        elif total >= 1024:
            size_str = f"{total/1024:.2f} KB"
        else:
            size_str = f"{total} B"
        
        self.total_games_label.config(text=f'Total Game: {len(self.selected_games)}')
        self.total_size_label.config(text=f'Total Size: {size_str}')

    def filter_game_list(self):
        search_text = self.search_var.get().strip().lower()
        self.game_listbox.delete(0, tk.END)
        filtered_games = [g for g in self.master.games if search_text in g['name'].lower()]
        for game in sorted(filtered_games, key=lambda g: g['name'].lower()):
            size_str = ''
            if 'size' in game:
                sz = game['size']
                if sz >= 1024**3:
                    size_str = f" ({sz/(1024**3):.2f} GB)"
                elif sz >= 1024**2:
                    size_str = f" ({sz/(1024**2):.2f} MB)"
                elif sz >= 1024:
                    size_str = f" ({sz/1024:.2f} KB)"
                else:
                    size_str = f" ({sz} B)"
            self.game_listbox.insert(tk.END, game['name'] + size_str)

    def reset_game_list(self):
        self.search_var.set('')
        self.refresh_game_list()

    def on_game_select(self, event=None):
        idxs = self.game_listbox.curselection()
        if not idxs:
            self.total_size_label.config(text='Total Size: 0')
            return
        games = sorted(self.master.games, key=lambda g: g['name'].lower())
        total = 0
        for i in idxs:
            if i < len(games):
                sz = games[i].get('size', 0)
                if isinstance(sz, int):
                    total += sz
        if total >= 1024**3:
            size_str = f"{total/(1024**3):.2f} GB"
        elif total >= 1024**2:
            size_str = f"{total/(1024**2):.2f} MB"
        elif total >= 1024:
            size_str = f"{total/1024:.2f} KB"
        else:
            size_str = f"{total} B"
        self.total_size_label.config(text=f'Total Size: {size_str}')

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
            game_id = self._generate_id()
            self.master.games.append({'id': game_id, 'name': name, 'hdd_id': self.selected_hdd_id})
            self.master.save_game_data()
            self.refresh_game_list()

    def edit_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        # Ambil list game yang sudah diurutkan seperti di Listbox
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        games = sorted(games, key=lambda g: g['name'].lower())
        game = games[idx[0]]
        name = simpledialog.askstring('Edit Game', 'Nama Game:', initialvalue=game['name'])
        if name:
            # Update nama game di database berdasarkan id
            for g in self.master.games:
                if g.get('id') == game.get('id'):
                    g['name'] = name
                    break
            self.master.save_game_data()
            self.refresh_game_list()

    def delete_game(self):
        idx = self.game_listbox.curselection()
        if not idx or not self.selected_hdd_id:
            return
        # Ambil list game yang sudah diurutkan seperti di Listbox
        games = [g for g in self.master.games if g['hdd_id'] == self.selected_hdd_id]
        games = sorted(games, key=lambda g: g['name'].lower())
        game = games[idx[0]]
        if messagebox.askyesno('Konfirmasi', f'Hapus game "{game['name']}"?'):
            # Hapus game dari database berdasarkan id
            self.master.games = [g for g in self.master.games if g.get('id') != game.get('id')]
            self.master.save_game_data()
            self.refresh_game_list()

    def scan_folder(self):
        import os
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
            subfolders = [f for f in os.scandir(folder) if f.is_dir()]
        except Exception as e:
            messagebox.showerror('Error', f'Gagal scan folder: {e}')
            return
        def get_folder_size(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            return total
        added = 0
        updated = 0
        for f in subfolders:
            name = f.name
            full_path = f.path
            size_bytes = get_folder_size(full_path)
            # Cari game dengan nama dan hdd_id sama (case-insensitive)
            found = None
            for g in self.master.games:
                if g['name'].lower() == name.lower() and g['hdd_id'] == self.selected_hdd_id:
                    found = g
                    break
            if found:
                # Update size jika berbeda atau belum ada
                if found.get('size') != size_bytes:
                    found['size'] = size_bytes
                    updated += 1
            else:
                game_id = self._generate_id()
                self.master.games.append({'id': game_id, 'name': name, 'hdd_id': self.selected_hdd_id, 'size': size_bytes})
                added += 1
        self.master.save_game_data()
        self.refresh_game_list()
        messagebox.showinfo('Scan Selesai', f'{added} game baru ditambahkan, {updated} size game diupdate.')

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

    def export_selected_to_excel(self):
        """Ekspor game yang dipilih ke file Excel (CSV)"""
        if not self.selected_games:
            messagebox.showinfo('Info', 'Tidak ada game yang dipilih untuk diekspor.')
            return
        
        filename = filedialog.asksaveasfilename(
            title='Simpan File Excel (Game Terpilih)',
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            initialfile=f'selected_games_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['No', 'Nama Game', 'Size (Bytes)', 'Size (Formatted)', 'HDD', 'Path']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    for i, game in enumerate(self.selected_games, 1):
                        size_bytes = game.get('size', 0)
                        
                        # Format size
                        if size_bytes >= 1024**3:
                            size_formatted = f"{size_bytes/(1024**3):.2f} GB"
                        elif size_bytes >= 1024**2:
                            size_formatted = f"{size_bytes/(1024**2):.2f} MB"
                        elif size_bytes >= 1024:
                            size_formatted = f"{size_bytes/1024:.2f} KB"
                        else:
                            size_formatted = f"{size_bytes} B"
                        
                        hdd_name = self.get_hdd_name(game['hdd_id'])
                        game_path = game.get('path', '')
                        
                        writer.writerow({
                            'No': i,
                            'Nama Game': game['name'],
                            'Size (Bytes)': size_bytes,
                            'Size (Formatted)': size_formatted,
                            'HDD': hdd_name,
                            'Path': game_path
                        })
                
                messagebox.showinfo('Sukses', f'Berhasil mengekspor {len(self.selected_games)} game terpilih ke:\n{filename}')
                
            except Exception as e:
                messagebox.showerror('Error', f'Gagal mengekspor file: {str(e)}')

if __name__ == '__main__':
    app = GameManagerApp()
    app.mainloop() 