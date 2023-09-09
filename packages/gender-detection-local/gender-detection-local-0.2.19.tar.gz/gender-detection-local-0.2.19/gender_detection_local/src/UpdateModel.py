import sys
import os
sys.path.append(os.getcwd())
from gender_detection_local_python_package.gender_detection_local.src.gender_detection import GenderClassifier
from gender_detection_local_python_package.gender_detection_local.src.extract_data import process_dataset, utk_classefier
if __name__=="__main__":
    
    #if models directory is not empty create and train a model
    model = GenderClassifier()
    try:
        model.load_model()
    except:
        #for this to work you HAVE to have the UTKFace dataset in the same directory as this file,
        # the name of the directory should be UTKFace
        
        process_dataset(
            dataset_path="UTKFace",
            num_classes=2,
            classifier=utk_classefier,
        )
        model.train_model2()
    