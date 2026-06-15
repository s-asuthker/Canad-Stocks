import matplotlib
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
import io, base64, datetime
from datetime import date
from forex_python.converter import CurrencyRates
matplotlib.use('Agg')
def plot_2html(df_html,user_symbol,qtype):
    """type is 'stock' or 'economic'. """
    fig, ax = plt.subplots()
    if qtype == 'stock':
        ax.plot(df_html['Close'], label=user_symbol, color='red')
    else:
        ax.plot(df_html, label=user_symbol, color='red')
    ax.legend()
    ax.grid(True)
    ax.set_title(f"{user_symbol} Stock Price")
    fig.autofmt_xdate()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img_base64
app = Flask(__name__)
@app.route('/',methods=['GET','POST'])
def stock_graph():
    closing_price=None
    stock_graph_img=None
    if request.method == 'POST':
        user_input=request.form.get('ticker_input')
        end=datetime.datetime.today()
        try:
            start = end.replace(year=end.year - 1)  # sets timeframe to 1 year before present
        except ValueError:
            start = end.replace(year=end.year - 1, day=28)  # incase its leap year
        if user_input:
            df_stock = yf.download(user_input, start=start, end=end) #gets stock data
            print("EMPTY DF?", df_stock.empty)
            print(df_stock.tail())
            print(df_stock) # for debugging purposes
            try:
                closing_price=df_stock['Close'].iloc[-1,0]
                print(closing_price) #for debugging as well
                user_input=user_input.upper()
                stock_graph_img = plot_2html(df_stock, user_input,"stock")
            except Exception as e:
                closing_price=None
                print(f"Sorry, it looks like there was an error: {e}")

    #this code gets gold prices
    gold = yf.Ticker("GC=F")
    gold_price = gold.info.get('regularMarketPrice')
    #this code gets current exchange rate sbetween popular currencies
    c=CurrencyRates()

    crate=c.get_rate('USD','EUR') #USD --> EUR
    crate2=c.get_rate('EUR','USD')
    crate3=c.get_rate('USD','CAD')
    crate4=c.get_rate('CAD','USD')
    crate5=c.get_rate('USD','GBP') #GBP=Great Britain Pound
    crate6=c.get_rate('GBP','USD')
    crate7=c.get_rate('USD','JPY')
    rate_dic={
        "rate": crate,
        "rate2": crate2,
        "rate3": crate3,
        "rate4": crate4,
        "rate5": crate5,
        "rate6": crate6,
        "rate7": crate7
    }
    return render_template("stocks.html",price=closing_price, graph=stock_graph_img,wgold_price=gold_price,rate_dic=rate_dic)
if __name__ == '__main__':
    app.run(debug=True)
