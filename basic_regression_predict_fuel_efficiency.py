# -*- coding: utf-8 -*-
"""Basic regression: Predict fuel efficiency.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rpWU14iY9_WnwMB40cE6lB-WJopu9Kgu

This notebook uses the classic Auto MPG Dataset and builds a model to predict the fuel efficiency of late-1970s and early 1980s automobiles. To do this, we'll provide the model with a description of many automobiles from that time period. This description includes attributes like: cylinders, displacement, horsepower, and weight.
"""

!pip install -q seaborn

!pip install -q git+https://github.com/tensorflow/docs

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

print(tf.__version__)

import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling

"""## The Auto MPG dataset

**Get the data**
"""

dataset_path = keras.utils.get_file("auto-mpg.data",
                                    "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data")
dataset_path

column_names = ['MPG', 'Cylinders', 'Displacement', 'Horsepower',
                'Weight', 'Acceleration', 'Model Year', 'Origin']
raw_dataset = pd.read_csv(dataset_path, names=column_names,
                       na_values='?', comment='\t',
                       sep=' ', skipinitialspace=True)
dataset = raw_dataset.copy()
dataset.tail()

dataset.head()

"""#### Clean the data"""

dataset.isna().sum()

# we're going to drop these row

dataset = dataset.dropna()

dataset.isna().sum()

dataset.info()

dataset['Origin'].unique()

"""The `"Origin"` column is really categorical, not numeric. So convert that to a one-hot:"""

dataset['Origin'] = dataset['Origin'].map({1:'USA', 2:'Europe', 3:'Japan'})

dataset.head()

dataset = pd.get_dummies(dataset, prefix='', prefix_sep='')
dataset.head()

dataset.tail()

"""### Split the data into train and test"""

train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

"""### Inspect the data

Have a quick look at the `joint-distribution` of a few pairs of columns from the training dataset
"""

sns.pairplot(train_dataset[['MPG', 'Cylinders', 'Displacement', 'Weight']],
             diag_kind='kde')

train_dataset.describe().T

train_stats = train_dataset.describe()
train_stats.pop('MPG')
train_stats = train_stats.transpose()
train_stats

"""### Split features from labels"""

train_labels = train_dataset.pop('MPG')
test_labels = test_dataset.pop('MPG')

"""### Normalize the data"""

def norm(X):
    return (X-train_stats['mean']) / train_stats['std']

normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)     # we can do for test dataset also with same parameter as train
                                          # i.e. using mean, std of train data

"""# The Model
### Build the model
"""

def build_model():
    model = keras.Sequential([
                              layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
                              layers.Dense(64, activation='relu'),
                              layers.Dense(1)
    ])

    optimizer = tf.keras.optimizers.RMSprop(0.001)

    model.compile(loss='mse',
                  optimizer=optimizer,
                  metrics=['mae', 'mse'])
    return model

model = build_model()

model.summary()

"""Take a batch of `10` example from `training dataset` and call `model.predict` on it"""

example_batch = normed_train_data[:10]
example_result = model.predict(example_batch)
example_result

"""## Train the model"""

EPOCHS = 1000

history = model.fit(normed_train_data,
                    train_labels,
                    epochs=EPOCHS,
                    validation_split=0.2,
                    verbose=0,
                    callbacks=[tfdocs.modeling.EpochDots()])

hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
hist.head()

plotter  = tfdocs.plots.HistoryPlotter(smoothing_std=2)

plotter.plot({'Basic': history}, metric='mae')
plt.ylim([0,10])
plt.ylabel('MAE [MPG]')

"""So mae for training is decreasing while for validation it's increasing"""

plotter.plot({'Basic': history}, metric='mse')
plt.ylim([0, 20])
plt.ylabel('MSE (MPG^2]')

"""This graph shows little improvement, or even degradation in the validation error after about 100 epochs. Let's update the `model.fit` call to automatically stop training when the validation score doesn't improve. We'll use an `EarlyStopping callback` that tests a training condition for every epoch. If a set amount of epochs elapses without showing improvement, then automatically stop the training.

More about this callback https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping
"""

model = build_model()

# the patience parameter is the amount of epochs to check for improvement
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

early_history = model.fit(normed_train_data,
                          train_labels,
                          epochs=EPOCHS,
                          validation_split=0.2,
                          verbose=0,
                          callbacks=[early_stop, tfdocs.modeling.EpochDots()])

plotter.plot({'Early Stopping': early_history}, metric='mae')
plt.ylim([0,10])
plt.ylabel('MAE [MPG]')

loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
print('Testing set Mean Absolute Error: {:5.2f} MPG'.format(mae))

"""## Make predictions"""

test_predictions = model.predict(normed_test_data).flatten()

a = plt.axes(aspect='equal')
plt.scatter(test_labels, test_predictions)
plt.xlabel('True Values [MPG]')
plt.ylabel('Predictions [MPG]')
lims = [0, 50]
plt.xlim(lims)
plt.ylim(lims)
_ = plt.plot(lims, lims)

"""Now let's take look at the error distribution."""

error = test_predictions - test_labels
plt.hist(error, bins=25)
plt.xlabel('Prediction Error [MPG]')
_ = plt.ylabel('Count')

"""THANK YOU!!!"""

