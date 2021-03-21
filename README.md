# FTX COMPUNDING

- compound interest to lending
- report send via PushOver

## installation

```
git clone git@github.com:bert2002/ftx-compounding.git
cd ftx-compounding
pip3 -r requirements.txt
```

## configuration

Create a `.env` file with following content

```
FTX_API_KEY=
FTX_SECRET=
PUSHOVER_USER_KEY=
PUSHOVER_APP_KEY=
COINS=USD,USDT
```

`COINS` are the tokens you want to compound.


## run

```
./ftx-compounding.py
```
