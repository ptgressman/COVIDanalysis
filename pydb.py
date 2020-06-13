import ast,re

class Database(object):
    def __init__(self):
        self.records = []
        self.selected = {}
    def select(self,**kwargs):
        for index in range(len(records)):
            if index not in self.selected:
                valid = True
                for item in kwargs:
                    if item not in self.records[index]:
                        valid = False
                        break
                    elif type(self.records[index][item]) == list and kwargs[item] not in self.records[index][item]:
                        valid = False
                        break
                    elif self.records[index][item] != kwargs[item]:
                        valid = False
                        break
                if valid:
                    self.selected[index] = True
    def deselect(self,**kwargs):
        for index in range(len(records)):
            if index in self.selected:
                valid = True
                for item in kwargs:
                    if item not in self.records[index]:
                        valid = False
                        break
                    elif type(self.records[index][item]) == list and kwargs[item] not in self.records[index][item]:
                        valid = False
                        break
                    elif self.records[index][item] != kwargs[item]:
                        valid = False
                        break
                if valid:
                    del self.selected[index]

    def exporttxt(self):
        result = ''
        for item in self.records:
            result += self._to_string(item)
        return result
    def importtxt(self,textstuff):
        structure = self._from_string(textstuff)
        if type(structure) == 'dict':
            structure = [structure]
        self.records = structure
    def _to_string(self,record,depth=0):
        if depth > 0:
            result = '\n'
        else:
            result = ''
        result += ' ' * depth + '<record%i>\n' % (depth)
        for key in record:
            if type(record[key]) != list:
                values = [record[key]]
            else:
                values = record[key]
            for item in values:
                if type(item) == dict:
                    typestr = 'record'
                    item = self._to_string(item,depth+2)
                elif type(item) == str:
                    typestr = 'string'
                else:
                    typestr = 'literal'
                result += ' ' * (depth+1) + '<key%i name="%s" type="%s">%s</key%i>\n' % (depth+1,str(key),typestr,str(item),depth+1)
        result += ' ' * depth + '</record%i>'% (depth)
        if depth > 0:
            result += '\n' + ' ' * (depth-1)
        return result
    def _from_string(self,dbstring):
        resultobj = {}
        opener = re.search(r'<(record\d+)>',dbstring)
        if opener is None:
            return resultobj
        recordtitle = opener.group(1)
        opattern = re.compile(r'<' + recordtitle + r'>(?P<contents>(.|\n)*?)</' + recordtitle + '>')
        for opener in re.finditer(opattern,dbstring):
            resultdict = {}
            substring = opener.group('contents')
            level = int(re.search(r'\d+',recordtitle).group(0))
            keytype = 'key' + str(int(level+1))
            keydata = re.compile(r'<' + keytype + ' name="(?P<name>[^"]*)" type="(?P<type>[^"]*)">(?P<contents>(.|\n)*?)</' + keytype + '>')
            for result in re.finditer(keydata,dbstring):
                keyname = result.group('name')
                keytype = result.group('type')
                keycontent = result.group('contents')
                if keytype == 'string':
                    keyobj = keycontent
                elif keytype == 'literal':
                    keyobj = ast.literal_eval(keycontent)
                elif keytype == 'record':
                    keyobj = self._from_string(keycontent)
                if keyname not in resultdict:
                    resultdict[keyname] = keyobj
                else:
                    if type(resultdict[keyname]) != list:
                        resultdict[keyname] = [resultdict[keyname]]
                    resultdict[keyname].append(keyobj)
            if len(resultobj) == 0:
                resultobj = resultdict
            elif len(resultdict) > 0:
                if type(resultobj) != list:
                    resultobj = [resultobj]
                resultobj.append(resultdict)
        return resultobj



db = Database()
db.records=[{'case': '2020-06-12', 'death': '2020-06-12', 'records': {'Adams': [284, 3973, 9], 'Allegheny': [2065, 39522, 171], 'Armstrong': [66, 1550, 5], 'Beaver': [611, 4647, 75], 'Bedford': [46, 1007, 2], 'Berks': [4281, 14970, 338], 'Blair': [54, 3662, 1], 'Bradford': [46, 2341, 3], 'Bucks': [5396, 25608, 541], 'Butler': [256, 4538, 12], 'Cambria': [62, 5199, 3], 'Carbon': [257, 3129, 24], 'Centre': [165, 2806, 7], 'Chester': [3247, 18241, 306], 'Clarion': [30, 773, 2], 'Clinton': [61, 1036, 3], 'Columbia': [371, 1796, 33], 'Cumberland': [709, 7694, 58], 'Dauphin': [1587, 13098, 107], 'Delaware': [6837, 26918, 612], 'Erie': [439, 7339, 7], 'Fayette': [95, 3932, 4], 'Franklin': [837, 6436, 42], 'Fulton': [16, 314, 1], 'Huntingdon': [237, 1104, 4], 'Indiana': [93, 1714, 5], 'Jefferson': [18, 657, 1], 'Juniata': [105, 466, 5], 'Lackawanna': [1598, 8195, 191], 'Lancaster': [3682, 20606, 325], 'Lawrence': [86, 1809, 8], 'Lebanon': [1140, 5905, 39], 'Lehigh': [3926, 18045, 264], 'Luzerne': [2823, 14265, 162], 'Lycoming': [168, 2904, 17], 'McKean': [13, 855, 1], 'Mercer': [114, 2138, 6], 'Mifflin': [59, 1572, 1], 'Monroe': [1347, 7664, 103], 'Montgomery': [7834, 43001, 753], 'Northampton': [3217, 17448, 238], 'Northumberland': [219, 2018, 4], 'Perry': [70, 1039, 5], 'Philadelphia': [19746, 74661, 1487], 'Pike': [482, 2405, 20], 'Schuylkill': [677, 6156, 43], 'Snyder': [59, 547, 1], 'Somerset': [39, 2565, 1], 'Susquehanna': [166, 1142, 17], 'Tioga': [20, 783, 2], 'Union': [81, 1521, 2], 'Washington': [153, 5569, 6], 'Wayne': [125, 1388, 9], 'Westmoreland': [483, 12264, 38], 'Wyoming': [36, 714, 7], 'York': [1141, 17096, 31]}}]

db.records.append( {'title' : "Mongolia"})
result = db.exporttxt()
print(result)
db.importtxt(result)
print(db.records)
