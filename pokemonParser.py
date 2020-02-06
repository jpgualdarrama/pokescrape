from bs4 import BeautifulSoup
from bs4.element import *
from pokemon import *
import re

class PokemonParser():
    def __init__(self, handle):
        self.pokemon = Pokemon()

        self.soup = BeautifulSoup(handle, features="html.parser")
        
        self.in_dextable = False

    def parse(self):
        dextables = self.soup.find_all("table", class_="dextable")

        self.processPictureDexTable(dextables     [0])
        general_info = self.processGeneralInfoDexTable(dextables [1])
        detail_info = self.processDetailedInfoDexTable(dextables[2])
        self.processWeaknessesDexTable(dextables  [3])
        item_and_egg_info = self.processItemAndEggDexTable(dextables  [4])
        self.processEvolutionDexTable(dextables   [5])
        self.processLocationsDexTable(dextables   [6])
        self.processDexTextDexTable(dextables     [7])
        self.processLevelUpMovesDexTable(dextables[8])
        self.processTMMovesDexTable(dextables     [9])
        self.processTRMovesDexTable(dextables     [10])
        self.processEggMovesDexTable(dextables    [11])
        self.processTutorMovesDexTable(dextables  [12])
        self.processMaxMovesDexTable(dextables    [13])
        stats_struct = self.processStatsDexTable(dextables       [14])

        self.pokemon.name = general_info.name
        self.pokemon.national_dex_number = general_info.number
        self.pokemon.gender_threshold = general_info.gender_percents
        self.pokemon.types = general_info.types
        self.pokemon.species = general_info.classification
        self.pokemon.height = general_info.height
        self.pokemon.weight = general_info.weight
        self.pokemon.catch_rate = general_info.capture_rate
        self.pokemon.hatch_counter = general_info.egg_steps
        
        self.pokemon.abilities = detail_info.abilities
        self.pokemon.exp_group = detail_info.exp_group
        self.pokemon.base_friendship = detail_info.base_happiness
        self.pokemon.ev_yield = detail_info.ev_yield
        self.pokemon.can_dynamax = detail_info.can_dynamax
        
        self.pokemon.egg_groups = item_and_egg_info.egg_groups
        
        self.pokemon.base_stats = stats_struct.base_stats 

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
            bs = (bs[0:-3], bs[-1])
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
        base_happiness = int(tds[1].string) if tds[1].string != '' else -1
        # > tds[2] - Effort Values Earned
        ev_yield = tds[2].contents[0][:-9] # remove " Point(s)" at the end of the string
        # > tds[3] - Dynamax Capable?
        can_dynamax = True if "can Dynamax" in tds[3].string else False
        
        return {
            'abilities: abilities,
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
        egg_groups = [pkEggGroup[e] for e in egg_groups]
        
        return {
            'egg_groups': egg_groups
        }
    
    def processEvolutionDexTable(self, dt):
        pass
    def processLocationsDexTable(self, dt):
        pass
    def processDexTextDexTable(self, dt):
        pass
    
    def processLevelUpMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, 'level', True)
    def processTMMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, 'tm', True)
    def processTRMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, 'tr', True)
    def processEggMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, 'egg', False)
    def processTutorMovesDexTable(self, dt):
        return self.processMovesDexTable(dt, 'tutor', False)
    
    def processMaxMovesDexTable(self, dt):
        print("TODO - processMaxMovesDexTable")
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

    def processMovesDexTable(self, dextable, struct_label, table_has_label_column):
        # - 2 for the fooevo row and the "header" row
        # / 2 because each move has two table rows
        num_moves = (len(dt.find_all("tr")) - 2) / 2
        pass
