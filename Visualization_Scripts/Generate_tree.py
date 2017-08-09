import numpy as np
import sys
import random as rd
from scipy.sparse import coo_matrix
import collections 
from itertools import chain
import matplotlib.pyplot as plt
from matplotlib import rc
import os
import csv
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)


def generate_tree(N):
	counter=1
	levels=[[0]]
	num_of_children=[]
	Adj=[]
	while counter<=N:
		new_level=[]
		Interruption=[]
		for j in levels[-1]:
			if j==0:
				tentative_children=rd.randint(3,4)
			else:
				tentative_children=rd.randint(0,4)
			children=0
			if tentative_children==0:
				Interruption.append(False)
			for n in range(0,tentative_children):
				if counter+1>N:
					n=tentative_children #Leave the loop
					counter=N+1
				else:
					children+=1
					counter+=1
					new_level.append(counter-1)
					Adj.append([j,counter-1])
					Adj.append([counter-1,j])
			num_of_children.append(children)
		if Interruption==[False for k in range(0,len(levels[-1]))]:
			num_of_children=num_of_children[:-len(levels[-1])]
		if len(new_level)>0:
			levels.append(new_level)
			
	if len(num_of_children)<N:
		num_of_children=num_of_children+[0 for n in range(0,N-len(num_of_children))]
		
	num_of_children=np.array(num_of_children)
	Adj=np.array(Adj)
	A=coo_matrix((np.ones(len(Adj)), (Adj[:,0],Adj[:,1])), shape=(N,N))
	if (A-A.transpose()).nnz>0:
		print "ADJACENCY MATRIX IS NOT SYMMETRIC PROBLEM"
	else:
		print "ADJACENCY MATRIX IS SYMMETRIC"
	
	return Adj,levels,num_of_children
	
def Plot_tree(fig, ax, N, Adj, Levels, Num_of_children):
	
	### PLOT NODES ###
	Y=[]
	for n in range(0,N):
		for l in range(0,len(Levels)):
			if n in Levels[l]:
				Y.append(-l)
				
	X=np.zeros(N)
	counter=1
	for n in range(0,N):
		level=-Y[n]
		step=1.0/np.exp(1.1*level)
		if Num_of_children[n]>0:
			children_id=[counter+l for l in range(0,Num_of_children[n])]
			for j in children_id:
				X[j]=X[n]+step*(children_id.index(j)-float((Num_of_children[n])-1)/2.0)
		counter+=Num_of_children[n]
		if counter==N:
			break

	ax.scatter(X,Y,s=20, c='k', marker="o",lw=0.1)	
	# Node annotations
	"""
	for i in range(0,N):
		ax.annotate(str(i), xy=(X[i],Y[i]),fontsize=10)
	"""
	### PLOT LINES
	for i in range(0,len(Adj),2):
		id_1,id_2=Adj[i]
		ax.plot([X[id_1],X[id_2]],[Y[id_1],Y[id_2]], lw=0.5,color="k")

	### PLOT COSMETICS
	fig.subplots_adjust(left=0.03, bottom=None, right=0.97, top=None, wspace=None, hspace=0.4)
	fig.set_size_inches(17, 12, forward=True)
	fig.suptitle(str(N)+' Nodes', fontsize=30)
	ax.tick_params(axis='both', which='both', bottom='off', top='off', left='off', right='off', labelleft='off', labelbottom='off')
	ax.set_xlim(min(X)-0.05,max(X)+0.05)
	return [X,Y]
	
def Tree_statistics(N,Adj,Levels,Num_of_children):
	
	Num_levels=len(Levels)
	print "NUMBER OF LEVELS", Num_levels
	
	Source_Distance_Distribution=[]
	for l in Levels:
		Source_Distance_Distribution.append(len(l))
	
	Average_source_distance=0
	for d in range(0,len(Source_Distance_Distribution)):
		Average_source_distance+=d*Source_Distance_Distribution[d]
	Average_source_distance=float(Average_source_distance)/float(N)
	print "AVERAGE SOURCE DISTANCE", Average_source_distance

	A=coo_matrix((np.ones(len(Adj)), (Adj[:,0],Adj[:,1])), shape=(N,N)).todense()
	A=np.array(A)
	print "AVERAGE DEGREE", (A.sum(axis=0)).sum()/float(N)
	# Alternative definition of the average degree, we add (N-1) since all nodes exluding the source have one parent
	# print "AVERAGE DEGREE", (np.array(Num_of_children).sum()+(N-1))/float(N) 
	
	ids=np.arange(0,N)
	Descendants=[0 for n in range(0,N)]
	Descendants_ids=[[] for n in range(0,N)]
	for l in Levels[::-1]:
		for i in l:
			neighbors_of_i=ids[A[i]==1]
			children_of_i=(neighbors_of_i[neighbors_of_i>i])
			Descendants[i]=Num_of_children[i]
			Descendants_ids[i]+=list(children_of_i)
			for n in range(0,len(children_of_i)):
				Descendants[i]+=Descendants[children_of_i[n]]
				Descendants_ids[i]+=Descendants_ids[children_of_i[n]]
	#print "DESCENDANTS", Descendants
	#print "DESCENDANTS IDS", Descendants_ids
	Descendants_counter=collections.Counter(Descendants)
	
	### PLOTTING HISTOGRAMS ###
	fig2, ax = plt.subplots(2,1)
	width=1.0
	ax[0].bar(np.arange(0,len(Source_Distance_Distribution))-width/2.0, Source_Distance_Distribution,width, color='r')
	ax[1].bar(np.array(Descendants_counter.keys())-width/2.0, Descendants_counter.values(),width, color='g')
	
	### PLOT COSMETICS ###
	fig2.subplots_adjust(left=0.1, bottom=None, right=0.9, top=None, wspace=None, hspace=0.4)
	fig2.set_size_inches(17, 12, forward=True)
	fig2.suptitle(str(N)+' Nodes', fontsize=30)
	ax[0].tick_params(axis='both', which='both', labelsize=20)
	ax[1].tick_params(axis='both', which='both', labelsize=20)
	ax[0].set_xlim(-2,len(Source_Distance_Distribution)+1)
	ax[1].set_xlim(-2,N+1),
	ax[0].set_ylabel("Number of nodes",fontsize=25)
	ax[0].set_xlabel("Distance from source",fontsize=25)
	ax[1].set_ylabel("Number of nodes",fontsize=25)
	ax[1].set_xlabel("Number of descendants",fontsize=25)
	
	return np.array(Descendants), Descendants_ids

def Line_load(Descendants_ids,time_series,node):
	
	# In a tree network there are as many lines as there are nodes,
	# To each node we thus associate the load on the line above it
	# which is given by the sum of the load on the node considered + the load of all its descendants! 
	load = np.copy(time_series[:,node])
	for j in range(0,len(Descendants_ids[node])):
		load += time_series[:,Descendants_ids[node][j]]
	
	num_days=len(load)/1440
	Mean,Std=[],[]
	for i in range(0,num_days):
		Mean.append(load[1440*i:1440*(i+1)].mean())
		Std.append(load[1440*i:1440*(i+1)].std())
	Mean=np.array(Mean)
	Std=np.array(Std)
	return load,Mean,Std
	
def Save_tree(N,Adj,Levels,Num_of_children,Descendants,Descendants_ids,fn):
	
	if not os.path.exists(fn):
		os.makedirs(fn)
	os.chdir(fn)
	np.savetxt("Adjacence_matrix.csv",Adj,delimiter=",",fmt="%i")
	with open("Levels.csv", "wb") as f:
		writer = csv.writer(f)
		writer.writerows(Levels)
	np.savetxt("Num_of_children.csv",Num_of_children,delimiter=",",fmt="%i")
	with open("Descendants_ids.csv", "wb") as f:
		writer = csv.writer(f)
		writer.writerows(Descendants_ids)
	
def main(): 
	
	num_nodes=int(sys.argv[1])
	Adj, Levels, Num_of_children = generate_tree(num_nodes)
	
	fig = plt.figure()
	ax = fig.add_subplot(111)
	Plot_tree(fig, ax, num_nodes,Adj,Levels,Num_of_children)
	Descendants, Descendants_ids = Tree_statistics(num_nodes,Adj,Levels,Num_of_children)
	print "LEVELS",Levels
	print "Num_of Children",Num_of_children
	print "Num_of Children",len(Num_of_children)
	
	Save_tree(num_nodes,Adj,Levels,Num_of_children,Descendants,Descendants_ids,"Tree_N="+str(num_nodes))
	
	plt.show()
	
if __name__ == '__main__':
    main()
