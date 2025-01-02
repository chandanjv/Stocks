from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Use your actual connection string here
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:new_password@localhost:5432/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Stock model
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(20), unique=True, nullable=False)
    ltp = db.Column(db.Float)
    ath = db.Column(db.Float)
    from_alh = db.Column(db.Float)
    notes = db.Column(db.String(500))
    breakout_breakdown = db.Column(db.Float)

    def __repr__(self):
        return f'<Stock {self.stock_name} ({self.ticker})>'

@app.route('/')
def test_db_connection():
    try:
        # Try creating the table for Stock model
        db.create_all()  # Creates tables for all models defined in SQLAlchemy
        return "Connection to the database is successful! Tables created."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

