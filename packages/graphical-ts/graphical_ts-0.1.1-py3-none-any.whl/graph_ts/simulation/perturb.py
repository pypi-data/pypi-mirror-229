from ..structure.edge_id import *
from ..mapping.signal_function import *
from ..simulation.dgcm import *
from ..simulation.random_mlp import *
import yaml
import json
from copy import deepcopy


# TODO: post processing in node data
class PatientSampler(DGCM):
    
    ## TODO: this out graph and in graph shit.
    def __init__(self, out_graph=None, in_graph=None, config_path=None, rng=None, *args, **kwargs):
        self._is_init = False
        
        
        self._info = None # get something like  {v: {'C': int, 'offset': }, }, indim: int, hdim:int}  lag_window: int
        if config_path is not None:
            out_graph = self.read_config(config_path) 
        
        
        super(PatientSampler, self).__init__(out_graph=out_graph, in_graph=in_graph, *args, **kwargs)
        
        if self._info is not None:
            # random gaussian noise generator
            if isinstance(rng, int):
                self.rng = np.random.default_rng(rng)
            elif rng is not None: 
                self.rng = rng
            else:
                self.rng = np.random.default_rng()
            
            edge_funcs = {}
            signal_funcs = {}
            self.eid_lookup = {}
            hdim = int(self._info['hdim'])
            indim = int(self._info['indim'])
            
            for v in self.nodes:
                
                node_info = self._info['node'][v]
                
                is_discrete = node_info['is_discrete']
                if not is_discrete:
                    Cu, Cl = node_info['bound']
                    offset = node_info.setdefault('offset', (Cu+Cl)//2)
                    
                    efunc = RandomMLP(v, self.nodes, indim, Cu, Cl, offset, hdim)
                    sfunc = SignalFunction.ConstantSignal(offset)
                else:
                    values = node_info['values']
                    
                    efunc = RandomDiscreteMLP(v, self.nodes, indim, values, hdim)
                    sfunc = DiscreteSignal.UniformDiscrete(values)
                
                if self.in_degree(v) != 0:
                    eid = EdgeID.from_in_edges(self.in_edges(v, keys=True))
                    edge_funcs[eid] = efunc
                    self.eid_lookup[v] = eid
                    
                signal_funcs[v] = sfunc
                

            self.assign_edges(edge_funcs)
            self.assign_nodes(signal_funcs)
            self._is_init = True
            

    def simulate_perturb(self, T, n_max=5, pgv=None, *args, **kwargs):
        assert self._is_init, "Simulation not initialized!"
        pgv = self.perturb(n_max) if pgv is None else pgv
        
        efs, eids_for_nodes, pre_len = self.infer_from_view(pgv)
        sfs = deepcopy(self._signals)
        traverse_order = pgv.static_order()
        
        data = self._step_based_generation(T, sfs, efs, eids_for_nodes, pre_len, traverse_order, 
                                           safe_mode=False, 
                                           noisy_signal=True, 
                                           full_offset=False,
                                           post_process=self.post_process,)
        return data, pgv
        

    def perturb(self, n_max, n_min=0):
        assert self._is_init, "Simulation not initialized!"
        E = self.number_of_edges()
        
        N_op = self.rng.integers(n_min, n_max+1, 1)[0]
        if N_op > E//2:
            warnings.warn("Too many edges will be removed, using E//2 steps perturbation")
            N_op = E//2
        N_add = self.rng.binomial(N_op, 0.5)
        N_rm = N_op - N_add
        
        keep_idc = self.rng.choice(range(E), E-N_rm, replace=False)
        
        pgv = DynGraph()
        # print(len(keep_idc), self.number_of_edges())
        for i, e in enumerate(self.edges):
            if i not in keep_idc:
                continue
            u, v, lag = e
            if lag == 0: # don't mess around with instantaneous
                pgv.add_edge(u, v, lag)
            else:
                lag_diff = self.rng.binomial(self.lag_window, 0.5) - self.lag_window // 2
                new_lag = max(lag + lag_diff, 1) # 
                pgv.add_edge(u, v, new_lag)
                done = True
                # print(f"edge lag from {u} to {v} changes from {lag} to {new_lag}.")
        
        # print("starting to add edges")
        for i in range(N_add):
            done = False
            while not done:
                try:
                    u, v = self.rng.choice(list(self.nodes), 2, replace=False)
                    if self.in_degree(v) != 0: # don't add new edge to source
                        lag = self.rng.binomial(self.lag_window, 0.5)
                        pgv.add_edge(u, v, lag)
                        done = True
                        # print(f"new edge added from {u} to {v} with lag {lag}")
                except ValueError as e:
                    continue
                
        return pgv
    
        
    def infer_from_view(self, pgv):
        assert self._is_init, "Simulation not initialized!"
        pre_len = 1 
        efs = {}
        eids_for_node = {}
        for v in self.nodes:
            in_edges = self.in_edges(v, keys=True)
            if len(in_edges) == 0: 
                eids_for_node[v] = []
                continue
            new_eid = EdgeID.from_in_edges(in_edges)
            pre_len = max(pre_len, new_eid.max_lag)
            
            efs[new_eid] = self._edge_fn[self.eid_lookup[v]]
            eids_for_node[v] = [new_eid]
            
        return efs, eids_for_node, pre_len
        
        
    def read_config(self, path):
        with open(path, 'r') as f:
            self._info = yaml.load(f, Loader=yaml.FullLoader)
        self.lag_window = int(self._info["lag_window"])
        
        self.post_process = {v: self._info['node'][v]['post_process'] for v in self._info['node'] if 'post_process' in self._info['node'][v]}
        self.post_process = {v: config for v, config in self.post_process.items() if config is not None}
        
        for v, config in self.post_process.items():
            if config['mode'] == 'rolling_mean':
                self.post_process[v]['params'] = {'window': self._info['indim']}
        
        with open(self._info['graph_path'], 'r') as f:
            graph = json.load(f)
        graph = {key1: {int(key2): value2 for key2, value2 in value1.items()} for key1, value1 in graph.items()}
        return graph
    
    