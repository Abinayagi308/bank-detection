# Bank Crowd Detection & Smart Token Management (Prototype)

## Run in VS Code (Windows)
1. Install Python 3 and VS Code. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Run `py -m pip install -r requirements.txt`
4. Run `py app.py`
5. Visit http://127.0.0.1:5000 for customers and http://127.0.0.1:5000/admin for staff.
6. Demo admin PIN: `1234` (change via ADMIN_PIN environment variable).

SQLite database `bank.db` is created automatically. Use Ctrl+C to stop.

## Limitations
This is a local demonstration, not connected to a real bank. Crowd counts reflect people booked in **waiting online tokens**, not everyone physically present. Estimated time uses 5 minutes per waiting token, not measured bank service times. For production: HTTPS, proper bank staff authentication, CSRF protection, rate limits, booking abuse controls, privacy policy, data retention, monitoring, and actual branch check-in/camera integration with appropriate permission are needed. Do not deploy with the default demo PIN or secret key. No real banking or financial account information is collected.
