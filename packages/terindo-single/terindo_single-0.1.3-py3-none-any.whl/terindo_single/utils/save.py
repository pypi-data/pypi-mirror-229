import os
import cv2

def save_image(folder_name, image_kendaraan, image_plate, file_name, plat, compress_size=0.5):
    """
    Save an image to a specified folder with a given file name and compression size.

    Parameters:
        folder_name (str): The name of the folder where the image will be saved.
        image_kendaraan (numpy.ndarray): The cropped vehicle image to be saved.
        image_plate (numpy.ndarray): The segmented plate image to be saved.
        file_name (str): The name of the file to be saved.
        plat (str): The plate number associated with the image.
        compress_size (float, optional): The compression size for the cropped vehicle image. Defaults to 0.5.

    Returns:
        None
    """
    # Membuat folder jika belum ada
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Menyimpan gambar crop kendaraan dengan kompresi
    cropped_vehicle_path = os.path.join(folder_name, f'{file_name}_{plat}_kendaraan.jpg')
    cv2.imwrite(cropped_vehicle_path, image_kendaraan, [int(cv2.IMWRITE_JPEG_QUALITY), int(100 * compress_size)])
    
    # Menyimpan segmented image plat tanpa kompresi
    plate_path = os.path.join(folder_name, f'{file_name}_{plat}_plate.jpg')
    cv2.imwrite(plate_path, image_plate)
    
    # print(f'Gambar crop kendaraan disimpan di: {cropped_vehicle_path}')
    # print(f'Segmented image plat disimpan di: {plate_path}')