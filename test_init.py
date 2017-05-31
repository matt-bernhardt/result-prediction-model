# This is to work out how to initialize a variable once and then reset to
# that state repeatedly.
import copy
import database
from log import Log
from output import Output


def calculatePPG(data):
    # This expects data in a form of
    # {'MIN': {'Points': 8.0, 'PPG': 0.8888888888888888, 'GP': 9.0}, 'TOR': {'Points': 16.0, 'PPG': 1.7777777777777777, 'GP': 9.0}}
    for team in data:
        data[team]['PPG'] = data[team]['Points'] / data[team]['GP']
    return data


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
    stats['GP'] = 0.0
    stats['Points'] = 0.0
    for game in records:
        stats['GP'] = game[4]
        stats['Points'] = game[5]

    return stats


def simulateGame(log, game, season):
    # For now we just make this really simple
    season['ATL']['Points'] += 1

    # Log initial standings
    log.message('Initial:')
    log.standings(initial)
    log.message('')

    return season


def simulateSeason(log, output, gamelist, season):

    # Initialize starting data
    this = copy.deepcopy(season)

    log.message('Season before change')
    log.message(str(type(season)))
    log.standings(season)

    log.message('Make change to copy')
    log.message(str(type(this)))
    log.message('')
    this['ATL']['Points'] += 10

    log.message('Season after change')
    log.message(str(type(season)))
    log.standings(season)

    # For each event, do X
    for event in enumerate(gamelist):
        this = simulateGame(log, event, this)

    # Log and output the outcome of what we have done
    log.message("Final Standings this season")
    log.standings(this)
    output.points(this)


if __name__ == "__main__":
    # Log
    log = Log('logs/test_init.log')

    # Database
    database.connect()

    # Initial variable condition
    initial = dataInit(database)
    log.standings(initial)

    # Initialize output file
    output = Output('output/test_init.csv', initial)

    # Get list of games
    schedule = ['a', 'b', 'c', 'd']

    # Simulate all seasons
    for i in range(10):
        log.message('######################################################')
        log.message('######################################################')
        log.message('Cycle ' + str(i))
        simulateSeason(log, output, schedule, initial)
        log.message('')
        log.message('')

    # Shut down
    database.disconnect()
    log.end()
