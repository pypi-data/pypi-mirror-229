
import sqlite3
import os
from datetime import datetime

def create_database_if_not_exists(database_path):
    """
    Create a database if it does not already exist.

    Parameters:
    - database_path (str): The path to the database file.

    Returns:
    - None

    Raises:
    - None
    """
    if not os.path.exists(database_path):
        # Jika database belum ada, maka buatlah
        conn = sqlite3.connect(database_path)
        conn.close()
        print(f"Database '{database_path}' telah berhasil dibuat.")

def create_kendaraan_table_if_not_exists(database_path):
    """
    Creates a table named "kendaraan" in the specified database if it does not already exist.

    Parameters:
        - database_path (str): The path to the database file.

    Returns:
        None
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Tambahkan kode SQL untuk membuat tabel "kendaraan" jika belum ada
    cursor.execute('''CREATE TABLE IF NOT EXISTS kendaraan (
                        id INTEGER PRIMARY KEY,
                        nopol TEXT,
                        jenis_kendaraan TEXT,
                        status_uji_emisi TEXT,
                        tanggal_kadaluarsa TEXT,
                        waktu_cek_terakhir TEXT
                    )''')

    conn.commit()
    conn.close()

def insert_kendaraan_data(database_path, kendaraan_data):
    """
    Inserts kendaraan data into the database.

    Parameters:
    - database_path (str): The path to the database.
    - kendaraan_data (list): A list of tuples containing the data to be inserted into the 'kendaraan' table. Each tuple should contain the following values in order: nopol (str), jenis_kendaraan (str), status_uji_emisi (str), tanggal_kadaluarsa (str), waktu_cek_terakhir (str).

    Returns:
    - None

    Prints a success message after the data is inserted into the 'kendaraan' table.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for data in kendaraan_data:
        cursor.execute("INSERT INTO kendaraan (nopol, jenis_kendaraan, status_uji_emisi, tanggal_kadaluarsa, waktu_cek_terakhir) VALUES (?, ?, ?, ?, ?)", data)

    conn.commit()
    conn.close()
    print("Data kendaraan telah berhasil dimasukkan ke dalam tabel 'kendaraan'.")

def check_kadaluarsa(database_path, nopol):
    """
    Check the expiration status of a vehicle based on its license plate number.
    
    Args:
        database_path (str): The path to the SQLite database.
        nopol (str): The license plate number of the vehicle.
    
    Returns:
        tuple: A tuple with the following values:
            - bool: The expiration status of the vehicle. True if the vehicle is not expired, False otherwise.
            - str or None: The expiration date of the vehicle in string format ("%Y-%m-%d") if the vehicle is not expired, None otherwise.
            - str or None: The type of the vehicle if the vehicle is not expired, None otherwise.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Cari data kendaraan berdasarkan nomor polisi (nopol)
    cursor.execute("SELECT tanggal_kadaluarsa, jenis_kendaraan FROM kendaraan WHERE nopol = ?", (nopol,))
    result = cursor.fetchone()

    if result:
        tanggal_kadaluarsa_str = result[0]
        jenis_kendaraan = result[1]
        tanggal_kadaluarsa = datetime.strptime(tanggal_kadaluarsa_str, "%Y-%m-%d").date()
        today = datetime.now().date()

        if tanggal_kadaluarsa > today:
            print("Status: True")
            print(f"Nomor Polisi: {nopol}")
            print(f"Tanggal Kadaluarsa: {tanggal_kadaluarsa_str}")
            return True, tanggal_kadaluarsa_str, jenis_kendaraan
        else:
            print("Status: False (Kadaluarsa)")
            return False, None, None
    else:
        print(f"Nomor Polisi '{nopol}' tidak ditemukan dalam database.")
        return False, None, None

def check_and_delete_expired_data(database_path):
    """
    Check and delete expired data from the database.
    
    Parameters:
        database_path (str): The path to the database file.
    
    Returns:
        None
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Ambil semua data dari tabel kendaraan
    cursor.execute("SELECT nopol, tanggal_kadaluarsa FROM kendaraan")
    rows = cursor.fetchall()

    today = datetime.now().date()

    for row in rows:
        nopol = row[0]
        tanggal_kadaluarsa_str = row[1]
        tanggal_kadaluarsa = datetime.strptime(tanggal_kadaluarsa_str, "%Y-%m-%d").date()

        if tanggal_kadaluarsa <= today:
            print(f"Menghapus data dengan nomor polisi '{nopol}' (Kadaluarsa: {tanggal_kadaluarsa_str})")
            cursor.execute("DELETE FROM kendaraan WHERE nopol = ?", (nopol,))
    
    conn.commit()
    conn.close()
    print("Pemeriksaan dan penghapusan data kadaluarsa telah selesai.")