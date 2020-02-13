from bs4 import BeautifulSoup
from bs4.element import *
from pokemon import *
import re
import os

class PokemonParser():
    def __init__(self, handle):
        self.pokemon = Pokemon()

        # self.soup = BeautifulSoup(handle, features="html.parser")
        self.soup = BeautifulSoup(handle, features="lxml")

    def parse(self):
        dextables = self.soup.find_all("table", class_="dextable")

        self.processPictureDexTable(                       dextables[0])
        general_info = self.processGeneralInfoDexTable(    dextables[1])
        detail_info = self.processDetailedInfoDexTable(    dextables[2])
        self.processWeaknessesDexTable(                    dextables[3])
        item_and_egg_info = self.processItemAndEggDexTable(dextables[4])
        self.processEvolutionDexTable(                     dextables[5])
        if len(dextables[6].contents) > 1 and \
           len(dextables[6].contents[1].contents) > 1 and \
           dextables[6].contents[1].contents[1].string == "Gender Differences":
            goffset = 1
        else:
            goffset = 0
        self.processLocationsDexTable(                     dextables[goffset+6])
        flavor_text_info = self.processDexTextDexTable(    dextables[goffset+7])
        levelup_info = self.processLevelUpMovesDexTable(   dextables[goffset+8])
        tm_info = self.processTMMovesDexTable(             dextables[goffset+9])
        tr_info = self.processTRMovesDexTable(             dextables[goffset+10])
        eggmoves_info = self.processEggMovesDexTable(      dextables[goffset+11])
        tutor_info = self.processTutorMovesDexTable(       dextables[goffset+12])
        self.processMaxMovesDexTable(                      dextables[goffset+13])
        if len(dextables[goffset+14].contents) > 1 and \
           dextables[goffset+14].contents[0].string == "Transfer Only Moves":
            stats_info = self.processStatsDexTable(        dextables[goffset+16])
        else:
            stats_info = self.processStatsDexTable(        dextables[goffset+14])

        self.pokemon.name = general_info['name']
        self.pokemon.national_dex_number = general_info['number']
        self.pokemon.gender_threshold = general_info['gender_percents']
        self.pokemon.types = general_info['types']
        self.pokemon.species = general_info['classification']
        self.pokemon.height = general_info['height']
        self.pokemon.weight = general_info['weight']
        self.pokemon.catch_rate = general_info['capture_rate']
        self.pokemon.hatch_counter = general_info['egg_steps']
        self.pokemon.abilities = detail_info['abilities']
        self.pokemon.exp_group = detail_info['exp_group']
        self.pokemon.base_friendship = detail_info['base_happiness']
        self.pokemon.ev_yield = detail_info['ev_yield']
        self.pokemon.can_dynamax = detail_info['can_dynamax']
        self.pokemon.egg_groups = item_and_egg_info['egg_groups']
        self.pokemon.pokedex = flavor_text_info['flavor_text']
        self.pokemon.base_stats = stats_info['base_stats']

    def processPictureDexTable(self, dt):
        pass
    def processGeneralInfoDexTable(self, dt):
        trs = [tr for tr in dt.contents if not isinstance(tr, NavigableString)]
        # trs[0] and trs[2] are just headers
        # trs[1] and trs[3] each contain 5 <td>
        # trs[1]
        tds = [td for td in trs[1].contents if not isinstance(td, NavigableString)]
        # > tds[0] - Name
        name = tds[0].string.lower()
        # > tds[1] - Other names
        # > tds[2] - Pokedex Number
        # use find to only get first tr, don't want region dex
        national_dex_number = int(tds[2].find("tr").find_all("td")[1].string[1:])
        # > tds[3] - Gender Ratio
        # the first td in each tr contains "Male" or "Female"
        # the second td in each tr contains the actual percentage
        gender_percents = [tr.find_all("td")[1].string for tr in tds[3].find_all("tr")]
        gender_percents = [float(p[:-1]) for p in gender_percents]
        # > tds[4] - Types
        types_links = tds[4].find_all("a")
        types = [re.match('^.*\/([a-z]+)\.shtml$', link['href']).group(1) for link in types_links]
        types = [PkType[t] for t in types]
        # trs[3]
        tds = trs[3].find_all("td")
        # > tds[0] - Classification
        classification = tds[0].string[:-8]
        # > tds[1] - Height
        height_list = [tds[1].contents[0].string, tds[1].contents[2].string]
        height_list = [h.strip() for h in height_list]
        height = {
            'imperial': height_list[0],
            'metric': height_list[1]
        }
        # > tds[2] - Weight
        weight_list = [tds[2].contents[0].string, tds[2].contents[2].string]
        weight_list = [w.strip() for w in weight_list]
        weight = {
            'imperial': weight_list[0],
            'metric': weight_list[1]
        }
        # > tds[3] - Capture Rate
        capture_rate = int(tds[3].string)
        # > tds[4] - Base Egg Steps
        egg_steps = int(tds[4].string.replace(',', ''))
        
        return {
            'name': name,
            'number': national_dex_number,
            'gender_percents': gender_percents,
            'types': types,
            'classification': classification,
            'height': height,
            'weight': weight,
            'capture_rate': capture_rate,
            'egg_steps': egg_steps
        }
    
    def processDetailedInfoDexTable(self, dt):
        # Necessary info:
        # 1. Abilities
        # 2. Experience Growth
        # 3. Base Happiness
        # 4. Effort Values Earned
        # 5. Dynamax Capable?
        trs = [tr for tr in dt.contents if not isinstance(tr, NavigableString)]
        # trs[0] and trs[2] are just headers
        # trs[1] contains abilities
        # trs[3] contains 4 <td> with the rest
        
        # trs[1]
        # ability names are contained in <b> tags
        bs = [b.string for b in trs[1].find_all("b")]
        abilities = []
        if "Hidden Ability" in bs:
            bs.pop(-2)
            [abilities.append({'ability': b, 'hidden': False}) for b in bs]
            abilities[-1]['hidden'] = True
        else:
            [abilities.append({'ability': b, 'hidden': False}) for b in bs]
            
        # trs[3]
        tds = trs[3].find_all("td")
        # > tds[0] - Experience Growth
        if tds[0].contents[2] == 'Slow':
            exp_group = PkExpGroup['slow']
        elif tds[0].contents[2] == 'Medium Slow':
            exp_group = PkExpGroup['mediumslow']
        elif tds[0].contents[2] == 'Medium Fast':
            exp_group = PkExpGroup['mediumfast']
        elif tds[0].contents[2] == 'Fast':
            exp_group = PkExpGroup['fast']
        elif tds[0].contents[2] == 'Erratic':
            exp_group = PkExpGroup['erratic']
        elif tds[0].contents[2] == 'Fluctuating':
            exp_group = PkExpGroup['fluctuating']
        else:
            print('Failed to parse experience group \'%s\'' % tds[0].contents[2])
        # > tds[1] - Base Happiness
        base_happiness = int(tds[1].string) if tds[1].string is not None  else -1
        # > tds[2] - Effort Values Earned
        ev_yield = tds[2].contents[0][:-9] # remove " Point(s)" at the end of the string
        # > tds[3] - Dynamax Capable?
        can_dynamax = "can Dynamax" in tds[3].string
        
        return {
            'abilities': abilities,
            'exp_group': exp_group,
            'base_happiness': base_happiness,
            'ev_yield': ev_yield,
            'can_dynamax': can_dynamax
        }
    
    def processWeaknessesDexTable(self, dt):
        pass
    def processItemAndEggDexTable(self, dt):
        trs = [tr for tr in dt.contents if not isinstance(tr, NavigableString)]
        #trs[0] is a header
        #trs[1]
        tds = [td for td in trs[1].contents if not isinstance(td, NavigableString)]
        # > tds[0] - Hold Item
        # > tds[1] - Egg Groups
        # every other td in tds[1] will contain the name of an egg group
        egg_groups = [td.find("a").string for td in tds[1].find_all("td")[1::2]]
        egg_groups = [PkEggGroup[e.lower()] for e in egg_groups]
        
        return {
            'egg_groups': egg_groups
        }
    
    def processEvolutionDexTable(self, dt):
        pass
    def processLocationsDexTable(self, dt):
        pass
    def processDexTextDexTable(self, dt):
        trs = [tr for tr in dt.contents if not isinstance(tr, NavigableString)]
        #trs[0] is a header
        # the remaining trs will be Flavor text. One row per game
        tds = [[td.string for td in tr if td.string != '\n'] for tr in trs[1:]]
        games = [tr_td[0] for tr_td in tds]
        flavor = [tr_td[1] for tr_td in tds]
        return {
            'flavor_text': dict(zip(games, flavor))
        }
    
    def processLevelUpMovesDexTable(self, dt):
        (levels, moves) = self.processMovesDexTable(dt, True)
        
        return {
            'levels': levels,
            'moves': moves
        }
    
    def processTMMovesDexTable(self, dt):
        (tms, moves) = self.processMovesDexTable(dt, True)

        return {
            'tms': tms,
            'moves': moves
        }
    
    def processTRMovesDexTable(self, dt):
        (trs, moves) = self.processMovesDexTable(dt, True)

        return {
            'trs': trs,
            'moves': moves
        }
    
    def processEggMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, False)
    def processTutorMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, False)
    
    def processMaxMovesDexTable(self, dt):
        # print("TODO - processMaxMovesDexTable")
        pass
    def processStatsDexTable(self, dt):
        # TR# > Format:
        #   0 > |                                                Stats                                                |
        #     > |-----------------------------------------------------------------------------------------------------|
        #   1 > |                             |     HP    |    Atk    |    Def    |    SpA    |    SpD    |    Spd    |
        #     > |-----------------------------------------------------------------------------------------------------|
        #   2 > | Base Stats - Total: ###     |    ###    |    ###    |    ###    |    ###    |    ###    |    ###    |
        #     > |-----------------------------------------------------------------------------------------------------|
        #   3 > | Max Stats         | Lv. 50  | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #   4 > | Hindering Nature  | Lv. 100 | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #     > |-----------------------------------------------------------------------------------------------------|
        #   5 > | Max Stats         | Lv. 50  | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #   6 > | Neutral Nature    | Lv. 100 | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #     > |-----------------------------------------------------------------------------------------------------|
        #   7 > | Max Stats         | Lv. 50  | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #   8 > | Beneficial Nature | Lv. 100 | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### | ### - ### |
        #     > |-----------------------------------------------------------------------------------------------------|
        
        trs = dt.find_all("tr")
        
        if(not trs[0].find("h2") or trs[0].find("h2").string != 'Stats'):
            print("Error! This is not the Stats Dex Table")
            return False
            
        collected_strings = [[trs[r].find_all("td")[d].string \
                              for d in range(1, 7)] \
                             for r in range(2, 9)]
        base_stats         = [int(x) for x in collected_strings[0]]

        range_re = re.compile(r'^([0-9]{1,3}) - ([0-9]{1,3})$')

        max_stats_hind_100 = {'max': [], 'min': []}
        max_stats_neut_100 = {'max': [], 'min': []}
        max_stats_bene_100 = {'max': [], 'min': []}
        
        for str in collected_strings[2]:
            match = range_re.match(str)
            max_stats_hind_100['min'].append(int(match.group(1)))
            max_stats_hind_100['max'].append(int(match.group(2)))

        for str in collected_strings[4]:
            match = range_re.match(str)
            max_stats_neut_100['min'].append(int(match.group(1)))
            max_stats_neut_100['max'].append(int(match.group(2)))

        for str in collected_strings[6]:
            match = range_re.match(str)
            max_stats_bene_100['min'].append(int(match.group(1)))
            max_stats_bene_100['max'].append(int(match.group(2)))

        # max_stats_hind_50 = {'max': [], 'min': []}
        # max_stats_neut_50 = {'max': [], 'min': []}
        # max_stats_bene_50 = {'max': [], 'min': []}
        #
        # for str in collected_strings[1][1:]:
        #     match = range_re.match(str)
        #     max_stats_hind_50['min'].append(int(match.group(1)))
        #     max_stats_hind_50['max'].append(int(match.group(2)))
        #
        # for str in collected_strings[3][1:]:
        #     match = range_re.match(str)
        #     max_stats_neut_50['min'].append(int(match.group(1)))
        #     max_stats_neut_50['max'].append(int(match.group(2)))
        #
        # for str in collected_strings[5][1:]:
        #     match = range_re.match(str)
        #     max_stats_bene_50['min'].append(int(match.group(1)))
        #     max_stats_bene_50['max'].append(int(match.group(2)))

        return {
            'base_stats': base_stats,
            'max_stats': {
                'hindering': max_stats_hind_100,
                'neutral': max_stats_neut_100,
                'beneficial': max_stats_bene_100
            },
        }

    def processMovesDexTable(self, dt, table_has_label_column):
        trs = dt.find_all("tr")
        trs.pop(0) # trs[0] is the table header row
        trs.pop(0) # trs[0] (orig. trs[1]) is the columns header row
        # the remaining trs contain move data
        
        # For each move, the two rows are organized like this:
        #     Label | Attack Name | Type | Cat  |  Att.  | Acc. | PP | Effect % |
        # 0: "-"/## |     Link    | Link | Link | "-"/## | ###  | ## | "-"/##   |
        #    (Label)| (Atk. Name) |              Description                    |
        # 1:        |             |              Text                           |
        
        # for each tr
        moves = []
        if table_has_label_column:
            move_labels = []
            
        for r in range(0, len(trs), 2):
            move = Move()
            tds  = [td for td in trs[r].contents if not isinstance(td, NavigableString)]
            tds1 = [td for td in trs[r+1].contents if not isinstance(td, NavigableString)]
            if table_has_label_column:
                # Replace the hyphen in tds[0].string with 0 for level 0
                tds[0].string = tds[0].string.replace(b'\xe2\x80\x94'.decode('utf-8'), '0')
                offset = 1
                move_labels.append(tds[0].string)
            else:
                offset = 0

            name_td = tds[offset]
            type_td = tds[offset+1]
            cat_td  = tds[offset+2]
            dmg_td  = tds[offset+3]
            acc_td  = tds[offset+4]
            pp_td   = tds[offset+5]
            eff_td  = tds[offset+6]

            name = name_td.find("a").string
            type = os.path.split(type_td.find("img")['src'])[1][:-4]
            cat  = os.path.split(cat_td.find("img")['src'])[1][:-4]
            dmg  = int(dmg_td.string) if dmg_td.string != "--" and dmg_td.string != "??" else 0
            acc  = int(acc_td.string) if acc_td.string != "--" else 100
            pp   = int(pp_td.string) if pp_td.string != "--" else pp_td.string
            eff  = int(eff_td.string) if eff_td.string != "--" else 0
            move.initializeParameters(name, type, cat, dmg, acc, pp, eff, tds1[0].string)
            moves.append(move)

        if table_has_label_column:
            return (move_labels, moves)
        else:
            return moves
