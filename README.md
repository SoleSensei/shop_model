# Shop work simulation model with SimPy

## Launch

    python3 shop.py

## Simulation

The shop working time: `6:00 AM - 11:00 PM.`

Customers enters with random distribution `~ every 15 seconds`

Each customer buys on average `~ 10 goods.` Pay and shopping time depends on the quantity of the goods.

There are `3 cash boxes` setup in the shop.

The shop announces its close `20 minutes` before it.

You can change all `highlighted` values above in the program:
```py
# You can change constants
SHOP_OPEN_TIME = 6*3600 # Shop opens at 6:00 AM
SHOP_CLOSE_TIME = 23*3600 # Shop closes at 11:00 PM
ANNOUNCE_CLOSE = 20*60 # The shop announces closing 20 minutes before
AVG_ENTER_TIME = 15 # A customer enters every ~15 seconds
AVG_BUYS_NUBMER = 10 # A customer buys ~10 goods
NUM_TERMINAL = 3 # Number of pay terminals in the shop
```
with some evident restricts:
```py
SHOP_OPEN_TIME < SHOP_CLOSE_TIME
ANNOUNCE_CLOSE < SHOP_CLOSE_TIME - SHOP_OPEN_TIME
```
all values positive of course.

```py
$ python3 shop.py
```