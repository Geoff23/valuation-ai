from peewee import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing


db = SqliteDatabase('data.db')

class Stock(Model):
    name = CharField(primary_key = True)
    market_cap = IntegerField()
    revenue_growth = FloatField()
    earnings_growth = FloatField()
    cash = IntegerField()
    debt = IntegerField()
    revenue = IntegerField()
    gross_profit = IntegerField()
    operating_income = IntegerField()
    net_income = IntegerField()
    assets = IntegerField()
    current_assets = IntegerField()
    liabilities = IntegerField()
    current_liabilities = IntegerField()
    equity = IntegerField()
    next_five_years = FloatField()
    past_five_years = FloatField()
    class Meta:
        database = db

db.connect()


dataset = pd.DataFrame(list(Stock.select().dicts()))
del dataset['name']

train_dataset = dataset.sample(frac=0.80)
test_dataset = dataset.drop(train_dataset.index)

train_features = train_dataset.copy()
test_features = test_dataset.copy()
train_labels = train_features.pop('market_cap')
test_labels = test_features.pop('market_cap')

normalizer = preprocessing.Normalization()
normalizer.adapt(np.array(train_features))


def build_and_compile_model(norm):
    model = keras.Sequential([
        norm,
        layers.Dense(256, activation='relu'),
        layers.Dense(256, activation='relu'),
        layers.Dense(256, activation='relu'),
        layers.Dense(256, activation='relu'),
        layers.Dense(1)
    ])
    model.compile(loss='mean_absolute_percentage_error',
                  optimizer=tf.keras.optimizers.Adam(learning_rate=0.01))
    return model
    
model = build_and_compile_model(normalizer)
history = model.fit(
    train_features, train_labels,
    validation_split=0.20,
    epochs=1000)


def plot_loss(history):
    plt.plot(history.history['loss'], label='Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True)

plot_loss(history)
plt.show()

test_predictions = model.predict(test_features).flatten()
model.evaluate(test_features, test_labels)

plt.axes(aspect='equal')
lims = [10000000000, 1000000000000]
plt.xlim(lims)
plt.ylim(lims)
plt.scatter(test_labels, test_predictions, s=1)
plt.xlabel('True Values')
plt.ylabel('Predictions')
plt.plot(lims, lims)
plt.show()

model.save('model')
