from skopt import forest_minimize
import functions
import models
import settings
import variables
import pandas as pd
from scipy.sparse import hstack


def extract_train_test_data():
    """Retrieve data and train/test masks."""
    mask_train_test = settings.getMaskTrainTest(variables.mlData['cleanedData'])
    x_train = variables.mlData['features'][mask_train_test['maskTrain']]
    x_test = variables.mlData['features'][mask_train_test['maskTest']]
    y_train = variables.mlData['y'][mask_train_test['maskTrain']]
    y_test = variables.mlData['y'][mask_train_test['maskTest']]
    return x_train, x_test, y_train, y_test, mask_train_test


def preprocess_text_data(x_train, x_test, mask_train_test, min_df, ngram_range):
    """Process and merge text data with features."""
    tfidf_vec, title_bow_train, title_bow_test = functions.dataFromText(
        variables.mlData['cleanedData']['title'],
        mask_train_test['maskTrain'],
        mask_train_test['maskTest'],
        {'min_df': min_df, 'ngram_range': ngram_range}
    )

    x_train = hstack([x_train, title_bow_train]) if hasattr(x_train, 'shape') else pd.concat([x_train, title_bow_train], axis=1)
    x_test = hstack([x_test, title_bow_test]) if hasattr(x_test, 'shape') else pd.concat([x_test, title_bow_test], axis=1)
    
    return x_train, x_test


def run_lgbm_model(x_train, y_train, x_test, y_test, params):
    """Train and evaluate the LGBM model."""
    model, prob, aps, roc_auc = models.lgbmWMetrics(
        x_train, y_train, x_test, y_test,
        2 ** params['max_depth'], params['learning_rate'], params['max_depth'],
        params['min_child_samples'], params['subsample'], params['colsample_bytree'],
        params['n_estimators']
    )
    print(f"APS: {aps}, ROC AUC: {roc_auc}")
    return -aps


def lgbm_target_function(params):
    """Objective function for hyperparameter optimization."""
    print(f"Params: {params}")
    
    # Retrieve and preprocess data
    x_train, x_test, y_train, y_test, mask_train_test = extract_train_test_data()
    x_train, x_test = preprocess_text_data(x_train, x_test, mask_train_test, params['min_df'], (1, params['ngram_range']))

    # Evaluate model
    return run_lgbm_model(x_train, y_train, x_test, y_test, params)


def optimize_lgbm(space):
    """Optimize LGBM hyperparameters."""
    result = forest_minimize(
        lgbm_target_function, space, random_state=160745, 
        n_random_starts=20, n_calls=50, verbose=1
    )
    return result.x, result.fun
