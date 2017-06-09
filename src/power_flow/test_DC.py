from Load_data import *
from NR_solver import *
from Graphs import Bus, Line
import numpy as np
import os

print("Testing DC-NR solver against MATPOWER testcases")

testcases = ["case14.m","case57.m","case89pegase.m","case118.m","case300.m",
			 "case1354pegase.m","case2869pegase.m","case9241pegase.m", 
			"case13659pegase.m"
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
	
	path_solved = os.path.join(solved_cases_dir,fn[:-2]+'.txt')
	Solved = np.loadtxt(path_solved)
	Vsolved, Tsolved = Solved[:,0], Solved[:,1]
	Tsolved -= Tsolved[slack_id]
	T -= T[slack_id]
	
	print("T, absolute error =", np.linalg.norm(T*180/np.pi-Tsolved,np.inf))
	print("Pslack", compute_P_DC(g, T)[slack_id])
	
	P_tab , Q_tab = g.Get_power()
	print("sum of tabulated powers", P_tab[np.delete(np.arange(0,len(busses)),slack_id)].sum())
