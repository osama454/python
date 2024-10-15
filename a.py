from skopt import forest_minimize
import functions
import models
import settings
import variables

NGRAM_RANGE = (1, 2)  # Hardcoded ngram_range


def _prepare_data(min_df):
    """Prepares data for model training and testing."""
    mask_train_test = settings.getMaskTrainTest(variables.mlData['cleanedData'])
    x_train, x_test = variables.mlData['features'][mask_train_test['maskTrain']], variables.mlData['features'][mask_train_test['maskTest']]
    y_train, y_test = variables.mlData['y'][mask_train_test['maskTrain']], variables.mlData['y'][mask_train_test['maskTest']]

    t_fid_vec, title_bow_train, title_bow_test = functions.dataFromText(
        variables.mlData['cleanedData']['title'], 
        mask_train_test['maskTrain'], 
        mask_train_test['maskTest'], 
        {'min_df': min_df, 'ngram_range': NGRAM_RANGE}
    )

    x_train = functions.mergeDataFrames(x_train, title_bow_train)
    x_test = functions.mergeDataFrames(x_test, title_bow_test)
    return x_train, y_train, x_test, y_test


def _evaluate_model(x_train, y_train, x_test, y_test, parameters):
    """Trains and evaluates the LGBM model."""
    learning_rate, max_depth, min_child_samples, subsample, colsample_bytree, n_estimators, min_df = parameters

    model, prob, aps, roc_auc = models.lgbmWMetrics(
        x_train, y_train, x_test, y_test, 
        2**max_depth, learning_rate, max_depth, min_child_samples, 
        subsample, colsample_bytree, n_estimators
    )

    print(f"Parameters: {parameters}")
    print(f"APS: {aps}")
    print(f"ROC AUC: {roc_auc}")

    return -aps


def _lgbm_target_function(parameters):
    """Target function for optimization."""

    x_train, y_train, x_test, y_test = _prepare_data(parameters[6])
    return _evaluate_model(x_train, y_train, x_test, y_test, parameters)



def optimize_lgbm(space):
    """Optimizes LGBM model using forest minimization."""
    result = forest_minimize(_lgbm_target_function, space, random_state=160745, n_random_starts=20, n_calls=50, verbose=1)
    return result.x, result.fun
