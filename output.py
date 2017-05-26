class Output():

    def __init__(self, name, array):
        self.file = open(name, 'w')
        for key in sorted(array.keys()):
            self.file.write(str(key) + ',')
        self.file.write('\n')
        return None

    def message(self, msg):
        return self.file.write(msg + '\n')

    def points(self, array):
        for key in sorted(array.keys()):
            self.file.write(str(array[key]['Points']) + ',')
        self.file.write('\n')

    def end(self):
        return self.file.close()
