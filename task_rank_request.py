import requests
import json
from tasklist import easy
import pymongo
import collection_log

mongo_uri = 'mongodb://localhost:27017/'
myclient = pymongo.MongoClient(mongo_uri)
mydb = myclient["TaskApp"]
coll = mydb["taskAccounts"]

response = requests.get("https://api.collectionlog.net/collectionlog/user/Gerni%20Task")
response_info = json.loads(response.text)
# response_info['collection_log']['tabs']['Minigames']['Gnome Restaurant']['items'][0]['obtained'] = False
# response_info['collection_log']['tabs']['Minigames']['Gnome Restaurant']['items'][1]['obtained'] = False
# response_info['collection_log']['tabs']['Minigames']['Gnome Restaurant']['items'][2]['obtained'] = False

# for k in response_info['collection_log']:
#     print(k)

user_data = coll.find_one({'username': 'Gerni'}, {'easyTasks': 1, '_id': 0})

task_check = []
missing_tasks = []
lms = False
valid = True
for index, ele in enumerate(user_data['easyTasks'], 1):
    if ele['status'] == 'Complete':
        print('Checking task: ' + str(index))
        if lms == False:
            if ele['taskname']['LMS'] == True:
                continue
        tasks = ele['taskname']
        for task in tasks:
            if task == 'Get bolt racks from Barrows':
                for item in response_info['collection_log']['tabs']['Bosses']['Barrows Chests']['items']:
                    if item['name'] == 'Bolt rack':
                        if item['obtained'] == True:
                            continue
                        else:
                            print('hit else')
                            valid = False
                            missing_tasks.append(task)
            if task == 'Get a Mole claw + skin':
                for item in response_info['collection_log']['tabs']['Bosses']['Giant Mole']['items']:
                    if item['name'] == 'Mole claw':
                        if item['obtained'] == True:
                            continue
                        else:
                            valid = False
                            missing_tasks.append(task)
                    if item['name'] == 'Mole skin':
                        if item['obtained'] == True:
                            continue
                        else:
                            valid = False
                            missing_tasks.append(task)
            if task == 'Get 1 Unique from Wintertodt':
                collection_log.Wintertodt['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Bosses']['Wintertodt']['items']:
                    exclude = {'Phoenix', 'Dragon axe'}
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.Wintertodt['log_count'] += 1
                            response_info['collection_log']['tabs']['Bosses']['Wintertodt']['items'].remove(item)
                            break
                if collection_log.Wintertodt['db_count'] != collection_log.Wintertodt['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 3 new uniques from beginner clues':
                collection_log.BeginnerClues['db_count'] += 3
                # print(response_info['collection_log']['tabs']['Clues']['Beginner Treasure Trails']['items'])
                for item in response_info['collection_log']['tabs']['Clues']['Beginner Treasure Trails']['items']:
                    exclude = {'Black pickaxe'}
                    
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.BeginnerClues['log_count'] += 1
                            response_info['collection_log']['tabs']['Clues']['Beginner Treasure Trails']['items'].remove(item)
                            if collection_log.BeginnerClues['log_count'] == collection_log.BeginnerClues['db_count']:
                                break
                            # print(len(response_info['collection_log']['tabs']['Clues']['Beginner Treasure Trails']['items']))
                            
                            
                if collection_log.BeginnerClues['db_count'] != collection_log.BeginnerClues['log_count']:
                    valid = False
                    missing_tasks.append(task)
                collection_log.BeginnerClues['log_count'] = 0
                collection_log.BeginnerClues['db_count'] = 0

            if task == 'Get 5 new uniques from easy clues':
                collection_log.EasyClues['db_count'] += 5
                for item in response_info['collection_log']['tabs']['Clues']['Easy Treasure Trails']['items']:
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.EasyClues['log_count'] += 1
                            response_info['collection_log']['tabs']['Clues']['Easy Treasure Trails']['items'].remove(item)
                            if collection_log.EasyClues['log_count'] == collection_log.EasyClues['db_count']:
                                break
                if collection_log.EasyClues['db_count'] != collection_log.EasyClues['log_count']:
                    valid = False
                    missing_tasks.append(task)
                collection_log.EasyClues['log_count'] = 0
                collection_log.EasyClues['db_count'] = 0

            if task == 'Get 5 new uniques from medium clues':
                collection_log.MediumClues['db_count'] += 5
                for item in response_info['collection_log']['tabs']['Clues']['Medium Treasure Trails']['items']:
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.MediumClues['log_count'] += 1
                            response_info['collection_log']['tabs']['Clues']['Medium Treasure Trails']['items'].remove(item)
                            if collection_log.MediumClues['log_count'] == collection_log.MediumClues['db_count']:
                                break
                if collection_log.MediumClues['db_count'] != collection_log.MediumClues['log_count']:
                    valid = False
                    missing_tasks.append(task)
                collection_log.MediumClues['log_count'] = 0
                collection_log.MediumClues['db_count'] = 0

            if task == 'Get 5 new uniques from hard clues':
                collection_log.HardClues['db_count'] += 5
                for item in response_info['collection_log']['tabs']['Clues']['Hard Treasure Trails']['items']:
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.HardClues['log_count'] += 1
                            response_info['collection_log']['tabs']['Clues']['Hard Treasure Trails']['items'].remove(item)
                            if collection_log.HardClues['log_count'] == collection_log.HardClues['db_count']:
                                break
                if collection_log.HardClues['db_count'] != collection_log.HardClues['log_count']:
                    valid = False
                    missing_tasks.append(task)
                collection_log.HardClues['log_count'] = 0
                collection_log.HardClues['db_count'] = 0

            if task == 'Get Runner boots':
                for item in response_info['collection_log']['tabs']['Minigames']['Barbarian Assault']['items']:
                    if item['name'] == 'Runner Boots':
                        if item['obtained'] == True:
                            continue
                        else:
                            valid = False
                            missing_tasks.append(task)
            if task == 'Get Penance gloves':
                for item in response_info['collection_log']['tabs']['Minigames']['Barbarian Assault']['items']:
                    if item['name'] == 'Penance gloves':
                        if item['obtained'] == True:
                            continue
                        else:
                            valid = False
                            missing_tasks.append(task)

            if task == 'Get a Granite body':
                for item in response_info['collection_log']['tabs']['Minigames']['Barbarian Assault']['items']:
                    if item['name'] == 'Granite body':
                        if item['obtained'] == True:
                            continue
                        else:
                            valid = False
                            missing_tasks.append(task)
            if task == 'Get 1 new halo':
                halo_1 = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][36]
                halo_2 = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][37]
                halo_3 = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][38]
                if halo_1['obtained'] == True or halo_2['obtained'] == True or halo_3['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the full Red decorative set':
                for ele in range(0,8):
                    item = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][ele]
                    if item['obtained'] == True:
                        continue
                    else:
                        valid = False
                        missing_tasks.append(task)

            if task == 'Get the Zamorak hood & cloak':
                sara_hood = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][24]
                sara_cloak = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][25]

                if sara_hood['obtained'] == True and sara_cloak['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the Saradomin hood & cloak':
                zam_hood = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][26]
                zam_cloak = response_info['collection_log']['tabs']['Minigames']['Castle Wars']['items'][27]

                if zam_hood['obtained'] == True and zam_cloak['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 Angler piece':
                collection_log.FishingTrawler['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Fishing Trawler']['items']:
                    if item['obtained'] ==  True:
                        collection_log.FishingTrawler['log_count'] += 1
                        response_info['collection_log']['tabs']['Minigames']['Fishing Trawler']['items'].remove(item)
                        break
                if collection_log.FishingTrawler['db_count'] != collection_log.FishingTrawler['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 new unique from Gnome Restaurant':
                collection_log.GnomeRestaurant['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Gnome Restaurant']['items']:
                    if item['obtained'] ==  True:
                        collection_log.GnomeRestaurant['log_count'] += 1
                        response_info['collection_log']['tabs']['Minigames']['Gnome Restaurant']['items'].remove(item)
                        break
                if collection_log.GnomeRestaurant['db_count'] != collection_log.GnomeRestaurant['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Beginner wand':
                wand = response_info['collection_log']['tabs']['Minigames']['Magic Training Arena']['items'][0]
                if wand['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Unlock bones to peaches':
                b2p = response_info['collection_log']['tabs']['Minigames']['Magic Training Arena']['items'][10]
                if b2p['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)
            if task == 'Get Infinity boots':
                boots = response_info['collection_log']['tabs']['Minigames']['Magic Training Arena']['items'][7]
                if boots['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)
            if task == 'Get Infinity gloves':
                gloves = response_info['collection_log']['tabs']['Minigames']['Magic Training Arena']['items'][8]
                if gloves['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Void Knight seal':
                seal = response_info['collection_log']['tabs']['Minigames']['Pest Control']['items'][7]
                if seal['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)
            if task == 'Get Void Knight gloves':
                gloves = response_info['collection_log']['tabs']['Minigames']['Pest Control']['items'][7]
                if gloves['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)
            if task == 'Get a Void Knight mace':
                mace = response_info['collection_log']['tabs']['Minigames']['Pest Control']['items'][7]
                if mace['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 piece of Rogue equipment':
                collection_log.RoguesDen['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Rogues\' Den']['items']:
                    if item['obtained'] ==  True:
                        collection_log.RoguesDen['log_count'] += 1
                        response_info['collection_log']['tabs']['Minigames']['Rogues\' Den']['items'].remove(item)
                        break
                if collection_log.RoguesDen['db_count'] != collection_log.RoguesDen['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique from Shades of Mort\'ton':
                collection_log.ShadesofMorton['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Shades of Mort\'ton']['items']:
                    if item['obtained'] ==  True:
                        collection_log.ShadesofMorton['log_count'] += 1
                        response_info['collection_log']['tabs']['Minigames']['Shades of Mort\'ton']['items'].remove(item)
                        break
                if collection_log.ShadesofMorton['db_count'] != collection_log.ShadesofMorton['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 piece of Lumberjack equipment':
                collection_log.TempleTrekking['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Temple Trekking']['items']:
                    if item['obtained'] ==  True:
                        collection_log.TempleTrekking['log_count'] += 1
                        response_info['collection_log']['tabs']['Minigames']['Temple Trekking']['items'].remove(item)
                        break
                if collection_log.TempleTrekking['db_count'] != collection_log.TempleTrekking['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the Gricoller\'s can':
                can = response_info['collection_log']['tabs']['Minigames']['Tithe Farm']['items'][5]
                if can['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 piece of Farmer\'s equipment':
                collection_log.TitheFarm['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Minigames']['Tithe Farm']['items']:
                    exclude = ['Gricoller\'s can', 'Seed box', 'Herb sack']
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.TitheFarm['log_count'] += 1
                            response_info['collection_log']['tabs']['Minigames']['Tithe Farm']['items'].remove(item)
                            break
                if collection_log.TitheFarm['db_count'] != collection_log.TitheFarm['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Blue Rum':
                bluerum = response_info['collection_log']['tabs']['Minigames']['Trouble Brewing']['items'][29]
                if bluerum['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Red Rum':
                redrum = response_info['collection_log']['tabs']['Minigames']['Trouble Brewing']['items'][28]
                if redrum['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get The stuff':
                stuff = response_info['collection_log']['tabs']['Minigames']['Trouble Brewing']['items'][27]
                if stuff['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the Pearl fishing rod':
                rod = response_info['collection_log']['tabs']['Other']['Aerial Fishing']['items'][1]
                if rod['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique Champion scroll':
                collection_log.ChampScroll['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Champion\'s Challenge']['items']:
                    exclude = ['Champion\'s cape',]
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.ChampScroll['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Champion\'s Challenge']['items'].remove(item)
                            break
                if collection_log.ChampScroll['db_count'] != collection_log.ChampScroll['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the Marksman headpiece':
                hat = response_info['collection_log']['tabs']['Other']['Chompy Bird Hunting']['items'][6]
                if hat['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get a Tea flask':
                tea = response_info['collection_log']['tabs']['Other']['Creature Creation']['items'][0]
                if tea['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get a Rune satchel':
                rune = response_info['collection_log']['tabs']['Other']['Creature Creation']['items'][6]
                if rune['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Green satchel':
                green = response_info['collection_log']['tabs']['Other']['Creature Creation']['items'][2]
                if green['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Red satchel':
                red = response_info['collection_log']['tabs']['Other']['Creature Creation']['items'][3]
                if red['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get a Black satchel':
                black = response_info['collection_log']['tabs']['Other']['Creature Creation']['items'][4]
                if black['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get a Rune defender':
                defender = response_info['collection_log']['tabs']['Other']['Cyclopes']['items'][6]
                if defender['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 2 unique notes from Fossil Island':
                collection_log.FossilIslandNotes['db_count'] += 2
                for item in response_info['collection_log']['tabs']['Other']['Fossil Island Notes']['items']:
                    if item['obtained'] ==  True:
                        collection_log.FossilIslandNotes['log_count'] += 1
                        response_info['collection_log']['tabs']['Other']['Fossil Island Notes']['items'].remove(item)

                        if collection_log.FossilIslandNotes['log_count'] == collection_log.FossilIslandNotes['db_count']:
                            break
                if collection_log.FossilIslandNotes['db_count'] != collection_log.FossilIslandNotes['log_count']:
                    valid = False
                    missing_tasks.append(task)
                    collection_log.FossilIslandNotes['db_count'] = 0
                    collection_log.FossilIslandNotes['log_count'] = 0


            if task == 'Get 1 piece of Prospector equipment':
                collection_log.MotherlodeMine['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Motherlode Mine']['items']:
                    exclude = {'Coal bag', 'Gem bag'}
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.MotherlodeMine['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Motherlode Mine']['items'].remove(item)
                            break
                if collection_log.MotherlodeMine['db_count'] != collection_log.MotherlodeMine['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Revenant ether':
                ether = response_info['collection_log']['tabs']['Other']['Revenants']['items'][13]
                if ether['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 piece of Graceful equipment':
                collection_log.RooftopAgility['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Rooftop Agility']['items']:
                    exclude = {'Coal bag', 'Gem bag'}
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.RooftopAgility['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Rooftop Agility']['items'].remove(item)
                            break
                if collection_log.RooftopAgility['db_count'] != collection_log.RooftopAgility['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Crawling hand':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Crawling hand'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Cockatrice head':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Cockatrice head'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get 1 unique from Mogres':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Flippers', 'Mudskipper hat'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Brine sabre':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Brine sabre'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique from Turoths':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic robe bottom (light)', 'Leaf-bladed sword'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Black mask':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Black mask (10)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get the next tier of metal boots':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Bronze boots', 'Iron boots', 'Steel boots', 'Black boots', 'Mithril boots'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Mystic hat (light)':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic hat (light)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Mystic gloves (light)':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic gloves (light)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Mystic boots (light)':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic boots (light)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique from Infernal Mages':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic hat (dark)', 'Mystic boots (dark)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get Mystic gloves (dark)':
                collection_log.SlayerItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Slayer']['items']:
                    include = {'Mystic gloves (dark)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.SlayerItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Slayer']['items'].remove(item)
                            break
                if collection_log.SlayerItems['db_count'] != collection_log.SlayerItems['log_count']:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get 1 unique Tzhaar drop':
                collection_log.TzhaarItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['TzHaar']['items']:
                    exclude = {'Obsidian helmet', 'Obsidian platebody', 'Obsidian platelegs', 'Toktz-mej-tal'}
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.TzhaarItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['TzHaar']['items'].remove(item)
                            break
                if collection_log.TzhaarItems['db_count'] != collection_log.TzhaarItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Big swordfish':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Big swordfish'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)
                    
            if task == 'Get a Big bass':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Big bass'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Long bone':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Long bone'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get an Ecumenical key':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Ecumenical key'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get 1 unique Dark totem piece / Ancient shard':
                collection_log.MiscItems['db_count'] += 1

                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Dark totem top', 'Dark totem middle', 'Dark totem base'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    for item in response_info['collection_log']['tabs']['Bosses']['Skotizo']['items']:
                        include = {'Ancient shard'}
                        if item['name'] in include:
                            if item['obtained'] ==  True:
                                collection_log.MiscItems['log_count'] += 1
                                response_info['collection_log']['tabs']['Bosses']['Skotizo']['items'].remove(item)
                                break
                    if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                        valid = False
                        missing_tasks.append(task)

            if task == 'Get Mining gloves':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Mining gloves'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Right skull half':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Right skull half'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Left skull half':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Left skull half'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Top of sceptre':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Top of sceptre'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Bottom of sceptre':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Bottom of sceptre'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Mossy key':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Mossy key'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Giant key':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Giant key'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Fresh crab claw & Fresh crab shell':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Fresh crab claw', 'Fresh crab shell'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get a Xeric\'s talisman (inert)':
                collection_log.MiscItems['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Other']['Miscellaneous']['items']:
                    include = {'Xeric\'s talisman (inert)'}
                    if item['name'] in include:
                        if item['obtained'] ==  True:
                            collection_log.MiscItems['log_count'] += 1
                            response_info['collection_log']['tabs']['Other']['Miscellaneous']['items'].remove(item)
                            break
                if collection_log.MiscItems['db_count'] != collection_log.MiscItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if 'Diary' in task:
                missing_tasks.append(task)


            if task == 'Get a Supply crate from Mahogany Homes':
                crate = response_info['collection_log']['tabs']['Minigames']['Mahogany Homes']['items'][0]
                if crate['obtained'] == True:
                    continue
                else:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique from Tempoross':
                collection_log.Tempoross['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Bosses']['Tempoross']['items']:
                    exclude = {'Tiny tempor', 'Dragon harpoon'}
                    if item['name'] not in exclude:
                        if item['obtained'] ==  True:
                            collection_log.Tempoross['log_count'] += 1
                            response_info['collection_log']['tabs']['Bosses']['Tempoross']['items'].remove(item)
                            break
                if collection_log.Tempoross['db_count'] != collection_log.Tempoross['log_count']:
                    valid = False
                    missing_tasks.append(task)
            
            if task == 'Get 5 unique items at Camdozaal':
                collection_log.CamdozaalItems['db_count'] += 5
                for i in range(collection_log.CamdozaalItems['db_count'] - 5, collection_log.CamdozaalItems['db_count']):
                    item = response_info['collection_log']['tabs']['Other']['Camdozaal']['items'][i]
                    if item['obtained'] ==  True:
                        collection_log.CamdozaalItems['log_count'] += 1
                if collection_log.CamdozaalItems['db_count'] != collection_log.CamdozaalItems['log_count']:
                    valid = False
                    missing_tasks.append(task)

            if task == 'Get 1 unique from Guardians of the Rift':
                collection_log.GotR['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Miningames']['Guardians of the Rift']['items']:
                    include = {'Abyssal protector'}
                    if item['name'] not in include:
                        if item['obtained'] ==  True:
                            collection_log.GotR['log_count'] += 1
                            response_info['collection_log']['tabs']['Miningames']['Guardians of the Rift']['items'].remove(item)
                            break
                            
                if collection_log.GotR['db_count'] != collection_log.GotR['log_count']:
                    valid = False
                    missing_tasks.append(task)


            if task == 'Get 1 unique from Giants\' Foundry':
                collection_log.GiantsFoundy['db_count'] += 1
                for item in response_info['collection_log']['tabs']['Miningames']['Giants\' Foundry']['items']:
                    if item['obtained'] ==  True:
                        collection_log.GiantsFoundy['log_count'] += 1
                        response_info['collection_log']['tabs']['Miningames']['Giants\' Foundry']['items'].remove(item)
                        break
                if collection_log.GiantsFoundy['db_count'] != collection_log.GiantsFoundy['log_count']:
                    valid = False
                    missing_tasks.append(task)
print(valid, missing_tasks)
print(len(user_data['easyTasks']))


