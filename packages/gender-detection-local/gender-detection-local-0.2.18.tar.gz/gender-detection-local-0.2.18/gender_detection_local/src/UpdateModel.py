import sys
import os
sys.path.append(os.getcwd())
from gender_detection_local_python_package.gender_detection_local.src.gender_detection import GenderClassifier

if __name__=="__main__":
    
    #if models directory is not empty create and train a model
    model = GenderClassifier()
    try:
        model.load_model()
    except:
        model.train_model()
        model.save_model()
    