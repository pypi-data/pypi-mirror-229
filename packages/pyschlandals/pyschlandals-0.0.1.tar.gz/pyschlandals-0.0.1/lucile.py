from pyschlandals.compiler import compile, Dac
from pyschlandals import BranchingHeuristic
import numpy as np
import torch
import matplotlib.pyplot as plt
import os
from datetime import datetime
import shutil
from pyschlandals.search import approximate
from DACgrad_numpy import compute_gradients

"Ecrit les nouveaux poids des distributions dans le fichier"
def write_w_in_file(softmaxed_w, filename):
    with open(filename, 'r+') as f:
        lines = []
        index = -1
        for line in f.readlines():
            if index in range(len(softmaxed_w)):
                splitted = line.split()
                lines.append(' '.join(splitted[:-2])+'  '+' '.join(softmaxed_w[index].detach().numpy().astype('str'))+'\n')
            else: lines.append(line)
            index += 1
        f.seek(0)
        f.truncate()
        f.writelines(lines)

"Force une distribution à prendre une certaine valeur dans le .cnf"
def write_assignement_in_endfile(value_i, filename):
    with open(filename, 'a') as f:
        f.write('-' + str(value_i) + ' 0')

"Retire du .cnf la contrainte d'une valeur spécifique pour une distribution"
def remove_assignement_in_endfile(value_i,filename):
    with open(filename, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        f.writelines(lines[:-1])

filename = '../schlandals/tests/instances/grouped/two_parents/two_parents_great_children_e_false.cnf'
newname = '..'+filename.split('.')[-2]+'_cpy.'+filename.split('.')[-1]
#copie du fichier pour ne pas modifier l'original
shutil.copyfile(filename, newname)
filename = newname
dac = compile(filename, BranchingHeuristic.MinInDegree)

# initialisation des infos correctes sur le modèle pour le training, pas très intéressant pour le problème
real_weights = np.ndarray((dac.number_distribution_node(),), dtype=object)
current_weights = np.ndarray((dac.number_distribution_node(),), dtype=object)
softmaxed_w = np.ndarray((dac.number_distribution_node(),), dtype=object)
nb_var = 0
s = torch.nn.Softmax()
for i in range(len(real_weights)):
    real_weights[i] = np.zeros((dac.get_distribution_number_value(i)))
    current_weights[i] = torch.nn.Parameter(torch.randn(dac.get_distribution_number_value(i)))#np.random.randn(dacs[0].get_distribution_number_value(i))
    softmaxed_w[i] = s(current_weights[i])
    for j in range(len(real_weights[i])):
        real_weights[i][j] = dac.get_distribution_probability(i,j)
        nb_var += 1
write_w_in_file(softmaxed_w, filename)

epsilon = 0.1

cnt = 1
outputs = np.zeros((len(real_weights)))
for distri_i in range(len(real_weights)):
    print('\ndistribution', distri_i)
    dac = compile(filename, BranchingHeuristic.MinInDegree)
    print('real, exact output',dac.evaluate())
    for value_i in range(len(real_weights[distri_i])):
        print('value', value_i)
        write_assignement_in_endfile(cnt,filename)
        pred = approximate(filename, BranchingHeuristic.MinInDegree, epsilon)
        outputs[distri_i] += pred
        print('approx pred for value', value_i, "is", pred)
        remove_assignement_in_endfile(cnt, filename)
        cnt += 1
    print('sum of approx predictions for all values of distri', distri_i, 'is', outputs[distri_i])