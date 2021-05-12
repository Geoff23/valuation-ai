from peewee import *
import yahoo_fin.stock_info as si


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
db.create_tables([Stock])


def convert(string):
    if 'T' in string:
        integer = int(float(string[:-1])*1000000000000)
    elif 'B' in string:
        integer = int(float(string[:-1])*1000000000)
    elif 'M' in string:
        integer = int(float(string[:-1])*1000000)
    else:
        raise NotImplementedError
    return integer
    
def scrape(name):
    stock = Stock()
    stock.name = name

    stock.market_cap = convert(si.get_quote_table(name)['Market Cap'])
            
    stats = si.get_stats(name).set_index('Attribute')
    stock.revenue_growth = float(stats.loc['Quarterly Revenue Growth (yoy)'][0][:-1])/100
    stock.earnings_growth = float(stats.loc['Quarterly Earnings Growth (yoy)'][0][:-1].replace(',', ''))/100
    stock.cash = convert(stats.loc['Total Cash (mrq)'][0])
    stock.debt = convert(stats.loc['Total Debt (mrq)'][0])
            
    income_statement = si.get_income_statement(name, yearly=False)
    stock.revenue = sum(income_statement.loc['totalRevenue'][:4])
    stock.gross_profit = sum(income_statement.loc['grossProfit'][:4])
    stock.operating_income = sum(income_statement.loc['operatingIncome'][:4])
    stock.net_income = sum(income_statement.loc['netIncome'][:4])
    
    balance_sheet = si.get_balance_sheet(name, yearly=False)
    stock.assets = int(balance_sheet.loc['totalAssets'][0])
    stock.current_assets = int(balance_sheet.loc['totalCurrentAssets'][0])
    stock.liabilities = int(balance_sheet.loc['totalLiab'][0])
    stock.current_liabilities = int(balance_sheet.loc['totalCurrentLiabilities'][0])
    stock.equity = int(balance_sheet.loc['totalStockholderEquity'][0])

    analysts_info = si.get_analysts_info(name)['Growth Estimates'].set_index('Growth Estimates')
    stock.next_five_years = float(analysts_info.loc['Next 5 Years (per annum)'][0][:-1])/100
    stock.past_five_years = float(analysts_info.loc['Past 5 Years (per annum)'][0][:-1])/100

    stock.save(force_insert = True)



for stock in Stock.select():
    stock.delete_instance()

errors = 0
sp500 = si.tickers_sp500()
for name in sp500:
    try:
        scrape(name)
        print(name)
    except:
        errors += 1
        print(name, 'ERROR!!!')

print(errors, 'errors', '('+str(round((1-errors/len(sp500))*100))+'% success rate)')
#4/2/2021-4/4/2021 (102 errors)
