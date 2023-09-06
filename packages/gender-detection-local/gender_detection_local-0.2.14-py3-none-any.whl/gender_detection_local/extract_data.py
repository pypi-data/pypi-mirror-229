import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append('.')
from gender_detection_local_python_package.gender_detection_local.src.image_manipulation import image_2_grayscale
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from typing import Callable
import os
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

DATA_EXTRACTOR_COMPONET_ID = 203
DATA_EXTRACTOR_COMPONENT_NAME = "gender_detection_local_python_package/gender_detection_local/src/extract_data.py"

object_to_insert = {
    "component_id": DATA_EXTRACTOR_COMPONET_ID,
    "component_name": DATA_EXTRACTOR_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "yoav.e@circ.zone"
}

logger = Logger()
logger.init(
    "Start logging in {DATA_EXTRACTOR_COMPONENT_NAME}", object=object_to_insert)


def process_dataset(dataset_path: str, num_classes: int, classifier: Callable[[str], int],
                    process_image: Callable[[str], np.ndarray] = image_2_grayscale,
                    test_size: int = 0.2, random_state: int = 42) -> None:
    """
    Processes a dataset of images and saves them as a numpy array, along with their labels.
    Inputs:
        dataset_path (str): Path to the UTKFace dataset directory.
        num_classes (int): Number of classes in the dataset.
        gender_classifier(str -> int): a function that gets a path to an
        image and returns the gender in binary (0 is male)
        process_image(str -> np.ndarray): a function that gets a path to a image
        and processes it to a numpy array (default is image_2_grayscale)
        test_size (float): Fraction of the dataset to be used as test data.
        random_state (int): Controls the shuffling applied to the data before applying the split.

    Outputs:
        None

    Summary:
        This function is used for for processing a dataset for classification.

        Tensorflow requires us to submit inputs in the form of np arrays,
        so in order to train a model on our data
        we need to convert the images to np arrays and save
        them along with their labels.

        This function effectively does the following:
            given a jpg data set D,
            transforms D -> process_image(D),
            splits process_image(D) into train and test sets,
            saves train and test sets as numpy arrays.

    """

    # Call logger
    PROCESS_DATASET_FUNCTION_NAME = "process_dataset()"
    logger.start(PROCESS_DATASET_FUNCTION_NAME, object={
                 "dataset_path": dataset_path, "test_size": test_size, "random_state": random_state})

    # Create empty lists to store data and labels
    data = []
    labels = []

    images = os.listdir(dataset_path)
    # shuffle the images
    np.random.shuffle(images)

    # Iterate over image files in the dataset directory
    for filename in tqdm(images):
        if filename.endswith('.jpg'):
            # Extract gender information from the filename
            gender = classifier(filename)

            gender_label = [0.] * num_classes
            gender_label[gender] = 1.

            # Load and preprocess image
            image_path = os.path.join(dataset_path, filename)
            image = process_image(image_path)

            # Append image and label to lists
            data.append(image)
            labels.append(gender_label)

    # Convert lists to numpy arrays
    data = np.array(data)
    labels = np.array(labels)

    # Split data into train and test sets
    train_data, test_data, train_labels, test_labels = train_test_split(
        data, labels, test_size=test_size, random_state=random_state)

    # Save train and test data as numpy arrays
    np.save('train_data.npy', train_data)
    np.save('train_labels.npy', train_labels)
    np.save('test_data.npy', test_data)
    np.save('test_labels.npy', test_labels)

    # Call logger
    logger.end(PROCESS_DATASET_FUNCTION_NAME)


def utk_classefier(filename: str) -> int:
    return int(filename.split('_')[1])
