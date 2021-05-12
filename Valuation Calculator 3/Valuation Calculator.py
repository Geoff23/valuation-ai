from peewee import *
import pandas as pd
import tensorflow as tf


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


features = pd.DataFrame(list(Stock.select().dicts()))
del features['name']
del features['market_cap']

model = tf.keras.models.load_model('model')
predictions = model.predict(features).flatten()

count = 0
differences = {}
for stock in Stock.select():
    differences[stock.name] = stock.market_cap/predictions[count]-1
    count += 1

rankings = dict(sorted(differences.items(), key=lambda item: item[1]))
for stock in rankings:
    print(stock, "{0:.0%}".format(rankings[stock]))
