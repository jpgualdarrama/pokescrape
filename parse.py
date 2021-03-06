import os.path
import urllib.request
# import urllib3
from html.parser import HTMLParser
from pk import *
from pokemon import *
from move import *
from ability import *

nameMap = {}
baseExpYields = [0 for i in range(0, num_pokemon + 1)]
colors = [0 for i in range(0, num_pokemon + 1)]
bodyStyles = [0 for i in range(0, num_pokemon + 1)]

def Init():
    # http = urllib3
    loadNames()
    loadBaseExpYields()
    loadColors()
    loadBodyStyles()
    loadMoves()
    loadAbilities()

def loadNames():
    source = open('input_files/names.txt')
    
    for line in source:
        pieces = line.split('\t')
        name = pieces[1].strip().lower()
        nameMap[name] = int(pieces[0].strip())
    
    source.close()
    
    
def loadBaseExpYields():
    source = open('input_files/baseexpyields.txt')
    
    for line in source:
        pieces = line.split('\t')
        name = pieces[2].strip().lower()
        baseExpYields[nameMap[name]] = int(pieces[3].strip())
    
    source.close()

def loadColors():
    source = open('input_files/colors.txt')
    
    cur_color = 0
    for line in source:
        if line.strip().isdigit():
            cur_color = int(line.strip())
        else:
            pieces = line.split('\t')
            for piece in pieces:
                name = piece.strip().lower()
                if name in nameMap:
                    colors[nameMap[name]] = cur_color
    
    source.close()

def loadBodyStyles():
    source = open('input_files/bodystyles.txt')
    
    cur_style = 0
    for line in source:
        if line.strip().isdigit():
            cur_style = int(line.strip())
        else:
            pieces = line.split('\t')
            name = pieces[1].strip().lower()
            if name in nameMap:
                bodyStyles[nameMap[name]] = cur_style
    
    source.close()

def loadMoves():
    source = open('input_files/moves.txt')
    
    for line in source:
        pieces = line.split('\t')
        
        move = Move()
        move.name = pieces[0]
        if pieces[1] == 'NOR':
            move.type = 1
        elif pieces[1] == 'FIG':
            move.type = 2
        elif pieces[1] == 'FLY':
            move.type = 3
        elif pieces[1] == 'POI':
            move.type = 4
        elif pieces[1] == 'GRO':
            move.type = 5
        elif pieces[1] == 'ROC':
            move.type = 6
        elif pieces[1] == 'BUG':
            move.type = 7
        elif pieces[1] == 'GHO':
            move.type = 8
        elif pieces[1] == 'STE':
            move.type = 9
        elif pieces[1] == 'FIR':
            move.type = 10
        elif pieces[1] == 'WAT':
            move.type = 11
        elif pieces[1] == 'GRA':
            move.type = 12
        elif pieces[1] == 'ELE':
            move.type = 13
        elif pieces[1] == 'PSY':
            move.type = 14
        elif pieces[1] == 'ICE':
            move.type = 15
        elif pieces[1] == 'DRA':
            move.type = 16
        elif pieces[1] == 'DAR':
            move.type = 17
        elif pieces[1] == 'FAI':
            move.type = 18
        else:
            print('Failed to parse move type \'%s\'' % pieces[1])
        move.pp = int(pieces[2])
        move.power = 0 if pieces[3] == '-' else int(pieces[3])
        move.accuracy = 0 if pieces[4] == '-' else int(pieces[4])
        if pieces[5] == 'No Damage.':
            move.category = 3
            move.damage = 0
        else:
            if 'Physical Attack' in pieces[5]:
                move.category = 1
            elif 'Special Attack' in pieces[5]:
                move.category = 2
            else:
                print('Failed to parse category \'%s\'' % pieces[5])
            
            if 'Sp.Atk' in pieces[5]:
                if 'Sp.Def' in pieces[5]:
                    move.damage = 4
                elif 'Def' in pieces[5]:
                    move.damage = 2
                else:
                    print('Failed to parse damage \'%s\'' % pieces[5])
            elif 'Atk' in pieces[5]:
                if 'Sp.Def' in pieces[5]:
                    move.damage = 3
                elif 'Def' in pieces[5]:
                    move.damage = 1
                else:
                    print('Failed to parse damage \'%s\'' % pieces[5])
            else:
                print('Failed to parse damage \'%s\'' % pieces[5])
        move.description = pieces[6].strip()
        
        moves_map[move.name.lower()] = len(moves)
        moves.append(move)
    
    source.close()

def loadAbilities():
    source = open('input_files/abilities.txt', encoding='utf8')
    
    for line in source:
        pieces = line.split('\t')
        
        ability = Ability()
        ability.name = pieces[0]
        ability.description = pieces[1].strip()
        
        abilities_map[ability.name.lower()] = len(abilities)
        abilities.append(ability)
    
    source.close()

def GetAndParse(number, force = False):
    if not os.path.exists('cache'):
        os.makedirs('cache')

    suffix = '%03i.shtml' % number
    path = 'cache/' + suffix
    if force == True or os.path.isfile(path) == False:
        url = 'http://www.serebii.net/pokedex-xy/' + suffix
        print('Fetching \'%s\' to \'%s\'' % (url, path))
        data = urllib.request.urlopen(url)
        # data = http.request.urlopen(url)
        out = open(path, 'wb')
        out.write(data.read().decode('ISO-8859-1').replace('&eacute;', '\u00E9').encode('utf-8'))
        print('Using newly-fetched file \'%s\'' % path)
    else:
        print('Using already-fetched file \'%s\'' % path)
    
    source = open(path, 'r', encoding='utf8')
    parser = PokemonParser()
    parser.feed(source.read())
    source.close()
    
    parser.pokemon.color = colors[parser.pokemon.national_dex_number]
    parser.pokemon.body_style = bodyStyles[parser.pokemon.national_dex_number]
    parser.pokemon.base_exp_yield = baseExpYields[parser.pokemon.national_dex_number]
    
    print('Done parsing \'%s\'' % path)
    
    return parser.pokemon

class PokemonParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        
        self.pokemon = Pokemon()
        
        self.cur_fooinfo = 0
        self.td_cur_level = 0
        self.fooinfo_enter_level = -1
        self.fooinfo_cur_td = 0
        self.cen_enter_level = -1
        self.cen_cur_td = 0
        self.is_bold = False
        self.is_evo = False
        self.is_font = False
        self.fooinfo_temp = 0
    
    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            if ('class', 'fooinfo') in attrs:
                if self.fooinfo_enter_level != -1:
                    self.cur_fooinfo += 1
                    self.fooinfo_cur_td = 0
                    self.fooinfo_temp = 0
                self.fooinfo_enter_level = self.td_cur_level
            if ('class', 'cen') in attrs:
                if self.cen_enter_level != -1:
                    self.cen_cur_td = 0
                self.cen_enter_level = self.td_cur_level
            self.td_cur_level += 1
        # Parse types out of links
        if tag == 'a':
            if self.cen_enter_level != -1:
                if self.cur_fooinfo == 5:
                    ptype = PkType[attrs[0][1][12:-6]]
                    if self.pokemon.types[0] == 0:
                        self.pokemon.types = (ptype, 0)
                    else:
                        self.pokemon.types = (self.pokemon.types[0], ptype)
        self.is_bold = tag == 'b'
        self.is_evo = ('class', 'fooevo') in attrs
        self.is_font = tag == 'font'
    
    def handle_endtag(self, tag):
        if tag == 'td':
            self.td_cur_level -= 1
            if self.fooinfo_enter_level != -1:
                self.fooinfo_cur_td += 1
            if self.fooinfo_enter_level == self.td_cur_level:
                self.cur_fooinfo += 1
                self.fooinfo_enter_level = -1
                self.fooinfo_cur_td = 0
                self.fooinfo_temp = 0
            if self.cen_enter_level != -1:
                self.cen_cur_td += 1
            if self.cen_enter_level == self.td_cur_level:
                self.cen_enter_level = -1
                self.cen_cur_td = 0
    
    def handle_data(self, data):
        if self.is_evo:
            if data == 'Locations':
                self.cur_fooinfo = 18
            elif data == 'Flavor Text':
                self.cur_fooinfo = 50
            elif data == 'Generation VI Level Up':
                self.cur_fooinfo = 100
            elif data == 'TM & HM Attacks':
                self.cur_fooinfo = 400
            elif data == 'Egg Moves ':
                self.cur_fooinfo = 500
            elif data == 'Move Tutor Attacks':
                self.cur_fooinfo = 600
            elif data == 'Omega Ruby/Alpha Sapphire Move Tutor Attacks':
                self.cur_fooinfo = 700
            elif data == 'Special Moves':
                self.cur_fooinfo = 800
            elif data == 'Pre-Evolution Only Moves':
                self.cur_fooinfo = 900
            elif data == 'Transfer Only Moves ':
                self.cur_fooinfo = 1000
        
        if self.is_font:
            if data == 'X & Y Level Up':
                self.cur_fooinfo = 200
            elif data == '\u03A9R\u03B1S Level Up':
                self.cur_fooinfo = 300
        
        if self.is_bold:
            if data == 'Stats':
                self.cur_fooinfo = 1100
        
        if self.fooinfo_enter_level != -1:
            # 'Name'
            if self.cur_fooinfo == 1:
                self.pokemon.name = data
            # 'No.'
            elif self.cur_fooinfo == 3:
                if self.fooinfo_cur_td == 1:
                    self.pokemon.national_dex_number = int(data[1:])
            # 'Gender Ratio'
            elif self.cur_fooinfo == 4:
                if 'is Genderless' in data:
                    self.pokemon.gender_threshold = PkGender['0:0']
                elif self.fooinfo_cur_td == 1:
                    if data == '0%':
                        self.pokemon.gender_threshold = PkGender['0:1']
                    elif data == '12.5%':
                        self.pokemon.gender_threshold = PkGender['1:7']
                    elif data == '25%':
                        self.pokemon.gender_threshold = PkGender['1:3']
                    elif data == '50%':
                        self.pokemon.gender_threshold = PkGender['1:1']
                    elif data == '75%':
                        self.pokemon.gender_threshold = PkGender['3:1']
                    elif data == '87.5%':
                        self.pokemon.gender_threshold = PkGender['7:1']
                    elif data == '100%':
                        self.pokemon.gender_threshold = PkGender['1:0']
                    else:
                        print('Failed to parse gender ratio \'%s\'' % data)
            # 'Classification'
            elif self.cur_fooinfo == 5:
                self.pokemon.species = data[:-8]
            # 'Height'
            elif self.cur_fooinfo == 6:
                if 'm' in data:
                    self.pokemon.height = float(data.strip()[:-1])
            # 'Weight'
            elif self.cur_fooinfo == 7:
                if 'kg' in data:
                    self.pokemon.weight = float(data.strip()[:-2])
            # 'Capture Rate'
            elif self.cur_fooinfo == 8:
                if data != '(XY)' and data != '(\u03A9R\u03B1S)':
                    self.pokemon.catch_rate = int(data)
            # 'Base Egg Steps'
            elif self.cur_fooinfo == 9:
                if data != '\xa0':
                    self.pokemon.hatch_counter = int(data.replace(',', '')) // 255
            # 'Abilities'
            elif self.cur_fooinfo == 10:
                if self.is_bold:
                    if self.fooinfo_temp % 2 == 0:
                        if data == 'Hidden Ability':
                            self.fooinfo_temp = 4
                        else:
                            data = data.strip().lower()
                            if self.fooinfo_temp == 0:
                                self.pokemon.abilities = (abilities_map[data], 0, 0)
                            elif self.fooinfo_temp == 2:
                                self.pokemon.abilities = (self.pokemon.abilities[0], abilities_map[data], 0)
                            elif self.fooinfo_temp == 6:
                                self.pokemon.abilities = (self.pokemon.abilities[0], self.pokemon.abilities[1], abilities_map[data])
                    self.fooinfo_temp += 1
            # 'Experience Growth'
            elif self.cur_fooinfo == 11:
                if not 'Points' in data:
                    if data == 'Slow':
                        self.pokemon.exp_group = PkExpGroup['slow']
                    elif data == 'Medium Slow':
                        self.pokemon.exp_group = PkExpGroup['mediumslow']
                    elif data == 'Medium Fast':
                        self.pokemon.exp_group = PkExpGroup['mediumfast']
                    elif data == 'Fast':
                        self.pokemon.exp_group = PkExpGroup['fast']
                    elif data == 'Erratic':
                        self.pokemon.exp_group = PkExpGroup['erratic']
                    elif data == 'Fluctuating':
                        self.pokemon.exp_group = PkExpGroup['fluctuating']
                    else:
                        print('Failed to parse experience group \'%s\'' % data)
            # 'Base Happiness'
            elif self.cur_fooinfo == 12:
                self.pokemon.base_friendship = int(data)
            # 'Effort Values Earned'
            elif self.cur_fooinfo == 13:
                n = int(data[:1])
                y = self.pokemon.ev_yield
                if 'HP' in data:
                    self.pokemon.ev_yield = (n, y[1], y[2], y[3], y[4], y[5])
                elif 'Sp. Attack' in data:
                    self.pokemon.ev_yield = (y[0], y[1], y[2], n, y[4], y[5])
                elif 'Sp. Defense' in data:
                    self.pokemon.ev_yield = (y[0], y[1], y[2], y[3], n, y[5])
                elif 'Attack' in data:
                    self.pokemon.ev_yield = (y[0], n, y[2], y[3], y[4], y[5])
                elif 'Defense' in data:
                    self.pokemon.ev_yield = (y[0], y[1], n, y[3], y[4], y[5])
                elif 'Speed' in data:
                    self.pokemon.ev_yield = (y[0], y[1], y[2], y[3], y[4], n)
                else:
                    print('Failed to parse EV yield \'%s\'' % data)
            # 'Egg Groups'
            elif self.cur_fooinfo == 15:
                data = data.strip().lower()
                if 'cannot breed' in data:
                    self.pokemon.egg_groups = (PkEggGroup['undiscovered'], 0)
                elif data == 'ditto':
                    if self.pokemon.national_dex_number == 132:
                        self.pokemon.egg_groups = (PkEggGroup['ditto'], 0)
                elif data != '':
                    if data in PkEggGroup:
                        group = PkEggGroup[data]
                        if self.pokemon.egg_groups[0] == 0:
                            self.pokemon.egg_groups = (group, 0)
                        elif self.pokemon.egg_groups[0] != group:
                            self.pokemon.egg_groups = (self.pokemon.egg_groups[0], group)
            # 'Flavor Text' (X)
            elif self.cur_fooinfo == 50:
                self.pokemon.pokedex_x = data
                # XXX Compensate for Serebii's double closing tags at the end of pokedex entries
                self.td_cur_level += 1
            # 'Flavor Text' (Y)
            elif self.cur_fooinfo == 51:
                self.pokemon.pokedex_y = data
                # XXX Compensate for Serebii's double closing tags at the end of pokedex entries
                self.td_cur_level += 1
            # 'Flavor Text' (OR/AS?)
            elif self.cur_fooinfo == 52:
                self.pokemon.pokedex_or = data
                self.pokemon.pokedex_as = data
                # XXX Compensate for Serebii's double closing tags at the end of pokedex entries
                self.td_cur_level += 1
            # 'Flavor Text' (AS)
            elif self.cur_fooinfo == 53:
                self.pokemon.pokedex_as = data
                # XXX Compensate for Serebii's double closing tags at the end of pokedex entries
                self.td_cur_level += 1
            # 'Gen VI Level Up'
            elif self.cur_fooinfo >= 100 and self.cur_fooinfo < 200:
                data = data.strip()
                index = (self.cur_fooinfo - 100) // 3
                offset = (self.cur_fooinfo - 100) % 3
                if offset == 0:
                    level = 0 if data == '\u2014' else int(data)
                    self.pokemon.learnset_level_xy.append(level)
                    self.pokemon.learnset_level_oras.append(level)
                elif offset == 1:
                    self.pokemon.learnset_level_xy.append((self.pokemon.learnset_level_xy.pop(), moves_map[data.lower()]))
                    self.pokemon.learnset_level_oras.append((self.pokemon.learnset_level_oras.pop(), moves_map[data.lower()]))
                elif offset == 2:
                    self.cur_fooinfo = 100 + offset
            # 'X & Y Level Up'
            elif self.cur_fooinfo >= 200 and self.cur_fooinfo < 300:
                data = data.strip()
                index = (self.cur_fooinfo - 200) // 3
                offset = (self.cur_fooinfo - 200) % 3
                if offset == 0:
                    level = 0 if data == '\u2014' else int(data)
                    self.pokemon.learnset_level_xy.append(level)
                elif offset == 1:
                    self.pokemon.learnset_level_xy.append((self.pokemon.learnset_level_xy.pop(), moves_map[data.lower()]))
                elif offset == 2:
                    self.cur_fooinfo = 200 + offset
            # 'ORaS Level Up'
            elif self.cur_fooinfo >= 300 and self.cur_fooinfo < 400:
                data = data.strip()
                index = (self.cur_fooinfo - 300) // 3
                offset = (self.cur_fooinfo - 300) % 3
                if offset == 0:
                    level = 0 if data == '\u2014' else int(data)
                    self.pokemon.learnset_level_oras.append(level)
                elif offset == 1:
                    self.pokemon.learnset_level_oras.append((self.pokemon.learnset_level_oras.pop(), moves_map[data.lower()]))
                elif offset == 2:
                    self.cur_fooinfo = 300 + offset
            # 'TM & HM Attacks'
            elif self.cur_fooinfo >= 400 and self.cur_fooinfo < 500:
                data = data.strip()
                index = (self.cur_fooinfo - 400) // 3
                offset = (self.cur_fooinfo - 400) % 3
                if offset == 1:
                    self.pokemon.learnset_machine.append(moves_map[data.lower()])
                elif offset == 2:
                    self.cur_fooinfo = 400 + offset
            # 'Egg Moves'
            elif self.cur_fooinfo >= 500 and self.cur_fooinfo < 600:
                data = data.strip()
                index = (self.cur_fooinfo - 500) // 9
                offset = (self.cur_fooinfo - 500) % 9
                if offset == 0:
                    self.pokemon.learnset_egg_move.append(moves_map[data.lower()])
                    if data != 'Volt Tackle':
                        self.cur_fooinfo += 7
                elif offset == 8:
                    self.cur_fooinfo = 500 + offset
            # 'Move Tutor Attacks'
            elif self.cur_fooinfo >= 600 and self.cur_fooinfo < 700:
                data = data.strip()
                index = (self.cur_fooinfo - 600) // 8
                offset = (self.cur_fooinfo - 600) % 8
                if offset == 0:
                    self.pokemon.learnset_tutor.append(moves_map[data.lower()])
                elif offset == 7:
                    self.cur_fooinfo = 600 + offset
            # 'Omega Ruby/Alpha Sapphire Move Tutor Attacks'
            elif self.cur_fooinfo >= 700 and self.cur_fooinfo < 800:
                data = data.strip()
                index = (self.cur_fooinfo - 700) // 8
                offset = (self.cur_fooinfo - 700) % 8
                if offset == 0:
                    self.pokemon.learnset_tutor.append(moves_map[data.lower()])
                elif offset == 7:
                    self.cur_fooinfo = 700 + offset
            # 'Special Moves'
            elif self.cur_fooinfo >= 800 and self.cur_fooinfo < 900:
                data = data.strip()
                index = (self.cur_fooinfo - 800) // 9
                offset = (self.cur_fooinfo - 800) % 9
                if offset == 0:
                    self.pokemon.learnset_special.append(moves_map[data.lower()])
                elif offset == 8:
                    self.cur_fooinfo = 800 + offset
            # 'Pre-Evolution Only Moves'
            elif self.cur_fooinfo >= 900 and self.cur_fooinfo < 1000:
                data = data.strip()
                index = (self.cur_fooinfo - 900) // 3
                offset = (self.cur_fooinfo - 900) % 3
                if offset == 0:
                    self.pokemon.learnset_evolve.append(moves_map[data.lower()])
                elif offset == 2:
                    self.cur_fooinfo = 900 + offset
            # 'Transfer Only Moves'
            elif self.cur_fooinfo >= 1000 and self.cur_fooinfo < 1100:
                data = data.strip()
                index = (self.cur_fooinfo - 1000) // 2
                offset = (self.cur_fooinfo - 1000) % 2
                if offset == 0:
                    self.pokemon.learnset_transfer.append(moves_map[data.lower()])
                elif offset == 1:
                    self.cur_fooinfo = 1000 + offset
            # 'Stats'
            elif self.cur_fooinfo >= 1101 and self.cur_fooinfo < 1107:
                b = self.pokemon.base_stats
                index = self.cur_fooinfo - 1101
                n = int(data)
                if index == 0:
                    self.pokemon.base_stats = (n, b[1], b[2], b[3], b[4], b[5])
                elif index == 1:
                    self.pokemon.base_stats = (b[0], n, b[2], b[3], b[4], b[5])
                elif index == 2:
                    self.pokemon.base_stats = (b[0], b[1], n, b[3], b[4], b[5])
                elif index == 3:
                    self.pokemon.base_stats = (b[0], b[1], b[2], n, b[4], b[5])
                elif index == 4:
                    self.pokemon.base_stats = (b[0], b[1], b[2], b[3], n, b[5])
                elif index == 5:
                    self.pokemon.base_stats = (b[0], b[1], b[2], b[3], b[4], n)

