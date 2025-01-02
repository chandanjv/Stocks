import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:new_password@localhost:5432/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    ltp = db.Column(db.Float)
    ath = db.Column(db.Float)
    from_alh = db.Column(db.Float)  # Percentage rise/fall from ATH
    notes = db.Column(db.String(500))
    breakout_breakdown = db.Column(db.Float)

# Ensure tables exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_stock', methods=['POST'])
def add_stock():
    stock_name = request.form['stock_name']
    ticker = request.form['ticker']

    # Check if the stock already exists
    existing_stock = Stock.query.filter_by(ticker=ticker).first()
    if existing_stock:
        return f"Stock with ticker {ticker} already exists!"

    new_stock = Stock(stock_name=stock_name, ticker=ticker)
    db.session.add(new_stock)
    db.session.commit()
    return redirect('/portfolio')

@app.route('/portfolio')
def portfolio():
    stocks = Stock.query.all()
    
    # Update LTP, ATH, and calculate From ATH for each stock
    for stock in stocks:
        try:
            ticker_data = yf.Ticker(stock.ticker)
            info = ticker_data.info
            stock.ltp = info.get('currentPrice') or info.get('ask') or info.get('previousClose') or None
            stock.ath = info.get('fiftyTwoWeekHigh')  # Fetch ATH from yfinance
            
            # Calculate From ATH (if ATH and LTP are available)
            if stock.ath and stock.ltp:
                # Calculate percentage difference from ATH
                stock.from_alh = ((stock.ltp - stock.ath) / stock.ath) * 100
            else:
                stock.from_alh = None
        except Exception as e:
            app.logger.error(f"Error fetching data for {stock.ticker}: {e}")
            stock.ltp = None
            stock.ath = None
            stock.from_alh = None

    db.session.commit()
    return render_template('portfolio.html', stocks=stocks)

@app.route('/update_notes/<int:stock_id>', methods=['POST'])
def update_notes(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    notes = request.form['notes']
    stock.notes = notes
    db.session.commit()
    return redirect('/portfolio')

@app.route('/add')
def add():
    return render_template('add_stock.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

