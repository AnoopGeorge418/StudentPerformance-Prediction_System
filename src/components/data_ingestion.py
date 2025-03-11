import os
import sys
import numpy as np # type: ignore
import pandas as pd # type: ignore
from dataclasses import dataclass # type: ignore
from sklearn.model_selection import train_test_split # type: ignore

from src.exceptions import CustomException
from src.logger import logging
from src.components.data_transformation import DataTransformation, DataTransformationConfig  # ✅ Fixed import

@dataclass
class DataIngestionConfig:
    artifacts_dir = os.path.join(os.getcwd(), "artifacts")
    train_data_path: str = os.path.join(artifacts_dir, "train.csv")
    test_data_path: str = os.path.join(artifacts_dir, "test.csv")
    raw_data_path: str = os.path.join(artifacts_dir, "raw.csv")

class DataIngestion:
    def __init__(self):
        self.ingestionConfig = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered the data ingestion method")
        try:
            data_path = os.path.join(os.getcwd(), "src", "data", "students_data.csv")
            df = pd.read_csv(data_path)
            logging.info("Read the dataset as a DataFrame")

            os.makedirs(os.path.dirname(self.ingestionConfig.train_data_path), exist_ok=True)
            logging.info("Artifacts folder has been created")
            df.to_csv(self.ingestionConfig.raw_data_path, index=False, header=True)

            logging.info("Train Test Split Initiated")
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
            train_set.to_csv(self.ingestionConfig.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestionConfig.test_data_path, index=False, header=True)
            logging.info("Ingestion of data has been completed")

            return self.ingestionConfig.train_data_path, self.ingestionConfig.test_data_path
        except Exception as e:
            logging.error(f"Error during data ingestion: {str(e)}")
            raise CustomException(e, sys)

def run_data_ingestion():
    obj = DataIngestion()
    train_data, test_data = obj.initiate_data_ingestion()
    data_transformation = DataTransformation()
    data_transformation.initiate_dataTransformation(train_data, test_data)

if __name__ == "__main__":
    run_data_ingestion()
