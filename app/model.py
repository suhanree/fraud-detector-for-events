# Here we build a model, and predict.

import pandas as pd
import numpy as np
import json
import os
import cPickle as pickle

from sklearn.ensemble import RandomForestClassifier

# Filenames for our train/test sets.
filename_train = 'data/train_new.json'
filename_test = 'data/test_new.json'

# Filename for the pickle object.
filename_pickle = 'data/model.pkl'


def convert_to_float(s):
    """
    Convert string to float (if not convertible, return None).
    """
    try:
        return float(s)
    except TypeError:
        return None


def preprocess(old_df, label_name, category_features, non_category_features):
    """
    Preprocess the old data frame, and produce the new data frame.
    Input:
        old_df: data frame to preprocess.
        label_name: column name for the targe feature.
        category_features: list of column names for category features.
        non_category_features: list of column names for non-category features.
    Output:
        new_df: data frame newly created.
    """
    old_df['fraud'] = old_df[label_name].apply(lambda x: x[0] == 'f')

    # Creating a new dataframe with a subset of features.
    new_df = old_df[['fraud'] + non_category_features]

    # For categorical features, we make dummy variables,
    # and merge them into new_df.
    for feature in category_features:
        dummy_df = pd.get_dummies(old_df[feature], prefix=feature,
                                  dummy_na=True)
        # Since dummy_na=True, the last column will be for null values.
        dummy_df.drop(dummy_df.columns[-1], axis=1, inplace=True)
        new_df = pd.concat([new_df, dummy_df], axis=1)
    return new_df


def read_data(all=True):
    """
    Read the data.
    Input: 
        all: if True, read all data; if False, read only train data.
    Output:
        train_df: data frame for train set
        test_df: data frame for test set
    """
    # Reading the train/test data as data frames.     
    train_df = pd.read_json(filename_train)
    if all:
        test_df = pd.read_json(filename_test)
    else:
        test_df = None
    return train_df, test_df


def buildmodel(label_name, category_features, non_category_features,
               model=None, save=True):
    """
    Model is built here.
    Input:
        label_name: column name for the targe feature.
        category_features: list of column names for category features.
        non_category_features: list of column names for non-category features.
        model: chosen model object (default: None, RandomRorest will be used).
        save: if True, save the pickle object as a file (default: True)
    Output:
        model: returns the fitted model (it will be saved as pickle object
            as '/data/model.pkl') (And the model object will be stored, too.)
        final_columns: list of names for final columns.
        averages: dictionary of averages for non-category features.
    """
    # Reading the train/test data as data frames.
    train_df, test_df = read_data()
    whole_df = pd.concat([train_df, test_df])

    # Preprocess the data frame.
    new_df = preprocess(whole_df, label_name, category_features, non_category_features)

    # Names of final columns
    final_columns = new_df.columns[1:]

    # Find averages for non-category features.
    averages = {}
    for col in non_category_features:
        averages[col] = new_df[col].mean()

    # Dropping na's
    new_df = new_df.dropna()

    # getting X & y for the train set
    y = np.array(new_df.fraud)
    X = new_df.drop(['fraud'], axis=1).values

    if model is None:
        model = RandomForestClassifier(n_estimators=150) # Our base model.
    model = model.fit(X, y)

    # Save our model and names of columns in the file as a pickle object.
    if save:
        with open(filename_pickle, 'wb') as f:
            pickle.dump((model, final_columns, averages), f)
    return (model, final_columns, averages)


def extend_dummy_columns(data, final_columns, category_features):
    """
    Convert one row of data into a new data point with dummy columns.
    Input:
        final_columns: names of columns for the dataframe with dummy variables.
        data: a given data point (as a json object)
    Output:
        new_data: a josn object with dummy columns.
    """
    # Columns that has integer values.
    category_int = set(['channels', 'delivery_method', 'fb_published',
                        'has_analytics', 'has_header', 'has_logo',
                        'show_map', 'user_type'])
    new_data = {}
    for final_col in final_columns:
        idx_cat_orig = [i for i in xrange(len(category_features))
                        if category_features[i] == final_col[:len(category_features[i])]]
        if len(idx_cat_orig):
            # original feature name
            cat_orig = category_features[idx_cat_orig[0]]
            # value (in string) of the feature for this column
            val = final_col.replace(cat_orig, '')[1:]
            if cat_orig in category_int:
                if val.isdigit() and int(data[cat_orig]) == int(val):
                    new_data[final_col] = 1
                else:
                    new_data[final_col] = 0
            else:
                if str(data[cat_orig]) == str(val):
                    new_data[final_col] = 1
                else:
                    new_data[final_col] = 0
        else:
            new_data[final_col] = convert_to_float(data[final_col])
    return new_data # dictionary containing all values for our final columns.


def predict(data, model, final_columns, category_features, averages):
    """
    Predict the result of the given data (json).
    Input:
        data: a row of data (as a json object)
        model: our model (should exist).
        category_features: list of category features.
        averages: average number for each non-category features.
    Output:
        prediction: prediction (float).
    """
    new_data = extend_dummy_columns(data, final_columns, category_features)
    # np array to use for our model.
    test_data = np.ones(len(final_columns))
    for i, col in enumerate(final_columns):
        if new_data[col] is None:
            test_data[i] = averages[col]
        else:
            test_data[i] = new_data[col]
    return model.predict_proba(test_data)[0][1]


def testmodel(label_name, category_features, non_category_features, model):
    """
    Model is built here.
    Input:
        label_name: column name for the targe feature.
        category_features: list of column names for category features.
        non_category_features: list of column names for non-category features.
        model: model object.
    Output:
        model: returns the fitted model (it will be saved as pickle object
            as '/data/model.pkl') (And the model object will be stored, too.)
        final_columns: list of names for final columns.
        averages: dictionary of averages for non-category features.
    """
    # Reading the train/test data as data frames.
    train_df, test_df = read_data()

    # Preprocess the data frame.
    new_df = preprocess(train_df, label_name, category_features, non_category_features)

    # Names of final columns
    final_columns = new_df.columns

    # Find averages for non-category features.
    averages = {}
    for col in non_category_features:
        averages[col] = new_df[col].mean()

    # Dropping na's
    new_df = new_df.dropna()

    # getting X & y for the train set
    y = np.array(new_df.fraud)
    X = new_df.drop(['fraud'], axis=1).values

    # Fit the model
    model = model.fit(X, y)

    return (model, final_columns, averages)
