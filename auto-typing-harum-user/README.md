# Auto Typing GUI

Aplikasi GUI untuk auto typing data dari file Excel atau CSV ke form input menggunakan koordinat mouse dengan fitur lengkap dan fleksibel.

## Fitur Utama

### 📁 **Multi-Format File Support**
- Import data dari file Excel (.xlsx, .xls) atau CSV (.csv)
- Semua kolom dibaca sebagai string/text untuk mempertahankan format asli (leading zero, dll)
- Auto-detection format file berdasarkan ekstensi

### 🎯 **Coordinate Management**
- Set koordinat untuk setiap field input dengan capture mouse
- Dukungan untuk field text dan dropdown
- Validasi koordinat dengan error handling

### 🔧 **Custom Columns**
- Tambah kolom custom dengan nama bebas
- Set default value untuk kolom custom
- Dukungan tipe text dan dropdown untuk custom columns
- Koordinat terpisah untuk setiap custom column

### 📋 **Dropdown Configuration**
- Konfigurasi dropdown dengan multiple options
- Mapping nilai data ke koordinat dropdown yang berbeda
- Dukungan khusus untuk dropdown Jenis Kelamin

### ⚡ **Pre-Click Buttons**
- Tambah tombol pre-click sebelum auto typing
- Custom delay untuk setiap pre-click button
- Multiple pre-click buttons dengan urutan eksekusi

### 🎛️ **Advanced Controls**
- Enable/disable field secara individual
- Kontrol Start/Stop untuk proses auto typing
- Progress bar dengan status real-time
- Configurable submit delay antar baris data

## Instalasi

1. Pastikan Python 3.7+ terinstall
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Cara Penggunaan

1. Jalankan aplikasi:
   ```
   python auto_typing_gui.py
   ```

2. **Pilih File Excel atau CSV:**
   - Klik tombol "Browse" untuk memilih file Excel (.xlsx, .xls) atau CSV (.csv)
   - File dapat memiliki kolom apa saja (tidak terbatas pada kolom tertentu)
   - Semua data akan dibaca sebagai string untuk mempertahankan format asli

3. **Konfigurasi Fields:**
   - **Enable/Disable**: Centang/uncentang field yang ingin diproses
   - **Field Type**: Pilih "Text" atau "Dropdown" untuk setiap field
   - **Set Koordinat**: Klik tombol "Set Koordinat" untuk capture posisi mouse
   - **Dropdown Config**: Untuk field dropdown, klik "Config" untuk setup mapping nilai

4. **Custom Columns (Opsional):**
   - **Tambah Custom Column**: Masukkan nama kolom dan default value
   - **Set Koordinat**: Capture koordinat untuk custom column
   - **Dropdown Custom**: Konfigurasi dropdown untuk custom column jika diperlukan

5. **Pre-Click Buttons (Opsional):**
   - **Tambah Pre-Click**: Set tombol yang diklik sebelum auto typing
   - **Custom Delay**: Atur delay setelah setiap pre-click
   - **Multiple Buttons**: Tambah beberapa pre-click button sesuai kebutuhan

6. **Mulai Auto Typing:**
   - Pastikan koordinat yang diperlukan sudah diset
   - Atur "Submit Delay" sesuai kebutuhan
   - Klik "Start Auto Typing"
   - Proses akan berjalan otomatis untuk semua baris data
   - Gunakan "Stop" untuk menghentikan proses kapan saja

## Format File Excel/CSV

### **Fleksibilitas Kolom**
- File dapat memiliki kolom dengan nama apa saja
- Tidak ada batasan nama kolom yang harus digunakan
- Aplikasi akan otomatis membuat field berdasarkan header kolom

### **Contoh Format:**
```csv
Nama Lengkap,NIK,Email,Nomor Telepon,Jenis Kelamin,Unit,Password
"Susan Adriyanti, S.Pd",3215034106760002,susan@email.com,089664521468,P,SMPIT,password123
```

### **Preservasi Format Data**
- **Leading Zero**: Nomor telepon seperti `089664521468` akan tetap utuh
- **NIK dan ID**: Tidak akan kehilangan digit di depan
- **String Format**: Semua data dibaca sebagai text untuk menjaga format asli

## Tips Penggunaan

### **Persiapan:**
- Pastikan form target sudah terbuka sebelum memulai auto typing
- Test dengan 1-2 baris data terlebih dahulu sebelum memproses data besar
- Backup data penting sebelum melakukan auto typing massal

### **Saat Auto Typing:**
- Jangan menggerakkan mouse atau menggunakan keyboard selama proses berlangsung
- Pastikan tidak ada popup atau notifikasi yang menghalangi
- Monitor progress bar untuk tracking proses

### **Optimasi:**
- Gunakan "Submit Delay" yang cukup untuk loading form
- Disable field yang tidak diperlukan untuk mempercepat proses
- Gunakan pre-click buttons untuk navigasi otomatis

## Troubleshooting

### **Masalah Koordinat:**
- **Koordinat tidak akurat**: Set ulang koordinat dengan lebih teliti
- **Error "errno 2"**: Sudah diperbaiki dengan parsing koordinat yang benar
- **Field tidak terisi**: Pastikan koordinat sudah diset dan field di-enable

### **Masalah File:**
- **CSV tidak terdeteksi**: Pastikan file browser menampilkan "All supported files"
- **Leading zero hilang**: Sudah diperbaiki dengan pembacaan semua kolom sebagai string
- **Data tidak terbaca**: Cek format file dan encoding (gunakan UTF-8)

### **Masalah Proses:**
- **Proses terhenti**: Cek apakah form target masih aktif
- **Dropdown tidak berfungsi**: Konfigurasi ulang mapping dropdown
- **Custom column error**: Pastikan koordinat custom column sudah diset

### **Performance:**
- **Proses lambat**: Kurangi submit delay atau disable field yang tidak perlu
- **Memory usage tinggi**: Tutup aplikasi lain yang tidak diperlukan
- **Aplikasi freeze**: Restart aplikasi dan coba dengan data yang lebih kecil