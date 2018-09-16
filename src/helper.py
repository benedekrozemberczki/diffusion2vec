import argparse
from texttable import Texttable
import numpy as np
from gensim.models.doc2vec import TaggedDocument
from tqdm import tqdm

def parameter_parser():
    """
    A method to parse up command line parameters. By default it gives an embedding of the Facebook Restaurants network.
    The default hyperparameters give a high quality representation already without grid search.
    :return : Object with hyperparameters.
    """

    parser = argparse.ArgumentParser(description = "Run diffusion2vec.")

    parser.add_argument('--input',
                        nargs = '?',
                        default = './data/restaurant_edges.csv',
	                help = 'Input graph path')

    parser.add_argument('--output',
                        nargs = '?',
                        default = './output/restaurant.csv',
	                help = 'Embeddings path')

    parser.add_argument('--model',
                        nargs = '?',
                        default = 'non-pooled',
	                help = 'Model type.')

    parser.add_argument('--dimensions',
                        type = int,
                        default = 128,
	                help = 'Number of dimensions. Default is 128.')

    parser.add_argument('--vertex-set-cardinality',
                        type = int,
                        default = 40,
	                help = 'Length of diffusion per source is 2*cardianlity-1. Default is 40.')

    parser.add_argument('--num-diffusions',
                        type = int,
                        default = 10,
	                help = 'Number of diffusions per source. Default is 10.')

    parser.add_argument('--window-size',
                        type = int,
                        default = 10,
                    	help = 'Context size for optimization. Default is 10.')

    parser.add_argument('--iter',
                        default = 1,
                        type = int,
                        help = 'Number of epochs in ASGD. Default is 1.')

    parser.add_argument('--workers',
                        type = int,
                        default = 4,
	                help = 'Number of cores. Default is 4.')

    parser.add_argument('--alpha',
                        type = float,
                        default = 0.025,
	                help = 'Initial learning rate. Default is 0.025.')
    
    return parser.parse_args()



def generation_tab_printer(read_times, generation_times):
    """
    Function to print the time logs in a nice tabular format.
    :param read_times: List of reading times.
    :param generation_times: List of generation times.
    """
    t = Texttable() 
    t.add_rows([["Metric","Value"],
                ["Mean graph read time:", np.mean(read_times)],
                ["Standard deviation of read time.",np.std(read_times)]]) 
    print t.draw() 
    t = Texttable()
    t.add_rows([["Metric","Value"],
                ["Mean sequence generation time:", np.mean(generation_times)],
                ["Standard deviation of generation time.",np.std(generation_times)]])
    print t.draw() 

def result_processing(results):
    """
    Function to separate the sequences from time measurements and process them.
    :param results: List of 3-length tuples including the sequences and results.
    :return walk_results: List of random walks.
    """
    walk_results = map(lambda x: x[0],results)
    read_time_results = map(lambda x: x[1],results)
    generation_time_results = map(lambda x: x[2],results)
    counts = max(map(lambda x: x[3],results))
    generation_tab_printer(read_time_results, generation_time_results)
    walk_results = [walk for walks in walk_results for walk in walks]
    return walk_results, counts


def process_non_pooled_model_data(walks, counts, args):
    print("Run Feature extraction")
    features = {str(node):[] for node in range(counts)}
    for walk in tqdm(walks):
        for i in range(len(walk)-args.window_size):
            for j in range(1,args.window_size+1):
                features[walk[i]].append(["+"+str(j)+"_"+walk[i+j]])
                features[walk[i+j]].append(["_"+str(j)+"_"+walk[i]])

    docs = [TaggedDocument(words = [x[0] for x in v], tags = [str(k)]) for k, v in features.iteritems()]
    return docs
    
