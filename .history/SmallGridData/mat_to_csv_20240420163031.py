import scipy.io as scipy
import os
import os.path as osp
import pandas as pd
import numpy as np

BASEDIR = osp.dirname(osp.abspath(__file__))
FILE_NAME = 'SmallGrid.mat'
OUTPUT_NAME = 'SmallGrid' 

# Load the .mat file
mat = scipy.loadmat(BASEDIR+'/'+FILE_NAME)

# Extract the data from the .mat file
mat_Arcs = list(mat.values())[3]

# Special case for SmallGridData: there is no self-connection. add it 
for i in range(0,100):
    mat_Arcs[i][i] = 1

#combine the two sets of requests into one
mat_Requests = list(mat.values())[4]
mat_Requests = np.concatenate((mat_Requests[:,0,:],mat_Requests[:,1,:]),axis=0) 
#Origin-node, Destination-node, request time, number of people in the request, max waiting time of this request, ID

mat_t_V = list(mat.values())[5]

df_Arcs = pd.DataFrame(mat_Arcs)
df_Requests = pd.DataFrame(mat_Requests)
# Origin-node, Destination-node, request time, number of people in the request, max waiting time of this request, ID
df_Requests = df_Requests.rename(columns={0: 'Oid', 1: 'Did', 2: 'Req_t', 3: 'Num_ppl', 4: 'Max_wait', 5: 'Req_ID'})
df_Requests = df_Requests.sort_values(by='Req_ID') #sort by request id
# Request nodes range is [1,100], change it to [0,99]
df_Requests['Oid'] = df_Requests['Oid'] - 1
df_Requests['Did'] = df_Requests['Did'] - 1
df_t_V = pd.DataFrame(mat_t_V)
# df_t_V.sort_values(by=[0,1], inplace=True)

# Save the DataFrame to a CSV file
df_Arcs.to_csv(BASEDIR + '/' + OUTPUT_NAME + '_Arcs.csv', index=False)
df_Requests.to_csv(BASEDIR + '/' + OUTPUT_NAME + '_Requests.csv', index=False)
df_t_V.to_csv(BASEDIR + '/' + OUTPUT_NAME + '_TimeCost.csv', index=False)