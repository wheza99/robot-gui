import pandas as pd

# Membuat contoh data untuk testing
data = {
    'Nama Lengkap': [
        'Ahmad Budi Santoso',
        'Siti Nurhaliza',
        'Dedi Kurniawan',
        'Maya Sari Dewi',
        'Rizki Pratama'
    ],
    'NIK': [
        '3201234567890123',
        '3301234567890124',
        '3401234567890125',
        '3501234567890126',
        '3601234567890127'
    ],
    'Email': [
        'ahmad.budi@email.com',
        'siti.nurhaliza@email.com',
        'dedi.kurniawan@email.com',
        'maya.sari@email.com',
        'rizki.pratama@email.com'
    ],
    'Nomor Telepon': [
        '081234567890',
        '082345678901',
        '083456789012',
        '084567890123',
        '085678901234'
    ],
    'Jenis Kelamin': [
        'Laki-laki',
        'Perempuan',
        'Laki-laki',
        'Perempuan',
        'Laki-laki'
    ],
    'Nomor KK': [
        '3201234567890001',
        '3301234567890002',
        '3401234567890003',
        '3501234567890004',
        '3601234567890005'
    ],
    'Bidang Ajar': [
        'Matematika',
        'Bahasa Indonesia',
        'Fisika',
        'Kimia',
        'Biologi'
    ]
}

# Membuat DataFrame
df = pd.DataFrame(data)

# Simpan ke file Excel
df.to_excel('contoh_data.xlsx', index=False)
print("File contoh_data.xlsx berhasil dibuat!")
print("\nData yang dibuat:")
print(df.to_string(index=False))