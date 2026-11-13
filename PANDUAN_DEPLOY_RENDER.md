# Panduan upload ORBIPERA ke GitHub dan Render

**Status:** file sudah disiapkan, *belum dipublikasikan*. Render telah dihubungkan, tetapi layanan membutuhkan sumber kode dalam repositori Git yang dapat di-clone.

1. Masuk GitHub dan buat repositori baru, misalnya `orbipera-website`. **Gunakan isi ZIP "GitHub Ready"**, ekstrak lalu unggah semua berkas dan direktori `assets/` di akar repositori (bukan folder pembungkus tambahan). GitHub memiliki batas ukuran file per unggahan; MP4 di sini masing-masing berukuran sekitar 1,3 MB.
2. Bagikan URL HTTPS repositori yang dapat diakses Render. Jika repositori bersifat private, hubungkan akun GitHub dengan Render agar Render punya izin mengaksesnya.
3. Pada Render buat Web Service: repository GitHub tadi, Python, region Singapore, plan Free untuk **demo saja**, build command `echo ready`, start command `python server.py`, environment `ORBIPERA_HOST=0.0.0.0`.
4. Bila memakai Blueprint, file `render.yaml` berisi konfigurasi yang sama.
5. Setelah deploy sukses, Render akan memberikan URL `https://...onrender.com`.

### Catatan penting tentang penyimpanan

Render Free memiliki filesystem ephemerial: perubahan SQLite (progres kuis, skor, tiket) **dapat hilang setelah restart/redeploy**. Untuk menyimpan perubahan secara permanen pada layanan publik, gunakan volume/disk persisten pada paket yang mendukung atau migrasi ke PostgreSQL. PostgreSQL belum didukung oleh kode Python ini tanpa modifikasi.

### Keamanan

Website ini memakai kata sandi *demo yang dipublikasikan*, dan tidak boleh diisi data pribadi asli. Sebelum operasi produksi, diperlukan mekanisme registrasi/undangan akun, reset kata sandi, audit login, pembatasan percobaan login, pengelolaan tenant, backup, dan pengujian keamanan. Fitur paket hanya simulasi pemilihan, belum pembayaran.
