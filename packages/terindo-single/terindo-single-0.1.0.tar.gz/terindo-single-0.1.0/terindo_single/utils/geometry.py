import numpy as np
import cv2

def order_points(pts):
    """
    Generate a function comment for the given function body.

    Parameters:
    - pts: a numpy array of shape (N, 2), representing the coordinates of N points

    Returns:
    - rect: a numpy array of shape (4, 2), representing the ordered points
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    """
    Apply a four-point perspective transform to an image.

    Parameters:
    - image: The input image to be transformed.
    - pts: The four points defining the original perspective.

    Returns:
    - warped: The transformed image.

    This function takes an input image and four points defining the original perspective. It applies a four-point perspective transform to the image and returns the transformed image. The four points should be provided in the order: top-left, top-right, bottom-right, and bottom-left.

    The function first orders the points in the correct order using the 'order_points' function. Then it calculates the width and height of the transformed image based on the distances between the ordered points. The maximum width and height are then used to create a destination array of four points. The 'getPerspectiveTransform' function is used to calculate the perspective transform matrix, and the 'warpPerspective' function is used to apply the transform to the input image.

    The transformed image is returned as the output of the function.
    """
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped
