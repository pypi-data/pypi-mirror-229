import cv2
from dotenv import load_dotenv
load_dotenv()
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger

DATA_EXTRACTOR_COMPONET_ID = 204
DATA_EXTRACTOR_COMPONENT_NAME = \
    "gender_detection_local_python_package/gender_detection_local/image_manipulation.py"

object_to_insert = {
    "component_id": DATA_EXTRACTOR_COMPONET_ID,
    "component_name": DATA_EXTRACTOR_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "yoav.e@gmail.com"
}

logger = Logger()
logger.init(
    "Start logging in {DATA_EXTRACTOR_COMPONENT_NAME}", object=object_to_insert)


def image_2_grayscale(image_path: str, desired_size=(100, 100)):
    """
    Converts an image to grayscale and resizes it to a desired size defult is (100,100)

    Parameters
    ----------
    image_path : str
        Path to the image
    desired_size : tuple
        Desired size of the image

    Returns
    -------
    image : numpy.ndarray
        Grayscale image
    """

    IMAGE_2_GRAYSCALE_FUNCTION_NAME = "image_2_grayscale()"
    logger.start(IMAGE_2_GRAYSCALE_FUNCTION_NAME, object={
                 "image_path": image_path, "desired_size": desired_size})

    # Load image
    image = cv2.imread(image_path)
    # Convert image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Resize image
    image = cv2.resize(image, desired_size)

    logger.end(IMAGE_2_GRAYSCALE_FUNCTION_NAME)
    return image
