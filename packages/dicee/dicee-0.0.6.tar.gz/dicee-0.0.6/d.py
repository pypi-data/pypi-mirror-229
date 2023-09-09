from dicee.executer import Execute
from dicee.config import Namespace
args = Namespace()
args.path_dataset_folder = 'KGs/UMLS'
args.scoring_technique = 'KvsAll'
args.eval_model = 'train_val_test'
result1 = Execute(args).start()
print(result1)
# 'Train': {'H@1': 1.0, 'H@3': 1.0, 'H@10': 1.0, 'MRR': 1.0},
# 'Val': {'H@1': 0.4624233128834356, 'H@3': 0.683282208588957, 'H@10': 0.9041411042944786, 'MRR': 0.6036344023620824},
# 'Test': {'H@1': 0.48789712556732223, 'H@3': 0.726928895612708, 'H@10': 0.9220877458396369, 'MRR': 0.633470183510084}}

"""
{'H@1': 1.0, 'H@3': 1.0, 'H@10': 1.0, 'MRR': 1.0}
Evaluate Keci on Validation set: Evaluate Keci on Validation set
{'H@1': 0.45015337423312884, 'H@3': 0.6756134969325154, 'H@10': 0.8895705521472392, 'MRR': 0.5935077148200957}
Evaluate Keci on Test set: Evaluate Keci on Test set
{'H@1': 0.4750378214826021, 'H@3': 0.7065052950075643, 'H@10': 0.9175491679273827, 'MRR': 0.6203722969924745}
"""
args = Namespace()
args.path_dataset_folder = 'KGs/UMLS'
args.scoring_technique = 'AllvsAll'
args.eval_model = 'train_val_test'
result2 = Execute(args).start()
print(result2)

"""
Evaluate Keci on Train set: Evaluate Keci on Train set
{'H@1': 1.0, 'H@3': 1.0, 'H@10': 1.0, 'MRR': 1.0}
Evaluate Keci on Validation set: Evaluate Keci on Validation set
{'H@1': 0.49003067484662577, 'H@3': 0.7476993865030674, 'H@10': 0.9294478527607362, 'MRR': 0.6411667754672092}
Evaluate Keci on Test set: Evaluate Keci on Test set
{'H@1': 0.5173978819969742, 'H@3': 0.7503782148260212, 'H@10': 0.9273827534039334, 'MRR': 0.6551162308911966}
"""
assert result2['Val']['MRR'] >= result1['Val']['MRR']
assert result2['Test']['MRR'] >= result1['Test']['MRR']
