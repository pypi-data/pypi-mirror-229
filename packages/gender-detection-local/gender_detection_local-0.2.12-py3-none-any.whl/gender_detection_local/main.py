from gender_detection_local_python_package.gender_detection_local.src.gender_detection import GenderClassifier


if __name__ == "__main__":
    model = GenderClassifier()
    result = model.predict_gender(
        model_path="gender_detection_local_python_package/gender_detection")
    print(result)
