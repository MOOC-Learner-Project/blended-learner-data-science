from utilities import *

def get_durations(data, session_threshold=TWO_HOURS):
    durations = []

    for u in data:
        for i in range(u.time.count() - 1):
            # For some reason, despite the timezones already being in UTC, they have to be converted
            # again. Not sure if a bug or something is modifying them between assignment and here
            time_diff = (u.time.iloc[i+1].tz_convert('UTC') - u.time.iloc[i].tz_convert('UTC')).total_seconds()
            if time_diff > session_threshold: time_diff = 0
            
            durations.append((u.display_name.iloc[i], u.display_name.iloc[i+1], time_diff))

    return pd.DataFrame(durations, columns=['from', 'to', 'duration'])

def get_transition_duration_sums(d_df, keep_reloads=False):
    transitions = d_df.groupby(['from', 'to'])
    sums = transitions.duration.sum().reset_index()
    
    return result_of_keep_reloads(keep_reloads, sums)


def get_transition_duration_avgs(d_df, keep_reloads=False):
    transitions = d_df.groupby(['from', 'to'])
    avgs = transitions.duration.mean().to_frame(name='duration average').reset_index()

    return result_of_keep_reloads(keep_reloads, avgs)


def get_transition_duration_medians(d_df, keep_reloads=False):
    transitions = d_df.groupby(['from', 'to'])
    avgs = transitions.duration.median().to_frame(name='duration average').reset_index()
    
    return result_of_keep_reloads(keep_reloads, avgs)


def get_resource_duration_sums(d_df):
    all_resource_time = d_df.groupby(['from'])
    
    return all_resource_time.duration.sum().sort_values(ascending=False)


def get_resource_duration_avgs(d_df):
    all_resource_time = d_df.groupby(['from'])
    return all_resource_time.duration.mean().sort_values(ascending=False)


def result_of_keep_reloads(keep_reloads, transitions):
    if keep_reloads: return transitions
    
    if len(transitions): return transitions[transitions['from'] != transitions['to']]
    
    else: return transitions