import os.path
import urllib.request
from urllib.error import HTTPError
import re
from bs4 import BeautifulSoup
from pokemonParser import *
from pk import *
from move import *
from ability import *

nameToNumberMap = {}
numberToNameMap = {}
baseExpYields = [0 for i in range(0, num_pokemon + 1)]
colors = [0 for i in range(0, num_pokemon + 1)]
bodyStyles = [0 for i in range(0, num_pokemon + 1)]

def Init():
    loadNames()
    loadBaseExpYields()
    loadColors()
    loadBodyStyles()
    loadMoves()
    loadAbilities()

def loadNames():
    src = "input_files/names.txt"
    if os.path.exists(src):
        source = open('input_files/names.txt')

        for line in source:
            pieces = line.split('\t')
            name = pieces[1].strip().lower()
            nameToNumberMap[name] = int(pieces[0].strip())
            numberToNameMap[int(pieces[0].strip())] = name

        source.close()
    else:
        url = "http://serebii.net/pokedex-swsh/"
        raw_data = urllib.request.urlopen(url)
        data = raw_data.read().decode('ISO-8859-1').replace('&eacute;', '\u00E9').encode('utf-8')
        soup = BeautifulSoup(data, features="html.parser")
        forms = soup.find_all("form")

        # the first two forms are unrelated to the pokedex
        forms = forms[2:]

        ################################
        # generate a list of pokemon from the forms
        # that contain numbers in the first option
        options = [form.find('option') for form in forms]

        regional_dex_forms = []
        regional_dex_re = re.compile("^[A-Z][a-z]+:\s*[0-9]+\s*-\s*[0-9]+$")
        for i in range(0, len(options)):
          if options[i].string is not None:
            if regional_dex_re.match(options[i].string):
              print("%i -> %s" % (i, options[i].string))
              regional_dex_forms.append(forms[i])

        pokemon_re = re.compile("^([0-9]+)\s*(.*)")
        for form in regional_dex_forms:
          options = [opt.string for opt in form.find_all("option") \
            if opt.string is not None]
          # remove the first option that is just the name of the dex
          options.pop(0)
          for opt in options:
            m = pokemon_re.match(opt)
            if m is None:
                print ("ERROR - no Pokemon match found in option " + opt)
            else:
                number = int(m.group(1))
                name = m.group(2).lower()
                nameToNumberMap[name] = number
                numberToNameMap[number] = name
    
def loadBaseExpYields():
    source = open('input_files/baseexpyields.txt')
    
    for line in source:
        pieces = line.split('\t')
        name = pieces[2].strip().lower()
        baseExpYields[nameToNumberMap[name]] = int(pieces[3].strip())
    
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
                if name in nameToNumberMap:
                    colors[nameToNumberMap[name]] = cur_color
    
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
            if name in nameToNumberMap:
                bodyStyles[nameToNumberMap[name]] = cur_style
    
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
    name = numberToNameMap[number]
    will_parse = True
    if force == True or os.path.isfile(path) == False:
        # url = 'http://www.serebii.net/pokedex-xy/' + suffix
        url = 'http://www.serebii.net/pokedex-swsh/' + name
        # cleanup un-allowed characters
        url = url.replace('&eacute;', '\u00E9').replace('\u2640', 'f').replace('\u2642', 'm')
        print('Fetching \'%s\' to \'%s\'' % (url, path))
        try:
            data = urllib.request.urlopen(url)
            out = open(path, 'wb')
            out.write(data.read().decode('ISO-8859-1').replace('&eacute;', '\u00E9').encode('utf-8'))
            print('Using newly-fetched file \'%s\'' % path)
        except HTTPError as e:
            print("Unable to read url %s" % url)
            will_parse = False
            
    else:
        print('Using already-fetched file \'%s\'' % path)
        pass

    if will_parse:
        source = open(path, 'r', encoding='utf8')
        parser = PokemonParser(source)
        parser.parse(name)
        source.close()
        
        # parser.pokemon.color = colors[parser.pokemon.national_dex_number]
        # parser.pokemon.body_style = bodyStyles[parser.pokemon.national_dex_number]
        # parser.pokemon.base_exp_yield = baseExpYields[parser.pokemon.national_dex_number]
    
        print('Done parsing \'%s\'' % path)
    
        return parser.pokemon
    else:
        return None
