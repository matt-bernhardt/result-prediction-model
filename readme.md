# Result Prediction Model

This tool allows you to simulate a season of Major League Soccer, storing a
list of final points earned by each team in each simulation.

## Usage

There are multiple simulation tools provided. Running any can be done by
calling the relevant script from your terminal window:

```
$ ./model170501.py
```

The output of each script, stored in the `output/` directory, will be a CSV
file with one line per each simulated season. This CSV file can then be
analyzed in the tool of your choice.

### Differences among tools

Each tool is a monte carlo model, building up a simulated final standings by
simulating each game in the schedule. The tools differ in how they calculate
a given result.

1. Naive model
The most naive models (model170403.py and model170403_3ltr.py) assign a winner
for each game by looking only at who plays at home.

2. Less-naive model
The later models (model170501.py and the 2018 models) are slightly more
refined, in that they consider which team has earned more points per game
(PPG) coming into that game.

None of these models attempt to consider factors such as travel, fixture
congestion, player absences, or in-game events.

## Requirements

The tool is written for Python 2.7, and requires a MySQL database connection
stored in `./connection.py` of the format:

```
u = 'USERNAME'
p = 'PASSWORD'
h = 'HOST'
d = 'SCHEMA'
```

The structure of the database can be inferred from the scripts' SQL query that
builds the remaining games for each season.

## Questions?

Please contact me at bernhardtsoccer@yahoo.com or on Twitter at 
@BernhardtSoccer with any questions or concerns.
