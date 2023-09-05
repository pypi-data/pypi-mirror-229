import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append('.')
from gender_local.src.gender_enum import GenderEnum as Enum
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
import os
from cv2 import VideoCapture, imwrite
import numpy as np
from numpy import expand_dims
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation
from tensorflow.keras.regularizers import l2
from gender_detection_local_python_package.gender_detection_local.src.image_manipulation import image_2_grayscale

logger = Logger()

FACIAL_ANALYSIS_LOCAL_COMPONENT_ID = 201
FACIAL_ANALYSIS_LOCAL_COMPONENT_NAME = "gender_detection_local_python_package/gender_detection_local/gender_detection.py"
INTERFACE_MODE = os.getenv("INTERFACE_MODE")


object_to_insert = {
    "component_id": FACIAL_ANALYSIS_LOCAL_COMPONENT_ID,
    "component_name": FACIAL_ANALYSIS_LOCAL_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": "yoav.e@circ.zone"
}

logger.init(
    "Start logging in {FACIAL_ANALYSIS_LOCAL_COMPONENT_NAME}", object=object_to_insert)


def create_model(input_shape: np.shape, learning_rate: float) -> Sequential:
    """
    Function to create a CNN model with multiple Convolutional, MaxPooling, and Dense layers. The model takes
    as input an image tensor of shape (input_shape) and outputs a prediction vector of shape (1,).

    Args:
        input_shape (tuple): A tuple representing the shape of input tensor of an image.
                             (height, width, channel)

    Returns:
        keras.Sequential: A compiled CNN model instance.
    """

    CREATE_MODEL = "create_model"
    logger.start(CREATE_MODEL, object={"input_shape": input_shape})
    CNNModel2 = Sequential([
        Conv2D(32, (3, 3), padding='same', strides=(1, 1),
               kernel_regularizer=l2(0.001), input_shape=input_shape),
        Dropout(0.1),
        Activation('relu'),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(64, (3, 3), padding='same', strides=(
            1, 1), kernel_regularizer=l2(0.001)),
        Dropout(0.1),
        Activation('relu'),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(128, (3, 3), padding='same', strides=(
            1, 1), kernel_regularizer=l2(0.001)),
        Dropout(0.1),
        Activation('relu'),
        MaxPooling2D(pool_size=(2, 2)),

        Conv2D(256, (3, 3), padding='same', strides=(
            1, 1), kernel_regularizer=l2(0.001)),
        Dropout(0.1),
        Activation('relu'),
        MaxPooling2D(pool_size=(2, 2)),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(2, activation="sigmoid")
    ])

    CNNModel2.compile(optimizer=Adam(learning_rate=learning_rate),
                      loss="binary_crossentropy", metrics=['accuracy'])

    logger.end(CREATE_MODEL)
    return CNNModel2


def capture_write(filename: str = "image.jpeg", port: int = 0, ramp_frames: int = 30, x: int = 178, y: int = 218) -> None:
    """
    Captures an image using the webcam and saves it to a file.

    Args:
        filename (str): The name of the file to save the image to. Default is "image.jpeg".
        port (int): The port number of the camera to use. Default is 0.
        ramp_frames (int): The number of frames to skip before capturing the image. Default is 30.
        x (int): The width of the image in pixels. Default is 178.
        y (int): The height of the image in pixels. Default is 218.

    Returns:
        numpy.ndarray: The captured image as a NumPy array.
    """

    CAPTURE_WRITE_FUNCTION_NAME = "capture_write()"
    logger.start(CAPTURE_WRITE_FUNCTION_NAME, object={
                 "filename": filename, "port": port, "ramp_frames": ramp_frames, "x": x, "y": y})

    # TODO: change this so the image saves at filename
    # camera = VideoCapture(port)
    camera = VideoCapture(port)

    # Set Resolution
    camera.set(3, x)
    camera.set(4, y)

    # Adjust camera lighting
    for _ in range(ramp_frames):
        _ = camera.read()
    _, im = camera.read()

    # Save the image to the current directory
    imwrite(filename, im)

    del (camera)
    logger.end(CAPTURE_WRITE_FUNCTION_NAME)


class GenderClassifier:
    def __init__(self):
        """
        GenderClassifier is a class that detects the gender of a person through webcam images.

        Args:
            train (bool): a boolean indicating whether to train the model or not. Defaults to False.
            predict (bool): a boolean indicating whether to predict the gender or not. Defaults to True.

        """

    def _get_prediction(self, model_prediction: np.array) -> str:
        GET_PREDICTION_FUNCTION_NAME = "_get_prediction()"
        logger.start(GET_PREDICTION_FUNCTION_NAME)

        inx = np.argmax(model_prediction)
        if inx == 0:
            prediction = Enum.MALE.value
        else:
            prediction = Enum.FEMALE.value

        logger.end(GET_PREDICTION_FUNCTION_NAME,
                   object={"prediction": prediction})
        return prediction

    def predict_gender(self, model_path: str, image_path: str = None) -> str:
        """
        This function captures an image from the webcam and predicts the gender of the person.

        Args:
            model_path (str): the path to the model file.
            image_path (str): the path to the image file. Defaults to None.
                              in which case the function will take a picture from the webcam.

        Returns:
            str: a string indicating the predicted gender ('Male' or 'Female').
        """

        PREDICT_GENDERER_FUNCTION_NAME = "predict_gender/()"
        logger.start(PREDICT_GENDERER_FUNCTION_NAME, object={
                     "model_path": model_path, "image_path": image_path})

        # Test Functionality
        if INTERFACE_MODE == "BATCH":
            # Read the contents of the image file
            image = image_2_grayscale(image_path)
        elif INTERFACE_MODE == "INTERACTIVE":
            # Permission to use webcam and work on singular image
            inquiry = input("""
            This script will take a picture with your webcam,
            this will only be for the purposes for determining your gender.
            Proceed? (Y/n) """)
            if inquiry.lower() != "y" and inquiry.lower != "yes":
                self.logger.info("\nAborting\n")
                self.logger.end(PREDICT_GENDERER_FUNCTION_NAME)
                exit()

            # Capture Image from Webcam
            capture_write()
            # Read the contents of the image file
            image = image_2_grayscale("image.jpeg")
        else:
            logger.exception(f"Invalid INTERFACE_MODE: {INTERFACE_MODE}")
            logger.end(PREDICT_GENDERER_FUNCTION_NAME)
            return None

        model = load_model(model_path)
        print(model.predict(expand_dims(image, axis=0)))
        predict_gender_result = self._get_prediction(
            model.predict(expand_dims(image, axis=0))[0])

        logger.end(PREDICT_GENDERER_FUNCTION_NAME, object={
                   "predict_gender_result": predict_gender_result})
        return predict_gender_result

    def train_model2(self, learning_rate: float = 5e-5,
                     epochs: int = 30, batch_size: int = 16,
                     save: bool = True, verbose=1) -> Sequential:
        """
        This function trains the model on the training data and saves the model to a file.
        Inputs:
            learning_rate (float): the learning rate of the Adam optimizer.
            Defaults to 1e-3.
            epochs (int): the number of epochs to train the model for. Defaults to 30.
            batch_size (int): the batch size to use for training. Defaults to 16.
            save (bool): a boolean indicating whether to save the model or not. Defaults to True.
            verbose (int): a number indicating whether to print the training progress or not.
            Defaults to 2.
            0 is no prints, 1 is progress bar,2 is one line per epoch.

        Saves:
            A trained model to a file.
        PRECONDITIONS:
            train_data.npy, train_labels.npy, test_data.npy, test_labels.npy must exis.
            please use extract_data.py to generate these files.
            this works only for the UDKFace dataset.
        """

        TRAIN_MODEL_FUNCTION_NAME = "train_model()"
        logger.start(TRAIN_MODEL_FUNCTION_NAME, object={"learning_rate": learning_rate,
                     "epochs": epochs, "batch_size": batch_size, "save": save, "verbose": verbose})
        try:
            train_data = np.load('train_data.npy')
            train_labels = np.load('train_labels.npy')
            test_data = np.load('test_data.npy')
            test_labels = np.load('test_labels.npy')
        except Exception as e:
            logger.exception(
                "Please make sure all the data files exists:\n" +
                f"train_data.npy\ntrain_labels.npy\ntest_data.npy\ntest_labels.npy\n\nGot error: {e}"
            )
            logger.end(TRAIN_MODEL_FUNCTION_NAME)
            return None

        # shuffle the data but keep the labels in the same order
        p = np.random.permutation(len(train_data))
        train_data = train_data[p]
        train_labels = train_labels[p]

        p = np.random.permutation(len(test_data))
        test_data = test_data[p]
        test_labels = test_labels[p]

        model = create_model((100, 100, 1), learning_rate=learning_rate)

        model.fit(train_data, train_labels, epochs=epochs, batch_size=batch_size,
                  validation_data=(test_data, test_labels), verbose=verbose)
        if save:
            model.save("./gender_detection_local_python_package/gender_detection",
                       save_format='h5')

        # evaluate the model on the test set
        loss, acc = model.evaluate(test_data, test_labels, verbose=verbose)
        logger.info(f"Test loss: {loss}")
        logger.info(f"Test accuracy: {acc}")

        # this is just for until I will have access to the logger:
        print("Test loss: ", loss)
        print("Test accuracy: ", acc)
        logger.end(TRAIN_MODEL_FUNCTION_NAME)
        return model

    def load_model(path_to_model="gender_detection_local_python_package/gender_detection"):
        LOAD_MODEL_FUNCTION_NAME = "load_model()"
        logger.start(LOAD_MODEL_FUNCTION_NAME, object={
                     "path_to_model": path_to_model})

        try:
            model = load_model(path_to_model)
        except Exception as e:
            logger.exception(f"Failed to load model, got error: {e}")

        logger.end(LOAD_MODEL_FUNCTION_NAME)
        return model
