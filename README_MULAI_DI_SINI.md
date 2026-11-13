# ORBIPERA — Aplikasi Web HR & Pembelajaran (Database SQLite)

**Status:** aplikasi web yang bisa dijalankan dengan backend dan database SQLite sungguhan, **menggunakan 360 data karyawan FIKTIF**. Ini bukan layanan ORBIPERA publik yang sudah di-hosting. Demo login & paket langganan tetap menggunakan data contoh; transaksi pembayaran dan pengaturan pembatasan paket belum diaktifkan.

## Jalankan di komputer

1. Ekstrak semua isi ZIP ke satu folder.
2. Pastikan Python 3.10 atau lebih baru terpasang (`python --version`). Tidak perlu `pip install` karena backend memakai pustaka standar Python.
3. **Windows:** klik `MULAI_ORBIPERA.bat` atau buka Command Prompt di folder ini dan jalankan `python server.py`.
4. **macOS / Linux:** jalankan `bash MULAI_ORBIPERA.sh` atau `python3 server.py`.
5. Buka browser di **http://127.0.0.1:8765**. Jangan buka `index.html` langsung dengan double-click: website ini memerlukan server database.
6. Login menggunakan akun contoh di bawah.

| Peran | Email | Password |
| --- | --- | --- |
| HR Admin | `admin@orbipera.demo` | `Admin123!` |
| Karyawan | `andi.rahman@orbipera.demo` | `Karyawan123!` |

Ke-360 alamat email karyawan yang ditampilkan di halaman HR menggunakan kata sandi contoh `Karyawan123!`. **Jangan memakai data pribadi atau data karyawan asli.**

## Alur demo yang bisa dicoba

1. Login HR → Dashboard → Karyawan: telusuri, cari dan pilih karyawan.
2. Asesmen: ubah kompetensi skala 1–5 → simpan. Perubahan langsung disimpan ke database.
3. Skill Gap: lihat selisih skor dengan target.
4. Login Karyawan → Pembelajaran: buka salah satu dari lima kursus, putar video MP4 yang memiliki audio, buka modul PDF, dan jawab lima pertanyaan kuis pilihan ganda.
5. **Kuis ≥70%:** status *LULUS*, nilai dan jawaban tersimpan, progres kursus menjadi 100%. Setiap pertanyaan dilengkapi alasan jawaban yang benar. Jika gagal, karyawan bisa mengulang.
6. Video selesai diputar → aktivitas tercatat; modul PDF dibuka → progres minimal bertambah. Monitoring memperlihatkan hasil terkini.
7. Bantuan: ajukan tiket kendala pembelajaran sebagai karyawan; balas dan ubah status sebagai HR.
8. Langganan: bandingkan dan pilih Basic, Professional, Business, Enterprise. Semua paket bisa dipilih **untuk demo**, tanpa membayar. Batas kuota belum diterapkan karena data uji berjumlah 360.
9. Perusahaan / Tentang ORBIPERA: profil pelanggan, visi, misi, motto, branding dan profil produk.

## Video & karakter suara

Lima MP4 memiliki **audio narasi sintetis bahasa Indonesia dan musik**; bukan rekaman pengisi suara manusia. Masing-masing sekitar satu menit. Di halaman kursus tersedia tombol **Bacakan Ringkasan**, yang menggunakan suara bahasa Indonesia dari browser/perangkat jika tersedia. Beberapa perangkat menyediakan suara neural yang lebih natural; hasilnya bisa berbeda antar-browser dan perangkat. Untuk suara manusia profesional diperlukan rekaman asli atau layanan TTS neural berlisensi, kemudian berkas MP4 di folder `assets/` dapat diganti.

## Struktur folder

- `server.py`: HTTP API, login, autentikasi server-side, aturan role, asesmen, kuis, learning events, tiket, paket.
- `index.html`: antarmuka responsif (landing page, dashboard HR/Karyawan, materi, kuis, monitoring, about).
- `orbipera.sqlite3`: database contoh dengan 360 karyawan, lima kursus, 25 soal, dan data awal.
- `assets/`: lima MP4 dengan audio, lima modul PDF, lima gambar kursus, logo PNG transparan.
- `MULAI_ORBIPERA.bat` / `.sh`: peluncur aplikasi.

## Cara menerbitkan secara online

Website ini **belum memiliki URL publik**. Untuk membuatnya dapat diakses dari HP atau komputer lain:

1. Tempatkan folder aplikasi di layanan hosting yang mendukung **proses Python server**, misalnya Render, Railway, VPS, atau layanan serupa.
2. Atur perintah jalankan: `python server.py`.
3. Atur `ORBIPERA_HOST=0.0.0.0`; aplikasi membaca variabel `PORT` dari hosting, atau `ORBIPERA_PORT` jika disetel.
4. Sediakan **penyimpanan persisten** untuk SQLite (atur `ORBIPERA_DB` ke jalur volume persisten). Tanpa itu, perubahan dapat hilang saat server restart/redeploy di beberapa platform.
5. Pasang HTTPS lewat reverse proxy/hosting.
6. **Sebelum publikasi umum:** hapus seluruh password demo, implementasikan undangan akun/password reset, pembatasan request login, CSRF protection tambahan, audit keamanan, backup, pemisahan organisasi, dan pengujian beban. Backend bawaan ini untuk MVP/validasi, **bukan sistem yang aman untuk data pribadi sungguhan**.

## Keterbatasan

- URL Canva referensi yang diberikan belum dapat diambil untuk dibandingkan per halaman. Desain memakai bahasa visual ORBIPERA dari file sebelumnya.
- Pembayaran, AI rekomendasi generatif, mentor terpisah, notifikasi email, akun publik, dan multi-tenant produksi belum dibuat. Rekomendasi tetap berbasis selisih kompetensi.
- Seorang HR dan karyawan dari dataset contoh mewakili satu perusahaan. Untuk banyak perusahaan nyata perlu isolasi data per tenant.
- Semua statistik berasal dari dataset contoh dan bisa berubah sesuai tindakan dalam aplikasi.

**ORBIPERA — Grow. Learn. Perform Better.**
