
import os, sys
from .download import *
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


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

destination_folder = current + '/model'
url = "https://drive.google.com/file/d/1vVOX3Zveu-CWTCJPXjZnI7p_2QslxZ9H/view"
zip_password = "AxL8tLAsCujpYxaYLupY"

db_folder = os.path.abspath("data/database")
images_folder = os.path.abspath("data/images")

download.check_model(destination_folder, url, zip_password)

tera_detector_weights = current + '/model/tera_object_n1.pt'
tera_plate_detector_weights = current + '/model/detect_plat_v6.pt'
segmentation_weights = current + '/model/yolo_segmentation_plat_n.pt'
classification_weights = current + '/model/clasisification_plate_n.pt'
ocr_recognition_model_dir = current + '/model/ocr/recognition'
ocr_detection_model_dir = current + '/model/ocr/detection'
character_dict_path = current + '/utils/en_dict.txt'

detector = Detektor(tera_detector_weights)
detector_kendaraan = Detektor(tera_detector_weights)
segmentasi = Segmentasi(segmentation_weights)
klasifikasi = Klasifikasi(classification_weights)
ocr = Ocr(ocr_recognition_model_dir, ocr_detection_model_dir, character_dict_path)

if not os.path.exists(db_folder):
    os.makedirs(db_folder)

if not os.path.exists(images_folder):
    os.makedirs(images_folder)