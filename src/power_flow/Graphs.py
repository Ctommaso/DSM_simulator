import numpy as np
from scipy.sparse import csr_matrix, lil_matrix, diags

class Bus():
	"""Electrical network bus """

	def __init__(self, bus_id, name, bus_type, init_voltage, final_voltage,
	                   base_voltage, angle, load, generation, Q_min, Q_max,
	                   P_min, P_max, sh_conductance, sh_susceptance):
		
		self.bus_id = bus_id #Int
		self.name = name #String
		self.bus_type = bus_type # 0:PQ, 1:Q \theta, 2: PV, 3: V\theta
		self.init_voltage = init_voltage #Float
		self.final_voltage = final_voltage #Float
		self.base_voltage = base_voltage # base voltage in KV
		self.angle = angle #Float
		self.load = load #Complex
		self.generation = generation #Complex
		self.Q_min = Q_min #Float
		self.Q_max = Q_max #Float
		self.P_min = P_min #Float
		self.P_max = P_max #Float
		self.sh_conductance = sh_conductance #Float
		self.sh_susceptance = sh_susceptance #Float

class Line():
	"""Electrical line"""
	
	def __init__(self, line_id, source, target, status, admittance, 
	                   sh_susceptance, line_type, s_ratio, t_ratio, 
	                   phase_shift):
						   
		self.line_id = line_id #Int
		self.source = source #Bus
		self.target = target #Bus
		self.status = status #Bool
		self.admittance = admittance #Complex Y = 1/Z  for Z = R + iX
		self.sh_susceptance = sh_susceptance #Float
		self.line_type = line_type
		self.s_ratio = s_ratio #Complex
		self.t_ratio = t_ratio #Complex
		self.phase_shift = phase_shift #In radians

class Electrical_network():
	"""Electrical Network: array of lines, array of busses, adjacency and admittance matrices"""
	
	def __init__(self, busses, lines, S_BASE):

		self.busses = busses
		self.lines = lines
		self.S_BASE = S_BASE
		self.Y = self.__YMatrix()
		self.A = self.__Get_Adjacency_matrix()
		self.L = self.__Get_Laplacian_matrix()

	def YMatrix(self):
		
		n = len(self.busses)
		Y = lil_matrix((n,n), dtype=complex)
		
		for l in self.lines:
			if l.status == True:
				y = l.admittance
				y_sh = l.sh_susceptance*1j
				Y[l.source.bus_id, l.source.bus_id] += pow(abs(l.s_ratio),2)*(y + y_sh/2) 
				Y[l.target.bus_id, l.target.bus_id] += pow(abs(l.t_ratio),2)*(y + y_sh/2)
				Y[l.source.bus_id, l.target.bus_id] += -y*np.conjugate(l.s_ratio)*l.t_ratio
				Y[l.target.bus_id, l.source.bus_id] += -y*np.conjugate(l.t_ratio)*l.s_ratio
		
		# add shunt susceptance to each node
		Y = Y.tocsr() + diags(np.array([bus.sh_conductance + bus.sh_susceptance*1j for bus in self.busses]))
		
		return Y
		
	__YMatrix = YMatrix
	
	def Get_Adjacency_matrix(self):
		
		n = len(self.busses)
		Y = (self.Y).copy()
		Y -= diags(Y.diagonal())
		row, col = Y.nonzero()
		A = csr_matrix((np.ones(len(row)),(row,col)), shape=(n,n))
		
		return A
	
	__Get_Adjacency_matrix = Get_Adjacency_matrix
	
	def Get_Laplacian_matrix(self):
		
		return diags(np.squeeze(np.asarray((self.A).sum(axis=0)))) - self.A
		
	__Get_Laplacian_matrix = Get_Laplacian_matrix 
	
	def Get_power(self):
		
		S = np.array([-b.load + b.generation for b in self.busses])
		return S.real, S.imag

	def YMatrix_DC(self):
		# Same approximations as in the Matpower DC power flow 
		
		n = len(self.busses)
		B_DC, G_DC = lil_matrix((n,n), dtype=complex), lil_matrix((n,n), dtype=complex)
		
		for l in self.lines:
			if l.status == True:
				# Only the reactance of the line is included y = 1/z for z = 1j*x, neglect r
				b = 1./(1j*((1./l.admittance).imag)) # 
				
				#cos(phase shift)  \approx 1
				B_DC[l.source.bus_id, l.target.bus_id] += -b*abs(np.conjugate(l.s_ratio)*l.t_ratio) 
				B_DC[l.target.bus_id, l.source.bus_id] += -b*abs(np.conjugate(l.t_ratio)*l.s_ratio)
				
				# 1j* sin(phase shift)  \approx 1j* sin(phase shift)
				G_DC[l.source.bus_id, l.target.bus_id] += -b*abs(np.conjugate(l.s_ratio)*l.t_ratio)*(l.phase_shift)*1j 
				G_DC[l.target.bus_id, l.source.bus_id] += -b*abs(np.conjugate(l.t_ratio)*l.s_ratio)*(-l.phase_shift)*1j
		
		# B_DC includes tap ratios, line shunt_susceptances are neglected
		# B_DC is really a weighted Laplacian matrix
		B_DC = B_DC.tocsr()
		B_DC = B_DC.imag
		B_DC = B_DC - diags( np.squeeze(np.asarray(B_DC.sum(axis=1))) )
		
		# dP is the adjustment to power injections which is due to phase shifters and real shunts
		G_DC = G_DC.real
		dP = np.squeeze(np.asarray(G_DC.sum(axis=1))) + np.array([bus.sh_conductance for bus in self.busses])
		return B_DC, dP


