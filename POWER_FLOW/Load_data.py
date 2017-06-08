from Graphs import Bus, Line, Electrical_network
import numpy as np
from scipy.sparse import coo_matrix, diags

# load Matpower format
def load_MATPOWER(filename):
	
	# load file
	f = open(filename, "r")
	text_lines = f.readlines()
	f.close()

	Busses = []
	Lines = []
	
	# incremented edge id
	eid = 0

	# incremented node id
	nid = 0	
	
	S_BASE = 0

	node_section = "mpc.bus ="
	gen_section = "mpc.gen ="
	edge_section = "mpc.branch ="
	end_section = "];"

	in_node_section = False
	in_gen_section = False
	in_edge_section = False
	
	# node name dictionary 
	node_name_dict = {}

	for l in text_lines:
		
		if l.startswith("mpc.baseMVA"):
			data = l.split()
			S_BASE = float(data[2][0:-1])
			
		if l.startswith(end_section):
			in_node_section = False
			in_gen_section = False
			in_edge_section = False
		
		if in_node_section:
			data = l.split()
			
			name = data[0]
			bus_type = int(data[1])
			final_voltage = float(data[7])

			# convert angles defined in degrees into radians
			angle = float(data[8])*np.pi/180
			
			# base voltage value in kV
			base_voltage = float(data[9])
			active_load = float(data[2])
			reactive_load = float(data[3])
			load = complex(active_load, reactive_load)

			# Generation is taken into account in the generation_section, 
			active_generation = 0.0
			reactive_generation = 0.0
			generation = complex(active_generation, reactive_generation)
			Q_max=0.0
			Q_min=0.0
			P_max=0.0
			P_min=0.0

			if bus_type > 1:
				init_voltage = 1. # The initial voltage is set in the generator section
			else:
				# for PQ bus, bus init voltage is set to 1
				bus_type=0				
				init_voltage = 1.
			
			sh_conductance = float(data[4])/S_BASE
			sh_susceptance = float(data[5])/S_BASE
			
			b = Bus(nid, name, bus_type, init_voltage, final_voltage, base_voltage, 
			                   angle, load, generation, Q_min, Q_max, P_min, 
			                   P_max, sh_conductance, sh_susceptance)
			Busses.append(b)
			# complete id -> node dictionary			
			node_name_dict[name] = b
			                   			
			# increment node id
			nid += 1

		elif in_gen_section:
			data = l.split()
			
			name = data[0]
			
			b = node_name_dict[name]
			
			active_generation = float(data[1])
			reactive_generation = float(data[2])
			generation = complex(active_generation, reactive_generation)

			b.generation = generation					

			b.init_voltage=float(data[5])
			b.Q_max=float(data[3])
			b.Q_min=float(data[4])
			b.P_max=float(data[8])
			b.P_min=float(data[9])

		elif in_edge_section:
			data = l.split()
			source_name = data[0]
			target_name = data[1]
			resistance = float(data[2]) 
			reactance =  float(data[3]) 
			admittance = 1./(resistance+reactance*1j)
			sh_susceptance = float(data[4]) 
			rtemp = float(data[8])
			phase_shift= float(data[9])*(np.pi/180)
			line_status = bool(int(data[10]))

			#normal lines, transformers and phase shifters
			if rtemp == 0. and phase_shift == 0.:
				line_type = 0
				s_ratio = 1.
			elif rtemp > 0.:
				line_type = 1
				s_ratio = (1./rtemp)*np.exp(-1j*phase_shift)
			else:
				line_type = 1
				s_ratio = 1.*np.exp(-1j*phase_shift)
			
			t_ratio = 1.

			edge = Line(eid, node_name_dict[source_name], node_name_dict[target_name], 
			           line_status, admittance, sh_susceptance, line_type, 
			           complex(s_ratio), complex(t_ratio), phase_shift)
			Lines.append(edge)
			# increment edge id
			eid += 1

		if l.startswith(node_section):
			in_node_section = True
		elif l.startswith(gen_section):
			in_gen_section = True
		elif l.startswith(edge_section):
			in_edge_section = True
	
	return Busses, Lines, S_BASE
