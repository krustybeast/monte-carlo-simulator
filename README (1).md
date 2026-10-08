# Monte Carlo Simulator

A Python program that simulates thousands of possible futures for a monthly investment plan, using a real stock's price history. Built while learning to code with VS Code and Claude Code.

Nobody knows what the market will do, so instead of making one guess, this program "rolls the dice" thousands of times to show the range of outcomes you could realistically expect from investing regularly.

## How it works

1. Downloads the last 10 years of monthly prices for a stock or ETF from Yahoo Finance.
2. Calculates the stock's real monthly returns (how much it went up or down each month).
3. Builds 1,000 possible futures by randomly picking from those real past months, a method called **bootstrapping**. Think of it as writing every past month's return on a slip of paper, putting them in a hat, and drawing one for each future month.
4. Adds your monthly investment each month and tracks how the portfolio grows.
5. Prints a summary and draws a chart of every simulated path, with the median path highlighted.

## Example output

```
Results after 20 years (1,000 simulations)
You put in a total of: $130,000
----------------------------------------
Worst case:        $69,913
10th percentile:   $151,914
Median:            $273,141
90th percentile:   $463,403
Best case:         $1,605,373
```

The **10th to 90th percentile** range is the realistic spread. The worst and best cases are rare extremes.

## Settings

All settings are at the top of `simulator.py`, so they're easy to change:

| Setting | Meaning |
|---|---|
| `TICKER` | The stock or ETF to use, e.g. `"D05.SI"` (DBS), `"ES3.SI"` (STI ETF), `"AAPL"`, `"VOO"` |
| `STARTING_AMOUNT` | Money invested on day one |
| `MONTHLY_AMOUNT` | Money added every month |
| `YEARS` | How long you keep investing |
| `NUM_SIMULATIONS` | How many possible futures to simulate |

Singapore-listed tickers end in `.SI`.

## How to run

Install the libraries (one time):

```
python3 -m pip install numpy matplotlib yfinance
```

Then run it from inside the `Monte Carlo Simulator` folder:

```
python3 simulator.py
```

## Things I learned

- A single stock usually gives a much wider spread of outcomes than a broad ETF.
- Bootstrapping from a stock that did very well in the past assumes it will keep doing just as well, which can produce unrealistically high results.

## Disclaimer

This is a learning project, not financial advice. It assumes the future will behave like the past 10 years, which it often won't, and it ignores fees, taxes, inflation and currency changes.
