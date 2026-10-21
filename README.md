# Bad Wallet

A really bad crypto wallet made for the Cyber Security Base Course Project I.
The coins (HYC) are not real, they are just numbers in the database.

The app has five security flaws from the OWASP Top 10 2021 list on purpose.
The fixes are in the code too, but they are commented out (look for `FLAW` and `FIX` comments).

## Installation

You need Python 3 and git. On Windows use `python` instead of `python3`.

```
git clone https://github.com/hhuuskon/HY-CS-Projekti
cd HY-CS-Projekti
pip install -r requirements.txt
cd mysite
python3 manage.py migrate
python3 manage.py runserver
```

Then open http://localhost:8000/wallet/

## Test users

The `migrate` command makes these users:

| Username | Password | Notes |
|---|---|---|
| kissa | kissa123 | wallet 1 |
| koira | koira123 | wallet 2 |
| admin | admin123 | can see the log at /wallet/logs/ |

## Screenshots

Screenshots of every flaw before and after the fix are in the `screenshots` folder.
