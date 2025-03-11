import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor # type: ignore
from sklearn.ensemble import ( # type: ignore
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor 
) 
from sklearn.linear_model import LinearRegression # type: ignore
from sklearn.metrics import r2_score # type: ignore
from sklearn.neighbors import KNeighborsRegressor # type: ignore
from sklearn.tree import DecisionTreeRegressor # type: ignore
from xgboost import XGBRegressor # type: ignore

from src.exceptions import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_model

@dataclass
class ModelTrainerConfig:
    models_dir = os.path.join(os.getcwd(), "models")
    train_model_file_path = os.path.join(models_dir, "model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_coonfig = ModelTrainerConfig()

    def initiate_model_trainer(self, train_arr, test_arr):
        try:
            logging.info('Splitting training and testing data')
            X_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1]
            )

            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "K-Neigbour Regressor": KNeighborsRegressor(),
                "XGBRegressor": XGBRegressor(),
                "CatBossting Regressor": CatBoostRegressor(verbose = False),
                "AdaBoost Regressor": AdaBoostRegressor(),
            }

            params = {
                "Decision Tree": {
                    'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                 
                    # 'max_features':['sqrt','log2',None],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Gradient Boosting":{
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    # 'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Linear Regression":{},
                "XGBRegressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "CatBoosting Regressor":{
                    'depth': [6,8,10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },
                "AdaBoost Regressor":{
                    'learning_rate':[.1,.01,0.5,.001],
                    # 'loss':['linear','square','exponential'],
                    'n_estimators': [8,16,32,64,128,256]
                }
            }

            model_report:dict = evaluate_model(
                X_train = X_train, 
                y_train = y_train, 
                X_test = X_test, 
                y_test = y_test, 
                models = models,
                param = params
            )

            # To get best model score from dict
            best_model_score = max(sorted(model_report.values()))
            # To get best model name from the dict
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            if best_model_score < 0.6:
                raise CustomException("No best Model found")
            
            logging.info('Best found model on both training and testing dataset')

            save_object(
                file_path = self.model_trainer_coonfig.train_model_file_path,
                obj = best_model
            )

            predicted = best_model.predict(X_test)

            r2_score_value = r2_score(y_test, predicted)
            return r2_score_value

        except Exception as e:
            raise CustomException(e, sys)
