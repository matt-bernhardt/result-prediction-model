# Result Prediction Model

This tool allows you to simulate a season of Major League Soccer, storing a
list of final points earned by each team in each simulation.

## Usage

Running each simulation is as simple as calling the script from your terminal
window:

```
$ ./model170501.py
```

The output of the script, stored in the `output/` directory, will be a CSV
file with one line per each simulated season. This CSV file can then be
analyzed in the tool of your choice.

## Requirements

The tool is written for Pythone 2.7, and requires a MySQL database connection
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
