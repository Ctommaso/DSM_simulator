import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, linalg, hstack, vstack, diags
import time


def NR_solver(g,epsilon,iter_max):
		
	vs = g.busses
	n = len(vs) 
	
	# node ids whose bus type is 0
	PQ_ids = [v.bus_id for v in filter(lambda v: v.bus_type == 0, vs)]
	
	# compute B and G matrices
	Y = g.Y
	B = Y.imag
	G = Y.real
	
	# adjacency of graph
	A = g.A
	slack_id = filter(lambda v: v.bus_type == 3, vs)[0].bus_id
	# ids from 1:n except slack_id
	ids = [i for i in range(0,n)]
	del ids[slack_id]
	
	error  = epsilon
	n_iter = 1

	S_BASE = g.S_BASE
	
	V = np.array([v.init_voltage for v in vs])
	T = np.zeros(n) # Flat start
	
	# Hot start! Start NR with tabulated voltages and angles 
	#V = np.array([v.final_voltage for v in vs])
	#T = np.array([v.angle for v in vs])
	P_tab, Q_tab = g.Get_power()
	P_tab = P_tab/S_BASE
	Q_tab = Q_tab/S_BASE

	start = time.time()
	
	while(error >= epsilon and n_iter < iter_max):
				
		# pre-computations 1
		from_bus, to_bus = A.nonzero()
		delta = T[from_bus]-T[to_bus]
		Ms = csr_matrix((np.sin(delta),(from_bus,to_bus)),shape = (n,n))
		Mc = csr_matrix((np.cos(delta),(from_bus,to_bus)),shape = (n,n)) + diags(np.ones(n))
		
		Mvs = (csr_matrix(V[:,np.newaxis]).multiply(Ms)).multiply(csr_matrix(V))
		Mvc = (csr_matrix(V[:,np.newaxis]).multiply(Mc)).multiply(csr_matrix(V))
		
		V2 = V*V
		
		# compute P and Q (n-dimensional vectors)	
		P = (G.multiply(Mvc) + B.multiply(Mvs)).sum(axis=1)
		Q = (G.multiply(Mvs) - B.multiply(Mvc)).sum(axis=1)
		P = np.squeeze(np.asarray(P))
		Q = np.squeeze(np.asarray(Q))
		
		# compare P and Q with their "known" value to get dPQ ((n-1+m)-dimensional vector)
		dP = P_tab[ids] - P[ids]
		dQ = Q_tab[PQ_ids] - Q[PQ_ids]
		dPQ = np.concatenate((dP,dQ))
		
		# compute the jacobian matrix
		# see Power System Analysis, Bergen/Vital, p345-347
		L = G.multiply(Mvs) - B.multiply(Mvc) + diags(-Q)
		N = (G.multiply(Mc) + B.multiply(Ms)).multiply(csr_matrix(V[:,np.newaxis])) + diags(P/V)
		M = -B.multiply(Mvs) - G.multiply(Mvc) + diags(P)
		O = (G.multiply(Ms) - B.multiply(Mc)).multiply(csr_matrix(V[:,np.newaxis])) + diags(Q/V)
		
		L = L[ids][:,ids]
		N = N[ids][:,PQ_ids]
		M = M[PQ_ids][:,ids]
		O = O[PQ_ids][:,PQ_ids]
		
		#J = [L N;M O]
		J = vstack( (hstack((L, N)), hstack((M, O))) ,'csr')

		# solve JX = dPQ (sparse)
		X = linalg.spsolve(J, dPQ)
		
		# update V and theta
		T[ids] += X[0:n-1]
		V[PQ_ids] += X[n-1:]
		error = np.linalg.norm(dPQ,np.inf)
		n_iter += 1
		#print("error ", error)
	end = time.time()
	"""
	print( "Elapsed time", end - start, " n_iter ", n_iter)
	if error < epsilon:
		print('Converged -- error ', error)
	else:
		print "PROBLEM"
	"""
	if error > epsilon:
		print('CONVERGENCE PROBLEM')
	return T, V

def compute_S(g,T,V):
	
	n=len(T)
	# Extract B and G matrices
	Y = g.Y
	B = Y.imag
	G = Y.real
	A = g.A
	
	from_bus, to_bus = A.nonzero()
	delta = T[from_bus]-T[to_bus]
	Ms = csr_matrix((np.sin(delta),(from_bus,to_bus)),shape = (n,n))
	Mc = csr_matrix((np.cos(delta),(from_bus,to_bus)),shape = (n,n)) + diags(np.ones(n))
	
	Mvs = (csr_matrix(V[:,np.newaxis]).multiply(Ms)).multiply(csr_matrix(V))
	Mvc = (csr_matrix(V[:,np.newaxis]).multiply(Mc)).multiply(csr_matrix(V))
		
	P = (G.multiply(Mvc) + B.multiply(Mvs)).sum(axis=1)
	Q = (G.multiply(Mvs) - B.multiply(Mvc)).sum(axis=1)
	P = np.squeeze(np.asarray(P))
	Q = np.squeeze(np.asarray(Q))
	
	S_BASE = g.S_BASE
	
	return P*S_BASE, Q*S_BASE

def NR_solver_DC(g):
		
	vs = g.busses
	n = len(vs) 
	
	# compute B_DC matrix adapted for DC power flow, it is a real Laplacian matrix  
	# and the adjustment to power injections: dP due to phase shifters and real shunts
	B_DC, dP = g.YMatrix_DC()

	slack_id = filter(lambda v: v.bus_type == 3, vs)[0].bus_id
	ids = [i for i in range(0,n)]
	del ids[slack_id]
	
	# Tabulated power injections
	S_BASE = g.S_BASE
	P_tab, Q_tab = g.Get_power()
	P_tab = P_tab/S_BASE

	T = np.zeros(n)	
	# Solve P = -B_DC * T + dP
	X = linalg.spsolve(-B_DC[ids][:,ids], P_tab[ids] - dP[ids])
	T[ids] = X
	V = np.ones(n)
	
	return T, V
	
def compute_P_DC(g,T):
	
	n=len(T)
	
	# compute B_DC matrix adapted for DC power flow,  
	# and the adjustment to power injections: dP due to phase shifters and real shunts
	B_DC, dP = g.YMatrix_DC()
	
	# Solve P = -B_DC * T + dP			
	P = -B_DC.dot(T) + dP
	S_BASE = g.S_BASE

	return P*S_BASE
