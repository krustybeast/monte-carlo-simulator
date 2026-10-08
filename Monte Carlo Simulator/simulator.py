# =============================================================================
# MONTE CARLO INVESTMENT SIMULATOR
#
# What this program does:
#   Nobody knows exactly what the stock market will do. So instead of making
#   one guess, we "roll the dice" many times, using a real stock's past
#   monthly ups and downs as the dice. Each roll is one possible future
#   for your investments. By looking at all those possible futures together,
#   we can see the range of outcomes: bad luck, average luck and good luck.
#
# How to run it:
#   Open a terminal in this folder and type:   python3 simulator.py
# =============================================================================


# -----------------------------------------------------------------------------
# SETTINGS - change these to try different scenarios
# -----------------------------------------------------------------------------
TICKER = "U11.SI"            # The stock's symbol on Yahoo Finance ("D05.SI" is DBS)
STARTING_AMOUNT = 500     # Money you invest on day one
MONTHLY_AMOUNT = 500         # Money you add every month
YEARS = 20                   # How many years you keep investing
NUM_SIMULATIONS = 1_000      # How many possible futures to simulate
# (The underscores in 10_000 are just for readability, like commas: 10,000)


# -----------------------------------------------------------------------------
# STEP 1: Load the tools we need
# -----------------------------------------------------------------------------
import numpy as np

import matplotlib.pyplot as plt
# yfinance downloads real stock prices from Yahoo Finance. 
import yfinance as yf


# -----------------------------------------------------------------------------
# STEP 2: Download the stock's real price history
# -----------------------------------------------------------------------------
# Ask Yahoo Finance for the last 10 years of prices, one price per month.
# (This needs an internet connection.)
# These prices are "adjusted", meaning dividends the stock paid are counted
# as if you had reinvested them.
price_history = yf.Ticker(TICKER).history(period="10y", interval="1mo")

# We only need the closing price for each month.
monthly_prices = price_history["Close"].dropna()
# (.dropna() throws away any months with missing prices.)

# If nothing came back, the ticker is probably misspelled. Stop with a message.
if len(monthly_prices) == 0:
    raise SystemExit(f"Couldn't find any prices for '{TICKER}'. Check the ticker spelling.")


# -----------------------------------------------------------------------------
# STEP 3: Work out the stock's real monthly returns
# -----------------------------------------------------------------------------
# A monthly return is how much the price changed from one month to the next,
# as a fraction. For example, $10 going to $10.20 is a return of 0.02 (+2%).
# .pct_change() does this for every month. The very first month has no
# "previous month" to compare to, so we drop it with .dropna().
historical_returns = monthly_prices.pct_change().dropna().to_numpy()
# (.to_numpy() turns it into a plain numpy list of numbers.)

# The average monthly return: what a "typical" month looked like.
average_monthly_return = np.mean(historical_returns)

# The volatility: how far a typical month strayed from that average.
# Bigger numbers mean a bumpier ride.
monthly_volatility = np.std(historical_returns)

# Show these so you can see what the stock has really done.
print()
print(f"Real history for {TICKER} ({len(historical_returns)} months of data)")
print("-" * 40)
print(f"Average monthly return:   {average_monthly_return:.2%}")
print(f"Monthly volatility:       {monthly_volatility:.2%}")
print(f"Best month:               {np.max(historical_returns):.2%}")
print(f"Worst month:              {np.min(historical_returns):.2%}")
# (":.2%" means: show it as a percentage with 2 decimal places.)


# -----------------------------------------------------------------------------
# STEP 4: Build random futures out of real past months ("bootstrapping")
# -----------------------------------------------------------------------------
# We simulate month by month, so we need the total number of months.
num_months = YEARS * 12

# Imagine writing each real monthly return from the past 10 years on a slip
# of paper and putting all the slips in a hat. For every month of every
# simulated future, we pull a slip out at random, write it down, and put it
# back in the hat (so the same month can be picked again).
#
# The result is a big table:
#   - one row for each simulation (each possible future)
#   - one column for each month
# and every number in it is a return the stock really had at some point.
random_returns = np.random.choice(
    historical_returns,                  # the hat full of real past returns
    size=(NUM_SIMULATIONS, num_months),  # how many slips to pull
    replace=True,                        # put each slip back after pulling it
)


# -----------------------------------------------------------------------------
# STEP 5: Play out each possible future, one month at a time
# -----------------------------------------------------------------------------
# Make an empty table to record the portfolio value at every month.
# It has one extra column so we can store the starting point (month 0).
portfolio_values = np.zeros((NUM_SIMULATIONS, num_months + 1))

# At month 0, every simulation starts with the same starting amount.
portfolio_values[:, 0] = STARTING_AMOUNT
# (The ":" means "every row", so this fills in all simulations at once.)

# Now walk forward through time, one month at a time.
for month in range(1, num_months + 1):
    # Last month's value for every simulation.
    previous_value = portfolio_values[:, month - 1]

    # This month's random return for every simulation.
    # (month - 1 because our returns table starts counting at 0.)
    this_months_return = random_returns[:, month - 1]

    # Grow (or shrink) the money by this month's return,
    # then add the monthly contribution on top.
    portfolio_values[:, month] = previous_value * (1 + this_months_return) + MONTHLY_AMOUNT


# -----------------------------------------------------------------------------
# STEP 6: Summarize the results
# -----------------------------------------------------------------------------
# Grab just the last column: the final value of each simulation.
final_values = portfolio_values[:, -1]
# (-1 means "the last one".)

# Work out the total amount of your own money you put in, for comparison.
total_contributed = STARTING_AMOUNT + MONTHLY_AMOUNT * num_months

# A "percentile" answers: "what value were X% of outcomes below?"
# For example, the 10th percentile means 10% of futures ended up worse than it.
worst_case = np.min(final_values)
percentile_10 = np.percentile(final_values, 10)
median = np.percentile(final_values, 50)   # the middle outcome
percentile_90 = np.percentile(final_values, 90)
best_case = np.max(final_values)

# Print everything nicely. Inside f"...", anything in {curly braces} is
# replaced with its value. ":,.0f" means: add commas, show no decimals.
print()
print(f"Results after {YEARS} years ({NUM_SIMULATIONS:,} simulations)")
print(f"You put in a total of: ${total_contributed:,.0f}")
print("-" * 40)
print(f"Worst case:       ${worst_case:,.0f}")
print(f"10th percentile:  ${percentile_10:,.0f}")
print(f"Median:           ${median:,.0f}")
print(f"90th percentile:  ${percentile_90:,.0f}")
print(f"Best case:        ${best_case:,.0f}")
print()


# -----------------------------------------------------------------------------
# STEP 7: Draw the chart
# -----------------------------------------------------------------------------
# The x-axis should show years, not months. This makes a list of numbers
# from 0 to YEARS, one for each month (0, 0.083, 0.167, ... 20).
years_axis = np.arange(num_months + 1) / 12

# For each month, find the middle value across all simulations.
# "axis=0" means "go down the columns", i.e. across all simulations.
median_path = np.median(portfolio_values, axis=0)

# Create a blank chart, 10 inches wide by 6 inches tall.
fig, ax = plt.subplots(figsize=(10, 6))

# Draw every simulation as a thin, very faint line.
# ".T" flips the table on its side, because matplotlib expects
# one column per line.
ax.plot(years_axis, portfolio_values.T, color="#2a78d6", alpha=0.04, linewidth=0.8)

# Draw the median path as a thick, dark line on top so it stands out.
ax.plot(years_axis, median_path, color="#0b2e5c", linewidth=2.5, label="Median path")

# Add a title and axis labels.
ax.set_title(f"{NUM_SIMULATIONS:,} simulated futures investing in {TICKER}")
ax.set_xlabel("Years")
ax.set_ylabel("Portfolio value")

# Show the y-axis numbers as dollars with commas, like $250,000.
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"${value:,.0f}"))

# Make the chart start exactly at year 0 and value $0.
ax.set_xlim(0, YEARS)
ax.set_ylim(bottom=0)

# Add light grid lines to make values easier to read, and a legend.
ax.grid(alpha=0.3)
ax.legend(loc="upper left")

# Remove extra blank space around the edges, then show the chart window.
plt.tight_layout()
plt.show()
