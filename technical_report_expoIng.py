# %% Preprocessing
# Load data
import tools as tl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import os
import seaborn as sns
import benchmark_func as bf

sns.set(context="paper", font_scale=1.8, palette="husl", style="ticks",
        rc={'text.usetex': True, 'font.family': 'serif', 'font.size': 15,
            "xtick.major.top": False, "ytick.major.right": False})

is_saving = True
show_plots = True
saving_format = 'svg'
results_file_name = 'batch_5'

plt.rcParams.update({'figure.max_open_warning': 0})
plt.close('all')
# List of combinations listed in the manuscript
batch_1 = ['Small_pop30', 'unfolded_hhs_pop30']
batch_2 = ['Small_pop30', 'Medium', 'Big', 'Deep']
batch_3 = ['LSTM_variable_length', 'LSTM_max_fixed_length', 'LSTM_30_fixed_length']
batch_4 = ['Small_pop30', 'Small_pop50', 'unfolded_hhs_pop30', 'unfolded_hhs_pop50']
batch_5 = ['Small_pop30', 'Deep', 'LSTM_30_fixed_length', 'Small_pop50'] # TBD

# All experiments
# consider_experiments = list(collection_experiments.keys())

# Indicates which experiments
consider_experiments = batch_5
 


chosen_categories = ['Differentiable', 'Unimodal']  # 'Separable',
case_label = 'DU'

#  ----------------------------------
# Read operators and find their alias
collections = ['default.txt'] #'short_collection.txt', 'medium_collection.txt',

encoded_heuristic_space = dict()
for collection_file in collections:
    with open('./collections/' + collection_file, 'r') as operators_file:
        encoded_heuristic_space[collection_file] = [eval(line.rstrip('\n')) for line in operators_file]

# Search operator aliases
perturbator_alias = {
    'random_search': 'RS',
    'central_force_dynamic': 'CF',
    'differential_mutation': 'DM',
    'firefly_dynamic': 'FD',
    'genetic_crossover': 'GC',
    'genetic_mutation': 'GM',
    'gravitational_search': 'GS',
    'random_flight': 'RF',
    'local_random_walk': 'RW',
    'random_sample': 'RX',
    'spiral_dynamic': 'SD',
    'swarm_dynamic': 'PS'}

selector_alias = {'greedy': 'g', 'all': 'd', 'metropolis': 'm', 'probabilistic': 'p'}

operator_families = {y: i for i, y in enumerate(sorted([x for x in perturbator_alias.values()]))}

# Pre-build the alias list
heuristic_space = dict()
for collection_file in collections:
    heuristic_space[collection_file] = [perturbator_alias[x[0]] + selector_alias[x[2]] for x in encoded_heuristic_space[collection_file]]

# Find repeated elements
for collection_file in collections:
    for heuristic in heuristic_space[collection_file]:
        concurrences = tl.listfind(heuristic_space[collection_file], heuristic)
        if len(concurrences) > 1:
            for count, idx in enumerate(concurrences):
                heuristic_space[collection_file][idx] += f'{count + 1}'


# Read basic metaheuristics
with open('collections/' + 'basicmetaheuristics.txt', 'r') as operators_file:
    basic_mhs_collection = [eval(line.rstrip('\n')) for line in operators_file]

# Read basic metaheuristics cardinality
basic_mhs_cadinality = [1 if isinstance(x, tuple) else len(x) for x in basic_mhs_collection]


dimensions = [2, 10, 30, 50]

def sort_dict(dataset):
    problems = dataset['problem']
    dimensions = dataset['dimensions']
    results = dataset['results']
    list_pair_prob_dim = list(zip(problems, dimensions, results))
    list_pair_prob_dim.sort()
    prob_sorted = []
    dim_sorted = []
    res_sorted = []
    for a, b, c in list_pair_prob_dim:
        prob_sorted.append(a)
        dim_sorted.append(b)
        res_sorted.append(c)
    dataset['problem'] = prob_sorted
    dataset['dimensions'] = dim_sorted
    dataset['results'] = res_sorted

def filter_by_dimensions(dataset):
    allowed_dim_inds = [index for d in dimensions for index in tl.listfind(dataset['dimensions'], d)]
    dict_filtered = {key: [val[x] for x in allowed_dim_inds] for key, val in dataset.items()}
    sort_dict(dict_filtered)
    return dict_filtered


# Load data from basic metaheuristics
basic_mhs_data = filter_by_dimensions(tl.read_json('data_files/basic-metaheuristics-data_v2.json'))
basic_metaheuristics = basic_mhs_data['results'][0]['operator_id']

long_dimensions = basic_mhs_data['dimensions']
long_problems = basic_mhs_data['problem']


# Call the problem categories
problem_features = bf.list_functions(fts=chosen_categories)
categories = sorted(set([problem_features[x]['Code'] for x in basic_mhs_data['problem']]), reverse=True)

# Obtain the optimum value per each problem
# optimum_value = {(problem_name, num_dimensions): bf.choose_problem(problem_name, num_dimensions).global_optimum_solution for problem_name in problem_features for num_dimensions in dimensions}

# --------------------------------
# Special adjustments for the plots
plt.rc('text', usetex=True)
plt.rc('font', size=18)     # family='serif',

# Colour settings
cmap = plt.get_cmap('tab20')
colour_cat = [cmap(i)[:-1] for i in np.linspace(0, 1, len(categories))]
colour_dim = [cmap(i)[:-1] for i in np.linspace(0, 1, len(dimensions))]

# Saving images flag
folder_name = 'data_files/results_nn_hh/'
if is_saving:
    # Read (of create if so) a folder for storing images
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)


collection_experiments = dict({
    'Small_pop30': {
        'filename': 'default_mlp_30pop_small',
        'id': 'Small\_pop30',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.22],
        'has_performance': True,
    },
    'Medium': {
        'filename': 'default_mlp_30pop',
        'id': 'Medium',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.23],
        'has_performance': True,
    },
    'Big': {
        'filename': 'default_mlp_30pop_big',
        'id': 'Big',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.22],
        'has_performance': True,
    },    
    'Deep': {
        'filename': 'default_mlp_30pop_deep',
        'id': 'Deep',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.24],
        'has_performance': True,
    },
    'LSTM_variable_length': {
        'filename': 'default_lstm_30pop',
        'id': 'LSTM\_variable\_length',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.22],
        'has_performance': True,
    },
    'LSTM_max_fixed_length': {
        'filename': 'default_lstm_padded_30pop',
        'id': 'LSTM\_max\_fixed\_length',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.21],
        'has_performance': True
    },
    'LSTM_30_fixed_length': {
        'filename': 'default_lstm_cut_30pop',
        'id': 'LSTM\_30\_fixed\_length',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.26],
        'has_performance': True
    },
    'Small_pop50': {
        'filename': 'default_mlp_50pop_small',
        'id': 'Small\_pop50',
        'pop': 50,
        'collection': 'default.txt',
        'ylim': [0, 0.24],
        'has_performance': True,  
    },
    'unfolded_hhs_pop30': {
        'filename': 'unfolded_hhs_pop30',
        'id': 'unfolded\_mh\_pop30',
        'pop': 30,
        'collection': 'default.txt',
        'ylim': [0, 0.15], 
        'is_unfolded': True,
    },
    'unfolded_hhs_pop50': {
        'filename': 'unfolded_hhs_pop50',
        'id': 'unfolded\_mh\_pop50',
        'pop': 50,
        'collection': 'default.txt',
        'ylim': [0, 0.15], 
        'is_unfolded': True,
    }
})


# Read the data file and assign the variables
data_files = dict({experiment: collection_experiments[experiment] for experiment in consider_experiments})

# Obtain results of unfolded performances
temporal_data = tl.read_json('data_files/unfolded_hhs_pop30.json')
data_frame = filter_by_dimensions(temporal_data)
unfolded_performance_pop30 = [x['performance'][-1] for x in data_frame['results']]

temporal_data = tl.read_json('data_files/unfolded_hhs_pop50.json')
data_frame = filter_by_dimensions(temporal_data)
unfolded_performance_pop50 = [x['performance'][-1] for x in data_frame['results']]

    



# Retrive the results from each experiment
data_tables = dict()
for experiment in data_files:
    filename = data_files[experiment]['filename']
    temporal_data = tl.read_json('data_files/' + filename + '.json')
    data_frame = filter_by_dimensions(temporal_data)
    collection_file = data_files[experiment]['collection']
    is_unfolded_results = data_files[experiment].get('is_unfolded', False)
    has_performance = data_files[experiment].get('has_performance', False)
    last_element = lambda seq: [y[-1] for y in seq]

    # Obtain performances
    if is_unfolded_results:
        current_performances = [x['performance'][-1] for x in data_frame['results']]
    else:
        current_performances = [x['performance'] for x in data_frame['results']]
    # For basic metaheuristics
    basic_performances = [x['performance'] for x in np.copy(basic_mhs_data['results'])]

    # Compare the current metaheuristic against the basic metaheuristics
    performance_comparison = [np.copy(x - np.array(y)) for x, y in zip(current_performances, basic_performances)]

    # Success rate with respect to basic metaheuristics
    success_rates = [np.sum(x <= 0.0) / len(x) for x in performance_comparison]
    
    # Compare the current metaheuristic against the basic metaheuristics
    performance_comparison_uMH30 = [np.copy(x - y) for x, y in zip(current_performances, unfolded_performance_pop30)]

    # Success rate with respect to basic metaheuristics
    success_rates_uMH30 = [1 if x <= 0.0 else 0 for x in performance_comparison_uMH30]
    
    # Compare the current metaheuristic against the basic metaheuristics
    performance_comparison_uMH50 = [np.copy(x - y) for x, y in zip(current_performances, unfolded_performance_pop50)]

    # Success rate with respect to basic metaheuristics
    success_rates_uMH50 = [1 if x <= 0.0 else 0 for x in performance_comparison_uMH50]

    # Create a data frame   
    performance = current_performances 
    if is_unfolded_results:
        steps_name = 'step'
        cardinality = [len(x['encoded_solution'][-1]) for x in data_frame['results']]
        unique_SO = [len(np.unique(x['encoded_solution'][-1])) for x in data_frame['results']]
        hFitness = [last_element(x['hist_fitness']) for x in data_frame['results']]
        pValue = [stats.normaltest(last_element(x['hist_fitness']))[1] for x in data_frame['results']]
        operatorFamily = [[operator_families[heuristic_space[collection_file][y][:2]] for y in x['encoded_solution'][-1]]
                            for x in data_frame['results']]
    else:
        steps_name = 'rep'
        fitness_name = 'hist_fitness' if has_performance else 'best_fitness'
        best_solutions = [np.argmin([y[-1] for y in x[fitness_name]]) for x in data_frame['results']]
        cardinality = [len(x['encoded_solution'][best_sol]) for x, best_sol in zip(data_frame['results'], best_solutions)]
        unique_SO = [len(np.unique(x['encoded_solution'][best_sol])) for x, best_sol in zip(data_frame['results'], best_solutions)]

        hFitness = [[y[-1] for y in x[fitness_name]] for x in data_frame['results']]
        pValue = [stats.normaltest([y[-1] for y in x[fitness_name]])[1] for x in data_frame['results']]
        operatorFamily = [[operator_families[heuristic_space[collection_file][y][:2]] for y in x['encoded_solution'][best_sol]]
                            for x, best_sol in zip(data_frame['results'], best_solutions)]

    id = data_files[experiment]['id']
    data_tables[id] = pd.DataFrame({
        'Dim': [str(x) for x in data_frame['dimensions']],
        'Pop': data_files[experiment]['pop'],
        'Problem': data_frame['problem'],
        'Cat': [problem_features[x]['Code'] for x in data_frame['problem']],
        'Performance': performance,
        'Steps': [x[steps_name][-1] for x in data_frame['results']],
        'Cardinality': cardinality,
        'Unique': unique_SO,
        'hFitness': hFitness,
        'pValue': pValue,
        'operatorFamily': operatorFamily,
        'successRate': success_rates,
        'successRateUMH30': success_rates_uMH30,
        'successRateUMH50': success_rates_uMH50
    })

# Melt data in one table
full_table = pd.concat(data_tables, axis=0, names=['Id', 'RID']).reset_index(level=0)
full_table['Dim'] = full_table['Dim'].apply(lambda x: int(x))
full_table['Pop'] = full_table['Pop'].apply(lambda x: int(x))

full_table['Rank'] = full_table.groupby(by=['Dim', 'Problem'])['Performance'].rank(method='dense')
full_table['RankSR'] = full_table.groupby(by=['Dim', 'Problem'])['successRate'].rank(method='dense', ascending=False)
full_table['DimPop'] = full_table[['Dim', 'Pop']].agg(tuple, axis=1)


def app_time_complexity(row):
    fam_list = row['operatorFamily']
    dim = row['Dim']
    pop = row['Pop']
    tc_by_fam = {
        0: 2 * pop,                     # CF
        1: pop ** 2,                    # DM
        2: 2 * pop,                     # FD
        3: pop ** 2,                    # GC
        4: pop,                         # GM
        5: 2 * pop,                     # GS
        6: 2 * pop,                     # PS
        7: 1,                           # RF
        8: 1,                           # RS
        9: pop,                         # RW
        10: 1,                          # RX
        11: pop * (dim ** 2.3737)       # SD
    }

    return np.sum(np.array([tc_by_fam[x] for x in fam_list]))

    
full_table['tcMH'] = np.log10(full_table['Dim'] * full_table['Pop'] *
                              full_table.apply(app_time_complexity, axis=1))

full_table['tcHH'] = full_table['tcMH'] + np.log10((full_table['Steps'] + 1) * 50)

theo_limit = pd.DataFrame([(d, p, np.log10(50 * 200 * 100 * d * (p ** 3))) for p in [30, 50, 100] for d in dimensions],
                          columns=['Dim', 'Pop', 'Theoretical'])


full_table = full_table.reset_index()



# %% [Optional] Search operators in 'default.txt' collection
heuristic_space = []
with open('collections/default.txt', 'r') as operators_file:
    heuristic_space = [eval(line.rstrip('\n')) for line in operators_file]
mh_so = []
selector_so = []
for mh, _, selector in heuristic_space:
    mh_so.append(mh.replace('_', '\_'))
    selector_so.append(selector.replace('_', '\_'))
DF = pd.DataFrame({'Metaheuristic': mh_so, 'Selector': selector_so})


fig, ax = plt.subplots(figsize=(12,6))
fig.subplots_adjust()
fig.tight_layout()
so_dist = sns.countplot(data=DF, x='Metaheuristic', hue='Selector', ax=ax, palette='tab10')
locs, labels = plt.xticks()
plt.setp(labels, rotation=45)
so_dist.set_xlabel(r'Basic metaheuristic search operators')
so_dist.set_ylabel(r'Number of search operators')

if is_saving:
    plt.savefig(folder_name + 'search_operators_collection_default.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
if show_plots:
    plt.show()



# %% First Plot // Percentage of winning per dimmension


ids_list = full_table['Id'].unique()
dims_list = full_table['Dim'].unique()

A, B, C = [], [], []
for Id in ids_list:
    for Dim in dims_list:
        A.append(Id)
        B.append(Dim)
        cnt = ((full_table['Id'] == Id) & (full_table['Dim'] == Dim) & (full_table['Rank'] == 1)).sum()
        C.append(cnt)
best_table_rank = pd.DataFrame({'Id': A, 'Dim': B, 'Count': C})

sums_id = dict()
sums_dim = dict()
for Id in ids_list:
    Idx = (best_table_rank['Id'] == Id) 
    sums_id[Id] = best_table_rank[Idx]['Count'].sum()
        
        
for Dim in dims_list:
    Idx = (best_table_rank['Dim'] == Dim)

    sums_dim[Dim] = best_table_rank[Idx]['Count'].sum()
        
        
best_table_rank_dim = best_table_rank.copy()
for idx in best_table_rank_dim.index:
    x = best_table_rank_dim.iloc[idx]
    best_table_rank_dim.loc[idx, 'Count'] = 100*x['Count'] / sums_dim[x['Dim']]

fig, ax = plt.subplots(figsize=(12,7))
fig.subplots_adjust()
fig.tight_layout()
p_1_winner = sns.barplot(data=best_table_rank_dim, x='Dim', y='Count', hue='Id', palette='tab10')

p_1_winner.set_xlabel(r'Dimension')
p_1_winner.set_ylabel('Percentage')

if is_saving:
    plt.savefig(folder_name + results_file_name + '_' + 'Rank_Winner_dim.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
if show_plots:
    plt.show()










# %% Second plot // General rank vs dim and pop

plt.figure(figsize=[5.5, 4])
sns.lineplot(data=full_table, x='Dim', y='Rank', palette='tab10', hue='Id')

#if is_saving:
#    plt.savefig(folder_name + results_file_name + '_' + 'Rank_vs_Dim_Id-Line.' + saving_format, format=saving_format, dpi=333, bbox_inches="tight", transparent=True)

if show_plots:
    plt.show()





# %% Third Plot // Comparison of experiments against basic MH and uMH30
success_table_basic = full_table.groupby(['Id', 'Dim'])['successRate'].mean()
success_table_uMH30 = full_table.groupby(['Id', 'Dim'])['successRateUMH30'].mean()
table_bydim_basic = success_table_basic.reset_index().set_index('Dim')
table_bydim_uMH30 = success_table_uMH30.reset_index().set_index('Dim')
dims = table_bydim_basic.index.unique()
ids = table_bydim_basic['Id'].unique()

ids_dict = dict()
for id in ids:
    ids_dict['Basic MH'] = list(table_bydim_basic[table_bydim_basic['Id'] == id]['successRate']*100) 
    ids_dict['Unfolded MH pop30'] = list(table_bydim_uMH30[table_bydim_uMH30['Id'] == id]['successRateUMH30']*100) 
    df = pd.DataFrame(ids_dict, index=dims)
    
    fig, ax = plt.subplots(figsize=(6,7.5))
    fig.subplots_adjust()
    fig.tight_layout()
    sns.heatmap(df, vmin=0, vmax=100, annot=True,  cmap="YlGnBu")
    plt.title(f'Percentage comparison for {id}')
    
    id_text = id.replace('\\', '')

    if is_saving:
        plt.savefig(folder_name  +  f'{id_text}_Percentage_cmp_BMH_UMH30.' + saving_format,
                format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
    if show_plots:
        plt.show()

# %% Third.Half Plot // Comparison of experiments against basic MH and uMH50
success_table_basic = full_table.groupby(['Id', 'Dim'])['successRate'].mean()
success_table_uMH50 = full_table.groupby(['Id', 'Dim'])['successRateUMH50'].mean()
table_bydim_basic = success_table_basic.reset_index().set_index('Dim')
table_bydim_uMH50 = success_table_uMH50.reset_index().set_index('Dim')
dims = table_bydim_basic.index.unique()
ids = table_bydim_basic['Id'].unique()

ids_dict = dict()
for id in ids:
    ids_dict['Basic MH'] = list(table_bydim_basic[table_bydim_basic['Id'] == id]['successRate']*100)
    ids_dict['Unfolded MH pop50'] = list(table_bydim_uMH50[table_bydim_uMH50['Id'] == id]['successRateUMH50']*100)
    df = pd.DataFrame(ids_dict, index=dims)
    
    fig, ax = plt.subplots(figsize=(6,7.5))
    fig.subplots_adjust()
    fig.tight_layout()
    sns.heatmap(df, vmin=0, vmax=1, annot=True,  cmap="YlGnBu")
    plt.title(f'Percentage comparison for {id}')
    
    id_text = id.replace('\\', '')

    if is_saving:
        plt.savefig(folder_name  +  f'{id_text}_Percentage_cmp_BMH_UMH50.' + saving_format,
                format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
    if show_plots:
        plt.show()




# %% Fourth Plot // Wilcoxon test
print(len(basic_mhs_data['results'][0]['operator_id']))

p_value = 0.05
dict_basicMH_perf = dict()
for i in basic_mhs_data['results'][0]['operator_id']:
    dict_basicMH_perf[i] = []
    
for x in basic_mhs_data['results']:
    for i, y in zip(x['operator_id'], x['performance']):
        dict_basicMH_perf[i].append(y)

for id in ids:
    performance_id = list(data_tables[id]['Performance'])
    results_stats = []
    print(f'Testing {id}')
    for i, x in enumerate(dict_basicMH_perf):
        _, p = stats.wilcoxon(performance_id, dict_basicMH_perf[x], alternative='less')
        if p > p_value:
            print('Winner: ', basic_mhs_collection[i])
        results_stats.append(p)
    print('\n\n')
    fig, ax = plt.subplots(figsize=(6,4))
    fig.subplots_adjust()
    fig.tight_layout()
    #ax.set(yscale='log')
    #results_stats = [1, 2, 3]
    df = pd.DataFrame({'Basic MH': list(range(len(results_stats))), 'p-value': results_stats })
    #ax.bar(df['Basic MH'], df['p-value'], color='blue')
    #plt.legend()
    barplottt = sns.barplot(x=df['Basic MH'], y=df['p-value'], palette='tab10')
    ax.axhline(y=p_value, color='black', linestyle='--')
    barplottt.set_yscale('linear')
    barplottt.set(xticks=[])
    ax.set_xlabel('Basic metaheuristics')
    ax.set_ylabel('$p$-value')
    ax.set_title(f"Wilcoxon test ({id})")
    id_text = id.replace('\\', '')

    if is_saving:
        plt.savefig(folder_name +  f'{id_text}_pvalue_linear_scale.' + saving_format,
                format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
    if show_plots:
        plt.show()

    
    fig, ax = plt.subplots(figsize=(6,4))
    fig.subplots_adjust()
    fig.tight_layout()
    barplottt = sns.barplot(x=df['Basic MH'], y=df['p-value'], palette='tab10')
    ax.axhline(y=0.05, color='black', linestyle='--')
    barplottt.set_yscale('log')
    barplottt.set(xticks=[])
    ax.set_xlabel('Basic metaheuristics')
    ax.set_ylabel('$p$-value')
    ax.set_title(f"Wilcoxon test ({id})")
    id_text = id.replace('\\', '')
    if is_saving:
        plt.savefig(folder_name +  f'{id_text}_pvalue_log_scale.' + saving_format,
                format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
    if show_plots:
        plt.show()

    
# %% Wilcoxon against uMH30
for id in ids:
    if id == 'unfolded\_mh\_pop30':
        continue
    performance_id = list(data_tables[id]['Performance'])
    performance_UMH30 = list(unfolded_performance_pop30)
    w, p = stats.wilcoxon(performance_id, performance_UMH30, alternative='less')
    print(w, p)
# %% Wilcoxon against uMH50
for id in ids:
    if id == 'unfolded\_mh\_pop50':
        continue
    performance_id = list(data_tables[id]['Performance'])
    performance_UMH50 = list(unfolded_performance_pop50)
    w, p = stats.wilcoxon(performance_id, performance_UMH50, alternative='less')
    print(w, p)

# %% Wilcoxon between ids
fig, ax = plt.subplots(figsize=(8,6))

fig.subplots_adjust()
fig.tight_layout()
dict_comparison = dict()
for id in ids:
    performance_id = list(data_tables[id]['Performance'])    
    dict_comparison[id] = []
    for id2 in ids:
        performance_id2 = list(data_tables[id2]['Performance'])
        if id == id2:
            p = 1
        else:
            w, p = stats.wilcoxon(performance_id, performance_id2)#, alternative='less')
        dict_comparison[id].append(p)

df_comparison = pd.DataFrame(dict_comparison, index=ids)
sns.heatmap(df_comparison, vmin=0, vmax=1, annot=True,  cmap="Reds")
ax.set_title('Alternative: Different than')
ax.set_xlabel('$A$')
ax.set_ylabel('$B$')

if is_saving:
    plt.savefig(folder_name + results_file_name + '_' + 'wilcoxon_all_pairs_twosided.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
if show_plots:
    plt.show()

#%%
fig, ax = plt.subplots(figsize=(8,6))
fig.subplots_adjust()
fig.tight_layout()
dict_comparison = dict()
for id in ids:
    performance_id = list(data_tables[id]['Performance'])    
    dict_comparison[id] = []
    for id2 in ids:
        performance_id2 = list(data_tables[id2]['Performance'])
        if id == id2:
            p = 0
        else:
            w, p = stats.wilcoxon(performance_id, performance_id2, alternative='less')
        dict_comparison[id].append(p)

df_comparison = pd.DataFrame(dict_comparison, index=ids)
sns.heatmap(df_comparison, vmin=0, vmax=1, annot=True,  cmap="Blues")
ax.set_title('Alternative: Outperform than')
ax.set_xlabel('$A$')
ax.set_ylabel('$B$')

if is_saving:
    plt.savefig(folder_name + results_file_name + '_' + 'wilcoxon_all_pairs_less.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
if show_plots:
    plt.show()
#%%
fig, ax = plt.subplots(figsize=(8,6))
fig.subplots_adjust()
fig.tight_layout()
dict_comparison = dict()
for id in ids:
    performance_id = list(data_tables[id]['Performance'])    
    dict_comparison[id] = []
    for id2 in ids:
        performance_id2 = list(data_tables[id2]['Performance'])
        if id == id2:
            p = 0
        else:
            w, p = stats.wilcoxon(performance_id, performance_id2, alternative='greater')
        dict_comparison[id].append(p)

df_comparison = pd.DataFrame(dict_comparison, index=ids)
sns.heatmap(df_comparison, vmin=0, vmax=1, annot=True,  cmap="Greens")
ax.set_title('Alternative: Worst than')
ax.set_xlabel('$A$')
ax.set_ylabel('$B$')

if is_saving:
    plt.savefig(folder_name + results_file_name + '_' + 'wilcoxon_all_pairs_greater.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)
if show_plots:
    plt.show()

plt.close('all')

#%%
"""
# %% Fifth Plot? // Cardinality comparison
p_5 = sns.displot(data=full_table, hue='Id', col='Dim', x='Cardinality', kind='kde', palette='tab10', height=2.5,
                 aspect=0.8, fill=True)

if is_saving:
    p_5.savefig(folder_name + results_file_name + '_' + 'Card_vs_Dim_Id-KDE.' + saving_format, format=saving_format, dpi=333, bbox_inches="tight", transparent=True)

if show_plots:
    plt.show()

# %% [Optional] 2.1 Plot // Comparison of winners per category 
rank_1 = full_table['Rank'] == 1
table_rank_1 = full_table[rank_1]

p_1_optional = sns.catplot(data=table_rank_1, hue='Id', x='Rank',row='Cat',  col='Dim', kind='count', height=1.8, aspect=0.8, legend=True )

p_1_optional.set_xlabel(r'Dimension')
p_1_optional.set_ylabel('Percentage')
if is_saving:
    p_1_optional.savefig(folder_name + results_file_name + '_' + 'Rank_vs_Id_and_Dim_Cat-BestRanked.' + saving_format,
               format=saving_format, dpi=333, bbox_inches="tight", transparent=True)

if show_plots:
    plt.show()


# %% [optional] 3.1 Plot // Heat map  0 - 100 sucess rate against basic metaheuristics 
success_table = full_table.groupby(['Id', 'Dim'])['successRate'].mean()
table_bydim = success_table.reset_index().set_index('Dim')
dims = table_bydim.index.unique()
ids = table_bydim['Id'].unique()

ids_dict = dict()
for id in ids:
    ids_dict[id] = list(table_bydim[table_bydim['Id'] == id]['successRate'])
df = pd.DataFrame(ids_dict, index=dims, columns=ids)
sns.heatmap(df, vmin=0, vmax=1, annot=True,  cmap="YlGnBu")


# %% [optional] Comparison of number of different SO that each experiment has
p_5_so = sns.displot(data=full_table, hue='Id', col='Dim', x='Unique', kind='kde', palette='tab10', height=2.5,
                 aspect=0.8, fill=True)
p_5_so.set_xlabels('Number of different SO')

if is_saving:
    p_5_so.savefig(folder_name + results_file_name + '_' + 'Unique_vs_Dim_Id-KDE.' + saving_format, format=saving_format, dpi=333, bbox_inches="tight", transparent=True)

if show_plots:
    plt.show()

# %% p-Value per Dim and Cat


def plot_pvalue_boxplot(data_table, id):
    fig = plt.figure(figsize=(5, 2.5))
    sns.boxplot(data=data_table, x='Dim', y='pValue', hue='Cat', hue_order=categories)
    plt.hlines(0.05, -0.5, len(dimensions)-0.5)
    plt.ylabel(r'$p$-Value')
    plt.title(r'Id = {}'.format(id))
    if show_plots:
        plt.show()

    if is_saving:
        id_file = ''.join(c for c in id if c not in '\\')
        fig.savefig(folder_name + results_file_name + '_' + 'pValue-id_{}-CatDim-BoxPlot.'.format(id_file) + saving_format,
                    format=saving_format, dpi=333, bbox_inches="tight", transparent=True)


for pop, data_table in data_tables.items():
    plot_pvalue_boxplot(data_table, pop)
"""