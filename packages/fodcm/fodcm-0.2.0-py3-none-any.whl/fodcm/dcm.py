from pathlib import Path
from fofunction import Map, Curve, Axis
from .parser import Parser
from .generator import Generator


class DCM(object):
    '''
    DCM class import and export DCM file format
    '''

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.generator = Generator()
        my_file = Path(filename)
        # if my_file.is_file():
        #    self.read()
        # else:
        self.params = dict()

    def read(self):
        file = open(self.filename, 'r')
        text = file.read()
        file.close()
        self.parser = Parser()
        self.params = self.parser.parse(text)

    def map(self, map):
        '''
        Generate output for Map
        '''
        output = ''
        x = map._x
        output += self.generator.STUETZSTELLENVERTEILUNG(x.name, x.values)
        y = map._y
        output += self.generator.STUETZSTELLENVERTEILUNG(y.name, y.values)

        output += self.generator.GRUPPENKENNFELD(map)
        return output
        return output

    def curve(self, curve):
        '''
        generate output for curve
        '''
        output = ''
        x = curve._x
        output += self.generator.STUETZSTELLENVERTEILUNG(x.name, x.values)
        print(curve._y)
        output += self.generator.GRUPPENKENNLINIE(curve)
        return output

    def value(self, value, name):
        '''
        Generate output for value
        '''
        return self.generator.FESTWERT(name, value)

    def generate(self):
        '''
        Generate the DCM file
        '''
        writer = Generator()
        file = open(self.filename, 'w')
        output = ''
        for key in self.params.keys():
            param = self.params[key]
            if type(param) == Map:
                output += self.map(param)
                continue
            if type(param) == Curve:
                output += self.curve(param)
                continue
            output += self.value(param, key)
        file.write(output)
        file.close()
