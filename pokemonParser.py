from bs4 import BeautifulSoup
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
        self.processDetailedInfoDexTable(dextables[2])
        self.processWeaknessesDexTable(dextables  [3])
        self.processItemAndEggDexTable(dextables  [4])
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
        self.pokemon.base_stats = stats_struct.base_stats 

    def processPictureDexTable(self, dt):
        pass
    def processGeneralInfoDexTable(self, dt):
        trs = dt.find_all("tr")
        # tr[0] and tr[2] are just headers
        # tr[1] and tr[3] each contain 5 <td>
        # tr[1]
        tds = tr[1].find_all("td")
        # > td[0] - Name
        name = tds[0].string.lower()
        # > td[1] - Other names
        # > td[2] - Pokedex Number
        # use find to only get first tr, don't want region dex
        national_dex_number = int(tds[2].find("tr").find_all("td")[1].string[1:])
        # > td[3] - Gender Ratio
        # the first td in each tr contains "Male" or "Female"
        # the second td in each tr contains the actual percentage
        gender_percents = [tr.find_all("td")[1].string for tr in  tds[3].find_all("tr")]
        # remove "%" at the end of the strings
        gender_percents = [float(p_string[:-1]) for p_string in gender_percents]
        # > td[4] - Types
        types_links = tds[4].find_all("a")
        types = [re.match('^.*\/([a-z]+)\.shmtl$', link.href).group(0) for link in types_links]
        types = [PkType[t] for t in types]
        # tr[3]
        tds = tr[3].find_all("td")
        # > tds[0] - Classification
        classification = tds[0].string[:-8]
        # > tds[1] - Height
        height = tds[1] # TODO - this is either .string or something else because of the <br>
        # > tds[2] - Weight
        weight = tds[2] # TODO - this is either .string or something else because of the <br>
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
        pass
    def processWeaknessesDexTable(self, dt):
        pass
    def processItemAndEggDexTable(self, dt):
        pass
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
