import pdb
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

    def dtMatches(self, dt, comp_str, contents_lengths, index_type_pairs, last_index):
        # args[0]  -> [(index, type), (index, type)]
        # args[1]  -> len
        ret_val = len(dt.contents) > contents_lengths[0]
        if len(index_type_pairs) > 0:
            (index, typ) = index_type_pairs[0]
            ret_val = ret_val and isinstance(dt.contents[index], typ)
            if ret_val:
                if len(index_type_pairs) > 1:
                    ret_val = ret_val and \
                              self.dtMatches(dt.contents[index], comp_str, \
                                             contents_lengths[1:], 
                                             index_type_pairs[1:], last_index)
                    pass
                else:
                    if len(dt.contents) > index and len(dt.contents[index].contents) > last_index and \
                       isinstance(dt.contents[index].contents[last_index].string, NavigableString):
                        ret_val = ret_val and dt.contents[index].contents[last_index].string.lower() == comp_str.lower()
                    else:
                        ret_val = False
                pass
            pass
        
        return ret_val

    def parse(self, name):
        dextables = self.soup.find_all("table", class_="dextable")

        general_info = None
        detail_info = None
        item_and_egg_info = None
        flavor_text_info = None
        levelup_info = None
        tm_info = None
        tr_info = None
        eggmoves_info = None
        tutor_info = None
        stats_info = None

        num_dt = len(dextables)

        for i in range(0, num_dt):
            dt = dextables[i]
            # Eternatus is strange, because it has a second set of tables
            # on the same webpage for Eternamax Eternatus. Use this check
            # to ignore those
            if self.dtMatches(dt, "Eternamax Eternatus", [1], [(1, Tag)], 0):
                return
            elif self.dtMatches(dt, "Picture", [1], [(1, Tag)], 1):
                self.processPictureDexTable(dt)
            elif self.dtMatches(dt, "Name", [1], [(1, Tag)], 1):
                general_info = self.processGeneralInfoDexTable(dt)
            elif self.dtMatches(dt, "Abilities", [1, 1], [(1, Tag), (1, Tag)], 0):
                detail_info = self.processDetailedInfoDexTable(dt)
            elif self.dtMatches(dt, "Weakness", [1, 1], [(1, Tag), (1, Tag)], 1):
                self.processWeaknessesDexTable(dt)
            elif self.dtMatches(dt, "Wild Hold Item", [1], [(1, Tag)], 1):
                item_and_egg_info = self.processItemAndEggDexTable(dt)
            elif self.dtMatches(dt, "Evolutionary Chain", [1], [(1, Tag)], 1):
                self.processEvolutionDexTable(dt)
            elif self.dtMatches(dt, "Locations", [1], [(1, Tag)], 1) or \
                 self.dtMatches(dt, "Locations", [1, 1], [(1, Tag), (1, Tag)], 0):
                self.processLocationsDexTable(dt)
            elif self.dtMatches(dt, "Flavor Text", [1], [(1, Tag)], 1):
                flavor_text_info = self.processDexTextDexTable(dt, name)
            elif self.dtMatches(dt, "Gender Differences", [1], [(1, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Alternate Forms", [1], [(1, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Standard Level Up", [0, 0, 0], [(0, Tag), (0, Tag), (0, Tag)], 1):
                levelup_info = self.processLevelUpMovesDexTable(dt)
            elif self.dtMatches(dt, "Alola Form Level Up", [0, 0, 0], [(0, Tag), (0, Tag), (0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Galarian Form Level Up", [0, 0, 0], [(0, Tag), (0, Tag), (0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Level Up - Male", [0, 0, 0], [(0, Tag), (0, Tag), (0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Level Up - Female", [0, 0], [(0, Tag), (0, Tag)], 0):
                pass
            elif self.dtMatches(dt, "Level Up - Low Key Form", [0], [(0, Tag)], 0):
                pass
            elif self.dtMatches(dt, "Technical Machine Attacks", [0, 0], [(0, Tag), (0, Tag)], 1):
                tm_info = self.processTMMovesDexTable(dt)
            elif self.dtMatches(dt, "Technical Record Attacks", [0, 0], [(0, Tag), (0, Tag)], 1):
                tr_info = self.processTRMovesDexTable(dt)
            elif self.dtMatches(dt, "Egg Moves", [0, 0], [(0, Tag), (0, Tag)], 1):
                eggmoves_info = self.processEggMovesDexTable(dt)
            elif self.dtMatches(dt, "Move Tutor Attacks", [0, 0], [(0, Tag), (0, Tag)], 0):
                tutor_info = self.processTutorMovesDexTable(dt)
            elif self.dtMatches(dt, "Usable Max Moves", [0, 0], [(0, Tag), (0, Tag)], 0):
                self.processMaxMovesDexTable(dt)
            elif self.dtMatches(dt, "Transfer Only Moves", [0], [(0, Tag)], 0): # collapsed
                pass
            elif self.dtMatches(dt, "Transfer Only Moves ", [0, 0], [(0, Tag), (0, Tag)], 0): # expanded
                pass
            elif self.dtMatches(dt, "Stats", [0], [(0, Tag)], 1):
                stats_info = self.processStatsDexTable(dt)
            elif self.dtMatches(dt, "Stats - Alolan " + name, [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Galarian " + name, [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Alternate Forms", [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - School Form", [0, 1], [(0, Tag), (1, Tag)], 0):
                pass
            elif self.dtMatches(dt, "Stats - Dusk Mane " + name, [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Dawn Wings " + name, [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - NoIce Form", [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Female", [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Crowned Sword", [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Stats - Crowned Shield", [0], [(0, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Eternamax " + name, [1], [(1, Tag)], 0):
                pass
            elif self.dtMatches(dt, "Pre-Evolution Only Moves", [0], [(0, Tag)], 0):
                pass
            elif self.dtMatches(dt, "Gigantamax " + name, [1], [(1, Tag)], 1):
                pass
            elif self.dtMatches(dt, "Special Moves", [0, 0], [(0, Tag), (0, Tag)], 0):
                pass
            else:
                print("ERROR: Unable to find match for dextables[%i] for %s" % (i, name.capitalize()))
                pdb.set_trace()
            pass

        if general_info is not None:
            self.pokemon.name = general_info['name']
            self.pokemon.national_dex_number = general_info['number']
            self.pokemon.gender_threshold = general_info['gender_percents']
            self.pokemon.types = general_info['types']
            self.pokemon.species = general_info['classification']
            self.pokemon.height = general_info['height']
            self.pokemon.weight = general_info['weight']
            self.pokemon.catch_rate = general_info['capture_rate']
            self.pokemon.hatch_counter = general_info['egg_steps']
        if detail_info is not None:
            self.pokemon.abilities = detail_info['abilities']
            self.pokemon.exp_group = detail_info['exp_group']
            self.pokemon.base_friendship = detail_info['base_happiness']
            self.pokemon.ev_yield = detail_info['ev_yield']
            self.pokemon.can_dynamax = detail_info['can_dynamax']
        if item_and_egg_info is not None:
            self.pokemon.egg_groups = item_and_egg_info['egg_groups']
        if flavor_text_info is not None:
            self.pokemon.pokedex = flavor_text_info['flavor_text']
        if stats_info is not None:
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
        if tds[0].string is not None:
            classification = tds[0].string[:-8]
        else:
            classification = tds[0].contents[0].string
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
        # some pokemon have more than one capture rate, if their capture
        # rate differs in different games.
        # TODO: Handle multiple capture rates. For now, just take the first one
        if tds[3].string is None:
            capture_rate = int(tds[3].contents[0].string)
        else:        
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
    def processDexTextDexTable(self, dt, name):
        trs = [tr for tr in dt.contents if not isinstance(tr, NavigableString)]
        #trs[0] is a header
        trs.pop(0)

        # the flavor text dextable can be in one of two formats:
        # if the species has more than one form with different flavor text:
        # | row | picture | game |          flavor text          |
        # |-----|---------|------|-------------------------------|
        # |  0  |   P     |  g1  | text text text                |
        # |-----|         |------|-------------------------------|
        # | ... |    I    | .... | ...                           |
        # |-----|         |------|-------------------------------|
        # |  N  |     C   |g(N+1)| text text text                |
        # |-----|---------|------|-------------------------------|
        # otherwise:
        # | row | game |          flavor text          |
        # |-----|------|-------------------------------|
        # |  0  |  g1  | text text text                |
        # |-----|------|-------------------------------|
        # | ... | .... | ...                           |
        # |-----|------|-------------------------------|
        # |  N  |g(N+1)| text text text                |
        # |-----|------|-------------------------------|

        # check the number of td's in trs[0] to see if there are 2 or 3
        row_0_tds = [td for td in trs[0].contents if not isinstance(td, NavigableString)]

        if len(row_0_tds) == 3:
            # every third row
            struct = {}
            names = []
            for i in range(0, len(trs), 3):
                name = os.path.split(trs[i].contents[0].contents[0]['src'])[1][:-4]
                struct[name] = {}
                struct[name][trs[i].contents[1].string] = trs[i].contents[2].string
                struct[name][trs[i+1].string] = trs[i+2].string
            
            return {
                'flavor_text': struct
            }
            
        elif len(row_0_tds) == 2:
            tds = [[td.string for td in tr.contents if not isinstance(td, NavigableString)] for tr in trs]
            games = [tr_td[0] for tr_td in tds]
            flavor = [tr_td[1] for tr_td in tds]
            struct = {}
            struct[name] = dict(zip(games, flavor))
            return {
                'flavor_text': struct
            }
        else:
            print("ERROR - Unable to process flavor text dex table of %s!" % name)
            return {'flavor_text': {}}
        
    
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
        if dt.contents[0].name == 'thead':
            dt = dt.contents[0]
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
        # trs = dt.find_all("tr")
        
        trs = [tr for tr in dt.contents if tr.name == 'tr']
        trs.pop(0) # trs[0] is the table header row
        trs.pop(0) # trs[0] (orig. trs[1]) is the columns header row
        # the remaining trs contain move data
        
        # For each move, the two rows are organized like this:
        #     Label | Attack Name | Type | Cat  |  Att.  | Acc. | PP | Effect % | [ Form ] |
        # 0: "-"/## |     Link    | Link | Link | "-"/## | ###  | ## | "-"/##   | [F1 |F2] |
        #    (Label)| (Atk. Name) |              Description                    | [(Form)] |
        # 1:        |             |              Text                           | [F1  F2] |
        
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

            # if the table contains a Form column
            if len(tds) > offset+7:
                form_td = tds[offset+7]
                form_imgs = form_td.find_all("img")
                forms = [img['alt'].lower().replace(" ","_") for img in form_imgs]

            name = name_td.find("a").string
            type = os.path.split(type_td.find("img")['src'])[1][:-4]
            cat  = os.path.split(cat_td.find("img")['src'])[1][:-4]
            dmg  = int(dmg_td.string) if dmg_td.string != "--" and dmg_td.string != "??" else 0
            acc  = int(acc_td.string) if acc_td.string != "--" else 100
            pp   = int(pp_td.string) if pp_td.string != "--" else pp_td.string
            eff  = int(eff_td.string) if eff_td.string != "--" else 0
            move.initializeParameters(name, type, cat, dmg, acc, pp, eff, tds1[0].string)
            moves.append(move)

        # TODO: Return forms
        if table_has_label_column:
            return (move_labels, moves)
        else:
            return moves
