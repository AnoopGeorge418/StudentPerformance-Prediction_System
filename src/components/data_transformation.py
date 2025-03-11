import os
import sys
import numpy as np # type: ignore
import pandas as pd # type: ignore
from dataclasses import dataclass
from sklearn.compose import ColumnTransformer # type: ignore
from sklearn.impute import SimpleImputer # type: ignore
from sklearn.pipeline import Pipeline # type: ignore
from sklearn.preprocessing import OneHotEncoder, StandardScaler # type: ignore

from src.exceptions import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    models_dir = os.path.join(os.getcwd(), "models")
    preprocessor_obj_file_path = os.path.join(models_dir, "preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        try:
            numerical_features  = ['writing_score', 'reading_score']
            categorical_features = [
                'gender', 'race_ethnicity', 'parental_level_of_education', 'lunch', 'test_preparation_course'
            ]

            numerical_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('one_hot_encoder', OneHotEncoder()),
                ('scaler', StandardScaler(with_mean=False)) 
            ])

            preprocessor = ColumnTransformer([
                ('numerical_pipeline', numerical_pipeline, numerical_features),
                ('categorical_pipeline', categorical_pipeline, categorical_features)
            ])
            return preprocessor
        
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_dataTransformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info("Read train and test data")

            preprocessor_objects = self.get_data_transformer_object()
            target_column = 'math_score'

            input_features_train_df = train_df.drop(columns=[target_column], axis=1)
            target_feature_train_df = train_df[target_column]

            input_features_test_df = test_df.drop(columns=[target_column], axis=1)
            target_feature_test_df = test_df[target_column]

            input_feature_train_arr = preprocessor_objects.fit_transform(input_features_train_df)
            input_feature_test_arr = preprocessor_objects.transform(input_features_test_df)  

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info('Object has been saved')
            os.makedirs(self.data_transformation_config.models_dir, exist_ok=True)  
            save_object(self.data_transformation_config.preprocessor_obj_file_path, preprocessor_objects)

            return train_arr, test_arr, self.data_transformation_config.preprocessor_obj_file_path
        
        except Exception as e:
            raise CustomException(e, sys)
