from Load_data import *
from NR_solver import *
from Graphs import Bus, Line
import numpy as np
import os

print("Testing DC-NR solver against MATPOWER testcases")

testcases = ["case14.txt","case57.txt","case89pegase.txt","case118.txt","case300.txt",
			 "case1354pegase.txt","case2869pegase.txt","case9241pegase.txt", 
			"case13659pegase.txt"
			]


testcase_dir = "MATPOWER"
solved_cases_dir = "tests/DC"

for fn in testcases:
	print("*****", fn ,"*****")
	path = os.path.join(testcase_dir,fn)
		
	busses, lines, S_BASE = load_MATPOWER(path)
	
	
	g = Electrical_network(busses, lines, S_BASE)	
	T, V = NR_solver_DC(g)
	
		
	vs = g.busses
	slack_id = filter(lambda v: v.bus_type==3, vs)[0].bus_id
	
	path_solved = os.path.join(solved_cases_dir,fn)
	Solved = np.loadtxt(path_solved)
	Vsolved, Tsolved = Solved[:,0], Solved[:,1]
	Tsolved -= Tsolved[slack_id]
	T -= T[slack_id]
	
	print("T, absolute error =", np.linalg.norm(T*180/np.pi-Tsolved,np.inf))
	print("Pslack", compute_P_DC(g, T)[slack_id])
	
	P_tab , Q_tab = g.Get_power()
	print("sum of tabulated powers", P_tab[np.delete(np.arange(0,len(busses)),slack_id)].sum())
