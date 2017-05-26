import database
from log import Log
from output import Output
import numpy as np


def calculatePPG(data):
    # This expects data in a form of
    # {'MIN': {'Points': 8.0, 'PPG': 0.8888888888888888, 'GP': 9.0}, 'TOR': {'Points': 16.0, 'PPG': 1.7777777777777777, 'GP': 9.0}}
    for team in data:
        data[team]['PPG'] = data[team]['Points'] / data[team]['GP']
    return data


def calculateThreshold(homePPG, awayPPG):
    # This calculates and returns a dictionary of thresholds for home wins
    # and draws. For now these are constants
    # log.message(str(homePPG) + ' Home PPG')
    # log.message(str(awayPPG) + ' Away PPG')

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
    # log.message(str(threshold))
    # log.message('')
    return threshold


def dataInit():
    # This initializes the nested dictionary that records the simulation output
    data = {}
    data['CLB'] = loadStats(11)
    data['DC'] = loadStats(12)
    data['CHI'] = loadStats(13)
    data['COL'] = loadStats(14)
    data['NE'] = loadStats(15)
    data['DAL'] = loadStats(16)
    data['SJ'] = loadStats(17)
    data['KC'] = loadStats(18)
    data['LA'] = loadStats(19)
    data['NY'] = loadStats(20)
    data['POR'] = loadStats(42)
    data['SEA'] = loadStats(43)
    data['VAN'] = loadStats(44)
    data['MON'] = loadStats(45)
    data['RSL'] = loadStats(340)
    data['HOU'] = loadStats(427)
    data['TOR'] = loadStats(463)
    data['PHI'] = loadStats(479)
    data['ORL'] = loadStats(506)
    data['MIN'] = loadStats(521)
    data['NYC'] = loadStats(547)
    data['ATL'] = loadStats(599)
    data = calculatePPG(data)
    return data


def loadGames():
    # This should be passed from outside, so we just get records once
    sql = ("SELECT g.ID, h.team3ltr AS Home, a.team3ltr AS Away "
           "FROM tbl_games g "
           "INNER JOIN tbl_teams h on g.HTeamID = h.ID "
           "INNER JOIN tbl_teams a on g.ATeamID = a.ID "
           "WHERE YEAR(g.MatchTime) = 2017 "
           "AND g.MatchTypeID = 21 "
           "AND g.MatchTime > NOW() "
           "ORDER BY g.MatchTime ASC")
    log.message(sql)
    rs = database.query(sql, ())

    if (rs.with_rows):
        records = rs.fetchall()

    return records


def loadStats(teamid):
    # This calculates a given team's GP, Points, and PPG values.
    # It is part of the initialization step.
    sql = ("SELECT HTeamID, HScore, ATeamID, AScore "
           "FROM tbl_games "
           "WHERE YEAR(MatchTime) = 2017 "
           "  AND MatchTime < NOW() "
           "  AND (HTeamID = %s OR ATeamID = %s) "
           "  AND MatchTypeID = 21")
    rs = database.query(sql, (teamid, teamid))

    if (rs.with_rows):
        records = rs.fetchall()

    stats = {}
    stats['GP'] = 0.0
    stats['Points'] = 0.0
    for game in records:
        # Increment games played
        stats['GP'] += 1
        # Increment points
        if (game[1] == game[3]):
            stats['Points'] += 1
        elif (game[0] == teamid):
            if (game[1] > game[3]):
                stats['Points'] += 3
        else:
            if (game[3] > game[1]):
                stats['Points'] += 3

    return stats


def logStandings(log, standings):
    log.message('Team Pts GP PPG')
    # Maybe we can make this prettier
    for key in sorted(standings.keys()):
        log.message(str(key) + ': ' + str(standings[key]['Points']) + ' ' + str(standings[key]['GP']) + ' ' + str(standings[key]['PPG']))
    log.message('')


def simulateGame(data, home, away, log):
    # log.message(str(home) + ' vs ' + str(away))

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


def simulateSeason(gamelist, log, output, database, initialdata):
    # Initialize starting data
    thisdata = dataInit()
    # thisdata = initialdata

    # Log initial standings
    log.message('Starting position:')
    logStandings(log, thisdata)

    # For each game in the list, simulate the result and calculate points array
    for game in enumerate(gamelist):
        thisdata = simulateGame(thisdata, game[1][1], game[1][2], log)

    # After simulating all games
    # Store final points totals for all teams in CSV file for later analysis
    output.points(thisdata)


if __name__ == "__main__":
    # Log
    log = Log('logs/model170501_test.log')

    # Database
    database.connect()

    # We do this now because the Output class needs it
    initial = dataInit()
    log.message(str(initial))

    # Log initial standings
    log.message('Starting position:')
    logStandings(log, initial)

    # Initialize output file
    # This is after the data init because the first step is to
    # write the array keys as the header row.
    output = Output('output/model_v2_test.csv', initial)

    # Get list of games
    schedule = loadGames()

    # Simulate all season
    for i in range(10):
        log.message('Season ' + str(i))
        # This doesn't pass in data because the function will re-call that init
        simulateSeason(schedule, log, output, database, initial)

    # End simulating a season

    # Shut down
    database.disconnect()
    output.end()
    log.end()
