
import os
import requests
import zipfile
import pyzipper
import gdown
class Paths:
    tera_detector_weights ='./model/tera_object_n1.pt' 
    tera_plate_detector_weights = './model/detect_plat_v6.pt'
    segmentation_weights = './model/yolo_segmentation_plat_n.pt'
    classification_weights = './model/clasisification_plate_n.pt'
    ocr_recognition_model_dir = './model/ocr/recognition'
    ocr_detection_model_dir = './model/ocr/detection'
    character_dict_path = './utils/en_dict.txt'
    
from .detektor_single import Detektor
from .segmentasi import Segmentasi
from .klasifikasi import Klasifikasi
from .ocr import Ocr
from .emisi import EmisiChecker
from .utils.save import save_image
from .utils.sqldata import (
    create_database_if_not_exists,
    create_kendaraan_table_if_not_exists,
    check_and_delete_expired_data,
    check_kadaluarsa,
    insert_kendaraan_data,
)


destination_folder = './model'
url = "https://drive.google.com/file/d/1vVOX3Zveu-CWTCJPXjZnI7p_2QslxZ9H/view"
zip_password = "AxL8tLAsCujpYxaYLupY"

def download_from_google_drive(gdrive_url, output_path):
    # Extract the file ID from the Google Drive link
    file_id = gdrive_url.split("/")[-2]

    # Create the download URL
    download_url = f"https://drive.google.com/uc?id={file_id}"

    # Download the file
    gdown.download(download_url, output_path, quiet=False)
    
if not os.path.exists(destination_folder):
    # Membuat folder tujuan jika belum ada
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        
    # Jika folder modul tidak ada, unduh data dari URL
    print(f"Folder '{destination_folder}' not found. Downloading data...")
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
                print("Incorrect password. Failed to unzip the file.")
            except Exception as e:
                print(f"An error occurred while unzipping the file: {e}")
        else:
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(destination_folder)
            except zipfile.BadZipFile as e:
                print(f"Failed to extract data from {zip_file_path}: {e}")
        
        # Hapus file zip setelah diekstrak
        os.remove(zip_file_path)
        
        print("Data has been downloaded and extracted.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download data from {url}: {e}")
else:
    print(f"Folder '{destination_folder}' already exists. No need to download data.")



detector = Detektor(Paths.tera_detector_weights)
detector_kendaraan = Detektor(Paths.tera_detector_weights)
segmentasi = Segmentasi(Paths.segmentation_weights)
klasifikasi = Klasifikasi(Paths.classification_weights)
ocr = Ocr(Paths.ocr_recognition_model_dir, Paths.ocr_detection_model_dir, Paths.character_dict_path)



