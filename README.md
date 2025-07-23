# Manajemen Game HDD

Aplikasi ini membantu kamu mengelola daftar game yang tersebar di beberapa harddisk eksternal.

## Cara Menjalankan

1. Pastikan sudah terinstall Python 3 (disarankan 3.10+).
2. Jalankan aplikasi dengan perintah:
   ```bash
   python main.py
   ```

## Fitur Utama

- **Cari Game:**
  - Masukkan nama game (bisa lebih dari satu, pisahkan dengan koma) di halaman utama.
  - Hasil pencarian akan menampilkan game yang ada beserta HDD asalnya, dan game yang tidak ditemukan.

- **Kelola HDD & Game:**
  - Tambah, edit, hapus HDD.
  - Tambah, edit, hapus game secara manual per HDD.
  - Scan otomatis folder di HDD: semua subfolder dianggap nama game dan langsung ditambahkan ke database.

- **Data Otomatis Tersimpan:**
  - Semua data disimpan di file `games_db.json` di folder aplikasi.

## Tips Penggunaan

- Lakukan scan folder secara berkala jika ada game baru di HDD.
- Backup file `games_db.json` secara rutin untuk mencegah kehilangan data.
- Jika ingin memindahkan data ke komputer lain, cukup salin file `games_db.json`.

---

Jika ada pertanyaan atau ingin fitur tambahan, silakan hubungi pengembang aplikasi ini. # program-manajemen-HDD-
