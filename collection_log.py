# taskname - tasks name
# category - category within the clog
# logName - name of log inside given category
# include - logslots to include from that log when checking
# exclude - logslots to ex from that log when checking
# count - 12 occurances on seemingly clue / ancient pages tasks?
# db_count - seems to be how many logs user needs to have given above criteria
# log_count - always 0, can be discarded


import tasklists
def get_log_slots_or_none(new_task):
    if 'colLogData' not in new_task:
        return None
    col_log = new_task['colLogData']
    old_col_log = {'taskName': new_task['name'], 'category': col_log['category'], 'logName': col_log['logName'] }
    if 'include' in col_log:
        old_col_log['include'] = set(col_log['include'])
    if 'exclude' in col_log:
        old_col_log['exclude'] = set(col_log['exclude'])
    if 'count' in col_log:
        old_col_log['count'] = col_log['count']
    old_col_log['db_count'] = col_log['logCount']
    old_col_log['log_count'] = 0
    return old_col_log

def convert_list(t_list):
    return list(filter(lambda a: a is not None, list(map(get_log_slots_or_none, t_list))))


easy_log_slots = convert_list(tasklists.easy)
medium_log_slots = convert_list(tasklists.medium)
hard_log_slots = convert_list(tasklists.hard)
