from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

app = Flask(__name__)

# Configure the database
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'default_connection_string')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chandanjv@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    ltp = db.Column(db.Float, nullable=True)
    ath = db.Column(db.Float, nullable=True)
    from_alh = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    breakout_breakdown = db.Column(db.Float, nullable=True)  # New column for Breakout/Breakdown value

    def __init__(self, stock_name, ticker, notes=None, breakout_breakdown=None):
        self.stock_name = stock_name
        self.ticker = ticker
        self.notes = notes
        self.breakout_breakdown = breakout_breakdown

   

# Ensure tables exist
with app.app_context():
    if not hasattr(Stock, 'breakout_breakdown'):
        try:
            db.session.execute('ALTER TABLE stock ADD COLUMN breakout_breakdown FLOAT;')
            db.session.commit()
        except Exception as e:
            print(f"Error adding breakout_breakdown column: {e}")
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

    for stock in stocks:
        try:
            ticker_data = yf.Ticker(stock.ticker)
            stock.ltp = round(float(ticker_data.history(period='1d')['Close'].iloc[-1]), 2)
            stock.ath = round(float(ticker_data.history(period='max')['High'].max()), 2)

            if stock.ath and stock.ltp:
                stock.from_alh = round(((stock.ltp - stock.ath) / stock.ath) * 100, 2)
            else:
                stock.from_alh = None

            # Add logic to check if LTP matches Breakout/Breakdown
            stock.is_breakout_breakdown = (
                stock.breakout_breakdown is not None and stock.ltp == stock.breakout_breakdown
            )
        except Exception:
            stock.ltp = None
            stock.ath = None
            stock.from_alh = None
            stock.is_breakout_breakdown = False

    db.session.commit()
    return render_template('portfolio.html', stocks=stocks)


@app.route('/update_notes/<int:stock_id>', methods=['POST'])
def update_notes(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    notes = request.form['notes']
    stock.notes = notes  # Update the notes
    db.session.commit()
    return redirect('/portfolio')

@app.route('/add')
def add():
    return render_template('add_stock.html')

if __name__ == '__main__':
    app.run(debug=True)
