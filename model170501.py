import copy
import database
from log import Log
from output import Output
import numpy as np


# This prediction model has been superceded by the model18* versions, but the
# changes introduced there are largely driven by efficiency rather than
# updated methods.
#
# This model is fairly naive, simulating each game result based on two
# factors (lines 34-54)
# 1. Who plays at home
# 2. Which team has a higher PPG coming into the game
#
# Before running the model, several things must be checked and updated
# manually:
# 1. If needed, update the SQL statements on lines 90 and 110 to retrieve the
#    current season's data.
# 2. For seasons other than 2017, the list of teams (lines 62-83) should be
#    updated.
# 3. The names of the log and output files (lines 177 and 188, respectively)
#    should be updated, unless you are comfortable overwriting the last run.

def calculatePPG(data):
    # This expects data in a form of
    # {'MIN': {'Points': 8.0, 'PPG': 0.8888888888888888, 'GP': 9.0}, 'TOR': {'Points': 16.0, 'PPG': 1.7777777777777777, 'GP': 9.0}}
    for team in data:
        data[team]['PPG'] = data[team]['Points'] / data[team]['GP']
    return data


def calculateThreshold(homePPG, awayPPG):
    # This calculates and returns a dictionary of thresholds for home wins
    # and draws.

    # Determine counts based on comparative PPG
    if (homePPG == awayPPG):
        home = 58.0
        draw = 26.0
        away = 33.0
    elif (homePPG > awayPPG):
        home = 481.0
        draw = 229.0
        away = 171.0
    else:
        home = 433.0
        draw = 278.0
        away = 246.0

    # Calculate and return randomness thresholds
    threshold = {}
    threshold['home'] = home / (home + draw + away)
    threshold['draw'] = (home + draw) / (home + draw + away)
    return threshold


def dataInit(database):
    # This initializes the nested dictionary that records the simulation output
    data = {}
    data['CLB'] = loadStats(database, 11)
    data['DC'] = loadStats(database, 12)
    data['CHI'] = loadStats(database, 13)
    data['COL'] = loadStats(database, 14)
    data['NE'] = loadStats(database, 15)
    data['DAL'] = loadStats(database, 16)
    data['SJ'] = loadStats(database, 17)
    data['KC'] = loadStats(database, 18)
    data['LA'] = loadStats(database, 19)
    data['NY'] = loadStats(database, 20)
    data['POR'] = loadStats(database, 42)
    data['SEA'] = loadStats(database, 43)
    data['VAN'] = loadStats(database, 44)
    data['MON'] = loadStats(database, 45)
    data['RSL'] = loadStats(database, 340)
    data['HOU'] = loadStats(database, 427)
    data['TOR'] = loadStats(database, 463)
    data['PHI'] = loadStats(database, 479)
    data['ORL'] = loadStats(database, 506)
    data['MIN'] = loadStats(database, 521)
    data['NYC'] = loadStats(database, 547)
    data['ATL'] = loadStats(database, 599)
    data = calculatePPG(data)
    return data


def loadGames(database):
    # This should be passed from outside, so we just get records once
    sql = ("SELECT g.ID, h.team3ltr AS Home, a.team3ltr AS Away "
           "FROM tbl_games g "
           "INNER JOIN tbl_teams h on g.HTeamID = h.ID "
           "INNER JOIN tbl_teams a on g.ATeamID = a.ID "
           "WHERE YEAR(g.MatchTime) = 2017 "
           "AND g.MatchTypeID = 21 "
           "AND g.MatchTime > NOW() "
           "ORDER BY g.MatchTime ASC")
    # log.message(sql)
    rs = database.query(sql, ())

    if (rs.with_rows):
        records = rs.fetchall()

    return records


def loadStats(database, teamid):
    # This calculates a given team's GP, Points, and PPG values.
    # It is part of the initialization step.
    sql = ("SET @GP = 0;"
           "SET @Pts = 0;"
           "SELECT HTeamID, HScore, ATeamID, AScore, @GP:=@GP+1 AS GP, "
           "IF(HScore=AScore, "
           "@Pts:=@Pts+1, "
           "IF(HTeamID= %s, "
           "  IF(HScore > AScore,@Pts:=@Pts+3,@Pts), "
           "  IF(HScore > AScore,@Pts,@Pts:=@Pts+3) "
           ")) AS Points "
           "FROM tbl_games "
           "WHERE YEAR(MatchTime) = 2017 "
           "  AND MatchTime < NOW() "
           "  AND (HTeamID = %s OR ATeamID = %s) "
           "  AND MatchTypeID = 21")
    records = database.multiquery(sql, (teamid, teamid, teamid))

    stats = {}
    for game in records:
        stats['GP'] = game[4]
        stats['Points'] = game[5]

    return stats


def simulateGame(log, data, home, away):
    # Calculate thresholds
    threshold = calculateThreshold(data[home]['PPG'], data[away]['PPG'])

    # Random number
    result = np.random.random(1)[0]

    # Return H/D/A based on random number
    if (result <= threshold['home']):
        # Home win
        data[home]['Points'] += 3
    elif (result <= threshold['draw']):
        # Draw
        data[home]['Points'] += 1
        data[away]['Points'] += 1
    else:
        # Away win
        data[away]['Points'] += 3

    # Increment games played
    data[home]['GP'] += 1
    data[away]['GP'] += 1

    # Recalculate PPG
    data = calculatePPG(data)

    return data


def simulateSeason(log, database, output, gamelist, initial):
    # Initialize starting data
    standings = copy.deepcopy(initial)

    # For each game in the list, simulate the result and update standings
    for game in enumerate(gamelist):
        standings = simulateGame(log, standings, game[1][1], game[1][2])

    # Store final points totals for all teams in CSV file for later analysis
    output.points(standings)


if __name__ == "__main__":
    # Log
    log = Log('logs/model_v2_170605.log')

    # Database
    database.connect()

    # Load initial standings
    initial = dataInit(database)

    # Initialize output file
    # This is after the standings init because the first line of output is to
    # write the team abbreviations (array keys) as the header row.
    output = Output('output/model_v2_170605.csv', initial)

    # Get list of games
    schedule = loadGames(database)

    # Simulate all season
    for i in range(10000):
        log.message('Season ' + str(i))
        simulateSeason(log, database, output, schedule, initial)

    # Shut down
    database.disconnect()
    output.end()
    log.end()
