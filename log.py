class Log():

    def __init__(self, name):
        self.file = open(name, 'w')
        self.file.write('Log start\n')
        return None

    def message(self, msg):
        return self.file.write(msg + '\n')

    def standings(self, array):
        self.file.write('Team Pts GP PPG\n')
        for key in sorted(array.keys()):
            self.file.write(str(key) + ': ')
            self.file.write(str(array[key]['Points']) + ' ')
            self.file.write(str(array[key]['GP']) + ' ')
            self.file.write(str(array[key]['PPG']) + '\n')
        self.file.write('\n')

    def end(self):
        self.file.write('Log end\n')
        return self.file.close()
