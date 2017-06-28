from Load_data import *
from NR_solver import *
import numpy as np
from scipy.sparse import linalg
import os

print("Testing NR solver against MATPOWER testcases")

testcases = ["case14.txt","case57.txt","case89pegase.txt","case118.txt","case300.txt",
			 "case1354pegase.txt","case2869pegase.txt","case9241pegase.txt", 
			#"case13659pegase.txt" #Only converges with the hot start
			]

testcase_dir = "MATPOWER"
solved_cases_dir = "tests/AC"
solved_cases_fn = "solved_matpower_cases.txt"

Sol = np.loadtxt(os.path.join(solved_cases_dir,solved_cases_fn))

for fn in testcases:
	print("*****", fn ,"*****")
	path = os.path.join(testcase_dir,fn)
	path_solved = os.path.join(solved_cases_dir,fn)
	
	busses, lines ,S_BASE = load_MATPOWER(path)
	g = Electrical_network(busses, lines, S_BASE)
	
	slack_id = filter(lambda v: v.bus_type==3 , g.busses)[0].bus_id
	T, V = NR_solver(g,1e-10,15)
	P, Q = compute_S(g,T,V)	
	
	P_slack_solved = Sol[testcases.index(fn)]
	Solved = np.loadtxt(path_solved)
	Vsolved, Tsolved = Solved[:,0], Solved[:,1]
	
	T -= T[slack_id]
	Tsolved -= Tsolved[slack_id]
	
	print("Losses ", P.sum())
	print("Slack P,    error =", P[slack_id]-P_slack_solved)
	print("T, absolute error =", np.linalg.norm(T*180/np.pi-Tsolved,np.inf))
	print("V, absolute error =", np.linalg.norm(V-Vsolved,np.inf))
