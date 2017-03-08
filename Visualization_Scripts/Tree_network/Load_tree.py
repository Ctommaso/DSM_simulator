import Generate_tree as Tree
import sys
import os
import numpy as np
import csv
import matplotlib.pyplot as plt

def Load_tree_data(N,fn):
	
	starting_dir=os.getcwd()
	if os.path.exists(fn):
		os.chdir(fn)
	else: 
		print "TREE DOES NOT EXIST"
	
	Adj=np.loadtxt("Adjacence_matrix.csv",delimiter=",")
	Adj=Adj.astype(np.int)
	Num_of_children=np.loadtxt("Num_of_children.csv")
	Num_of_children=Num_of_children.astype(np.int)
	Levels=[]
	cr=csv.reader(open("Levels.csv", "rb"))
	for row in cr:
		Levels.append(map(int,row))
	
	Descendants,Descendants_ids=[],[]
	cr=csv.reader(open("Descendants_ids.csv", "rb"))
	for row in cr:
		Descendants.append(len(row))
		Descendants_ids.append(map(int,row))
	Descendants=np.array(Descendants)
	os.chdir(starting_dir)
	return Adj,Num_of_children,Levels,Descendants,Descendants_ids
	
def main(): 
	
	num_nodes=int(sys.argv[1])
	fn="Tree_N="+str(num_nodes)
	Adj,Num_of_children,Levels,Descendants,Descendants_ids=Load_tree_data(num_nodes,fn)

	Tree.Plot_tree(num_nodes,Adj,Levels,Num_of_children)
	Tree.Tree_statistics(num_nodes,Adj,Levels,Num_of_children)
		
	plt.show()

if __name__ == '__main__':
    main()
