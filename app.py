import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'demo-only-change-this-secret')
DB = os.path.join(os.path.dirname(__file__), 'bank.db')
ADMIN_PIN = os.environ.get('ADMIN_PIN', '1234')  # Demo only
BANKS = ['Main Branch', 'Town Branch', 'Market Branch']
SERVICES = ['Deposit', 'Withdrawal', 'Account Opening', 'Other']

def connect():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank TEXT NOT NULL, name TEXT NOT NULL, service TEXT NOT NULL,
            people INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'waiting',
            created_at TEXT NOT NULL)''')
        con.execute('CREATE INDEX IF NOT EXISTS idx_tokens_bank_status ON tokens(bank,status)')

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/admin')
def admin():
    return render_template('admin.html')

@app.get('/api/status')
def status():
    bank = request.args.get('bank', BANKS[0])
    if bank not in BANKS:
        return jsonify(error='Invalid bank'), 400
    with connect() as con:
        rows = con.execute('SELECT id,people,status FROM tokens WHERE bank=? ORDER BY id', (bank,)).fetchall()
    waiting = [r for r in rows if r['status'] == 'waiting']
    serving = [r for r in rows if r['status'] == 'serving']
    return jsonify(bank=bank, waiting_tokens=len(waiting), waiting_people=sum(r['people'] for r in waiting),
                   serving_token=serving[0]['id'] if serving else None,
                   estimated_minutes=len(waiting)*5, crowd=('Low' if sum(r['people'] for r in waiting)<5 else 'Medium' if sum(r['people'] for r in waiting)<15 else 'High'))

@app.post('/api/book')
def book():
    data = request.get_json(silent=True) or {}
    bank, name, service = data.get('bank'), str(data.get('name','')).strip(), data.get('service')
    try:
        people = int(data.get('people'))
    except (ValueError, TypeError):
        return jsonify(error='Enter a valid number of people'), 400
    if bank not in BANKS or service not in SERVICES or not (1 <= len(name) <= 60) or not (1 <= people <= 5):
        return jsonify(error='Check bank, name, service and people (1 to 5)'), 400
    with connect() as con:
        cur = con.execute('INSERT INTO tokens(bank,name,service,people,created_at) VALUES(?,?,?,?,?)',
                          (bank,name,service,people,datetime.now().isoformat(timespec='seconds')))
        token_id = cur.lastrowid
    return jsonify(token=token_id, bank=bank, people=people), 201

@app.post('/api/admin/login')
def login():
    data = request.get_json(silent=True) or {}
    if str(data.get('pin','')) != ADMIN_PIN:
        return jsonify(error='Incorrect PIN'), 401
    session['admin'] = True
    return jsonify(ok=True)

@app.post('/api/admin/logout')
def logout():
    session.clear()
    return jsonify(ok=True)

def admin_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not session.get('admin'):
            return jsonify(error='Admin login required'), 401
        return fn(*args, **kwargs)
    return inner

@app.get('/api/admin/tokens')
@admin_required
def tokens():
    bank = request.args.get('bank', BANKS[0])
    if bank not in BANKS:
        return jsonify(error='Invalid bank'), 400
    with connect() as con:
        rows = con.execute('SELECT id,name,service,people,status,created_at FROM tokens WHERE bank=? ORDER BY id DESC LIMIT 100',(bank,)).fetchall()
    return jsonify(tokens=[dict(r) for r in rows])

@app.post('/api/admin/next')
@admin_required
def next_token():
    data = request.get_json(silent=True) or {}
    bank = data.get('bank')
    if bank not in BANKS:
        return jsonify(error='Invalid bank'), 400
    with connect() as con:
        con.execute("UPDATE tokens SET status='completed' WHERE bank=? AND status='serving'",(bank,))
        row = con.execute("SELECT id FROM tokens WHERE bank=? AND status='waiting' ORDER BY id LIMIT 1",(bank,)).fetchone()
        if row:
            con.execute("UPDATE tokens SET status='serving' WHERE id=?",(row['id'],))
    return jsonify(serving_token=row['id'] if row else None)

@app.get('/api/token/<int:token_id>')
def token_status(token_id):
    with connect() as con:
        row = con.execute('SELECT id,bank,service,people,status FROM tokens WHERE id=?',(token_id,)).fetchone()
        if not row:
            return jsonify(error='Token not found'), 404
        ahead = con.execute("SELECT COUNT(*) FROM tokens WHERE bank=? AND status='waiting' AND id<?",(row['bank'],token_id)).fetchone()[0]
    return jsonify(**dict(row), tokens_ahead=ahead, estimated_minutes=ahead*5)

init_db()
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
