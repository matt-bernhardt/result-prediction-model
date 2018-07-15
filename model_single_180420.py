import copy
import database
from log import Log
from output import Output
import numpy as np
from datetime import date


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
    data['LAFC'] = loadStats(database, 602)
    data = calculatePPG(data)
    return data


def loadGames(database):
    # This should be passed from outside, so we just get records once
    sql = ("SELECT g.ID, h.team3ltr AS Home, a.team3ltr AS Away "
           "FROM tbl_games g "
           "INNER JOIN tbl_teams h on g.HTeamID = h.ID "
           "INNER JOIN tbl_teams a on g.ATeamID = a.ID "
           "WHERE YEAR(g.MatchTime) = 2018 "
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
    sql = ("SET @GP = 0.0;"
           "SET @Pts = 0.0;"
           "SELECT HTeamID, HScore, ATeamID, AScore, @GP:=@GP+1 AS GP, "
           "IF(HScore=AScore, "
           "@Pts:=@Pts+1, "
           "IF(HTeamID= %s, "
           "  IF(HScore > AScore,@Pts:=@Pts+3,@Pts), "
           "  IF(HScore > AScore,@Pts,@Pts:=@Pts+3) "
           ")) AS Points "
           "FROM tbl_games "
           "WHERE YEAR(MatchTime) = 2018 "
           "  AND MatchTime < NOW() "
           "  AND (HTeamID = %s OR ATeamID = %s) "
           "  AND MatchTypeID = 21")
    records = database.multiquery(sql, (teamid, teamid, teamid))

    stats = {}
    stats['GP'] = 0.0
    stats['Points'] = 0.0
    stats['PPG'] = 0.0
    for game in records:
        stats['GP'] = game[4]
        stats['Points'] = game[5]

    return stats


def renderTable(data):
    # This renders the dictionary of standings data in a legible fashion
    for team in data:
        log.message(str(team) + "   " + str(int(data[team]['Points'])) + "   " + str(int(data[team]['GP'])) + "   " + str(round(data[team]['PPG'],1)) )


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
    data[home]['PPG'] = data[home]['Points'] / data[home]['GP']
    data[away]['PPG'] = data[away]['Points'] / data[away]['GP']

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
    datestamp = date.today().strftime("%y%m%d")
    log = Log('logs/model_v2_' + str(datestamp) + '.log')

    # Database
    database.connect()

    # Load initial standings
    initial = dataInit(database)

    renderTable(initial)

    # Initialize output file
    # This is after the standings init because the first line of output is to
    # write the team abbreviations (array keys) as the header row.
    output = Output('output/model_v2_' + str(datestamp) + '.csv', initial)

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
