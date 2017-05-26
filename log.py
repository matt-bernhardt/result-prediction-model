class Log():

    def __init__(self, name):
        self.file = open(name, 'w')
        self.file.write('Log start\n')
        return None

    def message(self, msg):
        return self.file.write(msg + '\n')

    def end(self):
        self.file.write('Log end\n')
        return self.file.close()
