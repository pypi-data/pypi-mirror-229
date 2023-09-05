from gender_detection import GenderClassifier


if __name__ == "__main__":
    model=GenderClassifier()
    result=model.predict_gender(model_path="CirclesGenderDetectionPython/gender_detection")
    print(result)
    