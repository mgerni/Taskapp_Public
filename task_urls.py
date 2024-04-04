import tasklists

def get_wiki_url(new_task):
 return new_task['wikiLink']

easy_urls = list(map(get_wiki_url, tasklists.easy))
medium_urls = list(map(get_wiki_url, tasklists.medium))
hard_urls = list(map(get_wiki_url, tasklists.hard))
elite_urls = list(map(get_wiki_url, tasklists.elite))
extra_urls = list(map(get_wiki_url, tasklists.extra))
passive_urls = list(map(get_wiki_url, tasklists.passive))
boss_pet_urls = list(map(get_wiki_url, tasklists.boss_pets))
skilling_pet_urls = list(map(get_wiki_url, tasklists.skill_pets))
boss_pet_urls = list(map(get_wiki_url, tasklists.boss_pets))
other_pet_urls = list(map(get_wiki_url, tasklists.other_pets))
