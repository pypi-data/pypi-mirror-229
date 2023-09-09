# Circles Gender Detection Python App

This project is designed for gender detection using images of faces. It contains scripts for extracting data from the UDKFace database, training the gender detection model, and performing gender predictions on new images.


## Usage Cases

### 1. Extracting Data from UDKFace Database

To extract data from the UDKFace database,follow these steps:

1. Make sure you have a directory containing images from the database, link https://www.kaggle.com/datasets/jangedoo/utkface-new
2. Edit the `extract_data.py` file and call its main function, passing the directory name.
3. Run the script. It will process the images and save the data in a numpy format.

### 2. Training the Model

Before training the model, ensure you have the necessary data in numpy format (possibly obtained from the extraction step).

To train the model, follow these steps:

1. Run the `UpdateModel.py` script.
2. You can specify parameters like learning rate, epochs, and batch size.
3. The script will retrain the model using the provided data.

### 3. Gender Detection

To perform gender detection on new images, use the `gender_detection.py` script. Follow these steps:

1. Make sure to run `pip install -r requirements.txt` to install required packages.
2. Use the `predict` function in `gender_detection.py`, passing a link to a face image.
3. The function will use the trained model to predict and return "male" or "female".


## Environment Variables

Before running the scripts, make sure to set the following environment variables:

- `LOGZIO_TOKEN`: The Logz.io token for logging and monitoring.

To set these variables, create a `.env` file in the project root directory and add the variable assignments there:

```plaintext
LOGZIO_TOKEN=your-logzio-token
INTERFACE_MODE=INTERACTIVE || BATCH
```

where **INTERACTIVE** is for using the camera for the input image,
and **BATCH** is for using a directory of images for the input image.


## Model Architecture

```python
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

