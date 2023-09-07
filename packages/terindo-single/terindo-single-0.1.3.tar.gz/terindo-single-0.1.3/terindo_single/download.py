import os
import requests
import zipfile
import pyzipper
import gdown
import sys

def download_from_google_drive(gdrive_url, output_path):
    # Extract the file ID from the Google Drive link
    file_id = gdrive_url.split("/")[-2]

    # Create the download URL
    download_url = f"https://drive.google.com/uc?id={file_id}"

    # Download the file
    gdown.download(download_url, output_path, quiet=False)
    
def check_model(destination_folder, url, zip_password):
    if not os.path.exists(destination_folder):
        # Membuat folder tujuan jika belum ada
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            
        # Jika folder modul tidak ada, unduh data dari URL
        print(f"Downloading data..... ")
        
        try:
            if "drive.google.com" in url:
                # Jika URL adalah Google Drive link, gunakan fungsi download_from_google_drive
                gdrive_url = url
                zip_file_path = os.path.join(destination_folder, 'data.zip')
                download_from_google_drive(gdrive_url, zip_file_path)
            else:
                response = requests.get(url)
                response.raise_for_status()
                zip_file_path = os.path.join(destination_folder, 'data.zip')
                with open(zip_file_path, 'wb') as zip_file:
                    zip_file.write(response.content)
            
            # Ekstrak data dari file zip (jika ada kata sandi)
            if zip_password:
                try:
                    with pyzipper.AESZipFile(zip_file_path) as zf:
                        zf.pwd = zip_password.encode()  # Set the password
                        zf.extractall(destination_folder)
                except pyzipper.BadPassword:
                    sys.exit(1)
                except Exception as e:
                    sys.exit(1)
            else:
                try:
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        zip_ref.extractall(destination_folder)
                except zipfile.BadZipFile as e:
                    sys.exit(1)
            
            # Hapus file zip setelah diekstrak
            os.remove(zip_file_path)
        except requests.exceptions.RequestException as e:
            sys.exit(1)
