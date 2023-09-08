import copy
import warnings
import pickle

import numpy as np
import pandas as pd

from pathlib import Path
from functools import wraps, cached_property
from collections.abc import Iterable

from graph_ts.structure.dyn_graph import *
from graph_ts.mapping.edge_function import *
from graph_ts.mapping.signal_function import SignalFunction
from graph_ts.structure.edge_id import *
from graph_ts.errors import *

# this is governed by verbose flag, so there is no log level 
def verbose_info(template):
    def parameterized(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            vinfo = fn(*args, **kwargs)
            if 'verbose' in kwargs:
                if kwargs['verbose']:
                    msg = ""
                    for item in vinfo:
                        if not isinstance(item, Iterable):
                            item = [item]
                        msg += f"{template.format(*item)}\n"
                    print(msg)
        return wrapper
    return parameterized

def obj_to_disk(folder):
    """
    Decorator function to save objects to disk and update instance attributes.
    This decorator allows methods to save objects to disk and update instance attributes based on certain conditions.
    Args:
        folder (str): The subfolder within the data_folder where objects will be saved.

    Returns:
        function: The decorated function that performs the object saving and attribute updating.

    """
    def parameterized(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get the instance and identifier (e.g., EdgeID or str) from the arguments
            instance = args[0]
            instance.clear_cache()
            filename, obj = fn(*args, **kwargs)
            
            # if there is a data folder specified, then replace the obj with it's file pickle
            to_save_flag = instance.data_folder is not None and isinstance(obj,(EdgeFunction, SignalFunction))
            if to_save_flag:
                full_path = instance.data_folder / folder / f"{filename}.pkl"
                with open(full_path, 'wb') as f:
                    pickle.dump(obj, f)
                    obj = full_path
                    
        return wrapper

    return parameterized

def upd_disk_graph(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = fn(*args, **kwargs)
        instance = args[0]
        instance.clear_cache()
        if instance.data_folder:
            instance.save_json(instance.data_folder)
        # if key is not None:  # TODO: check this is correct thing to do
        return key
    return wrapper

"""
DGCM Class Definition

This module defines the DGCM (Dynamic Graph Causal Model) class, which is used to construct, manipulate, and simulate causal models represented as dynamic graphs. The class allows users to assign edge functions and signal functions to model the relationships between nodes in the graph and simulate processes over time.

Attributes:
    DGCM.DEFAULT_GRPAH (str): Default filename for saving the graph structure as JSON.
    DGCM.DEFAULT_EDGE_FOLDER (str): Default subfolder name for storing edge functions.
    DGCM.DEFAULT_NODE_FOLDER (str): Default subfolder name for storing signal functions.

Classes:
    DGCM: Represents a Dynamic Graph Causal Model.

"""
class DGCM(DynGraph):
    """
    DGCM Class

    Represents a Dynamic Graph Causal Model (DGCM) used to construct, manipulate, and simulate causal models.

    Args:
        graph (dict, optional): A dictionary representing the initial graph structure.
        edge_functions (dict, optional): A dictionary of edge functions assigned to specific edges.
        signals (dict, optional): A dictionary of signal functions assigned to nodes.
        data_folder (str, optional): Path to the folder where data will be stored.
        collision_mode (str, optional): Specifies collision resolution mode for nodes.
        null_cause (EdgeFunction or str, optional): Edge function used as a null cause.
        null_signal (SignalFunction or str, optional): Signal function used as a null signal.

    Methods:
        assign_eid_with_fn(eid, func): Assigns an EdgeID with an edge function.
        assign_edge_with_fn(node_from, node_to, func, lag=0): Assigns an edge with an edge function.
        assign_edges(func_dict, lag=None): Assigns multiple edges with edge functions.
        assign_node_with_fn(node, func): Assigns a node with a signal function.
        assign_nodes(signal_dict): Assigns multiple nodes with signal functions.
        remove_node(node, force=False, verbose=False): Removes a node and related data.
        remove_edge(node_from, node_to, lag, force=False, verbose=False): Removes an edge and related data.
        simulate_process(T, mode='step', safe_mode=True, post_process=None, **params): Simulates a process over time.
        load_all_nodes(): Loads all signal functions from disk.
        load_all_edges(): Loads all edge functions from disk.
        null_edges(node_to=None, in_group=True): Returns null edges for a specific node or all nodes.
        from_path(path, cached_same=True): Creates a DGCM instance from a given path.

    Properties:
        edge_functions: Dictionary of assigned edge functions.
        signal_functions: Dictionary of assigned signal functions.

    """
    
    DEFAULT_GRPAH = "graph.json"
    DEFAULT_EDGE_FOLDER = "edge_funcs"
    DEFAULT_NODE_FOLDER = "signals"
    
    
    ################################################################
    #region construction
    
    def __init__(self, *args, edge_functions=None, signals=None, data_folder=None, null_cause=None, null_signal=None, **kwargs):  
        """
        Initialize DGCM instance with specified parameters.

        Args:
            graph (dict, optional): A dictionary representing the initial graph structure.
            edge_functions (dict, optional): A dictionary of edge functions assigned to specific edges.
            signals (dict, optional): A dictionary of signal functions assigned to nodes.
            data_folder (str, optional): Path to the folder where data will be stored.
            collision_mode (str, optional): Specifies collision resolution mode for nodes.
            null_cause (EdgeFunction or str, optional): Edge function used as a null cause.
            null_signal (SignalFunction or str, optional): Signal function used as a null signal.
        """
        if data_folder: 
            self.data_folder = Path(data_folder)
            ( self.data_folder / 'edge_funcs').mkdir(parents=True, exist_ok=True)
            ( self.data_folder / 'signals').mkdir(parents=True, exist_ok=True)
        else: 
            self.data_folder = None
            
        super(DGCM, self).__init__(*args, **kwargs) # !!!this will call the overridden add_edge
            
        self.__init_edges_functions(edge_functions, null_cause)
        self.__init_signals(signals, null_signal) 
        
        self._edge_cached = False # false case: structure is updated, functional forms are updated
    
    #endregion construction
    ################################################################
    
    
    
    ################################################################
    # region private methods
    @obj_to_disk(folder=DEFAULT_EDGE_FOLDER)
    def __init_edges_functions(self, edge_functions, null_cause=None):
        
        # handle null cause so it is a EdgeFunction
        if null_cause is None:
            null_cause = 'Identity'

        # null cause will be stored in the memory
        if type(null_cause) == str:
            self.null_cause = getattr(EdgeFunction, null_cause)()
        else: 
            self.null_cause = null_cause
            
        self._edge_fn = {}
                    
        self.assign_edges(edge_functions)
                
        return "null", self.null_cause
                
    @obj_to_disk(folder=DEFAULT_NODE_FOLDER)
    def __init_signals(self, signals, null_signal):
        if not null_signal:
            null_signal = 'Constant'
        
        if type(null_signal) == str:
            self.null_signal = getattr(SignalFunction, f"{null_signal}Signal")()
        else:
            self.null_signal = null_signal
        
        self._signals = {}
        self.assign_nodes(signals)
        
        return "null", self.null_signal
    
    @obj_to_disk(folder=DEFAULT_EDGE_FOLDER)
    def __assign_edge(self, eid, obj):
        if not self.has_edge_id(eid):
            raise EdgeNotExist(f"invalid EdgeID: {eid}")
        
        self._edge_fn[eid] = obj
        
        return eid.filename, obj
    
    @obj_to_disk(folder=DEFAULT_NODE_FOLDER)
    def __assign_node(self, node, obj):
        if not self.has_node(node):
            raise NodeNotExist(f"Node {node} doesn't exist.")
        
        self._signals[node] = obj
        
        return node, obj

    
    # TOOD: verbose replacement
    def __update_occp(self, eid: EdgeID, efindim=None):
        """
        Update edge occupancy information for a given EdgeID.

        This method updates the edge occupancy information for the specified EdgeID and its lag origins.
        The occupancy information is stored in the graph structure for efficient access.

        Args:
            eid (EdgeID): The EdgeID for which to update the occupancy information.
            efindim (Union[int, dict], optional): The input dimension(s) for the EdgeFunction associated with the EdgeID.

        """
        # Loop through each lag origin in the EdgeID
        for lag, origin in eid.lag_origins:
            # Update the occupancy information for the target node and lag
            self[origin][eid.target][lag]['occp'] = eid
            
            # Check if input dimension information is provided
            if efindim:
                # process the input dimension for the currect origin (or the only origin when the int is provided)
                if isinstance(efindim, int):
                    indim = efindim
                else:
                    indim = efindim[origin]
                    
                # Loop through each step within the input dimension (move ON along the history)
                for step in range(indim):
                    # Check if the graph has an edge between the origin and target nodes with the specified lag
                    if self.has_edge(origin, eid.target, lag - step):
                        # Update the occupancy information for the lag-affected edge 
                        if self[origin][eid.target][lag - step]['occp'] is None:
                            self[origin][eid.target][lag - step]['occp'] = eid

     
    @verbose_info(template="Edge from ({2}, {0}) to {1} is now a null cause")
    def __remove_occp(self, main_node, other_node=None, lag=None, verbose=False):
        arg_count = (other_node is not None) + (lag is not None)
        is_for_node = (arg_count  == 0)
        is_for_edge = (arg_count == 2)
        assert is_for_node or is_for_edge, "<inner logic T_T> wrong argument combination!"
        # delete the occupancies key for any edge involing node
        
        vinfo = []
        if is_for_node:
            for u, v, k, eid in self.edges(keys=True, data='occp'):
                if eid and eid.has_origin(main_node):
                    self[u][v][k]['occp'] = None
                    vinfo.append((u, v, k))
        
        if is_for_edge:
            eid = self[main_node][other_node][lag]['occp']
            if eid:
                for l, o in eid.lag_origins:
                    self[o][eid.target][l]['occp'] = None
                    vinfo.append((o, eid.target, l))
        
        return vinfo
    
    
    @verbose_info(template="Edge function deleted for {0}")
    def __clean_edge_fn(self, node_from, node_to=None, lag=None, verbose=False):
        assert (node_to is None and lag is None) or (node_to is not None and lag is not None)
        to_del = []
        for eid in self._edge_fn.keys():
            node_match = lag is None and (eid.has_origin(node_from) or eid.target==node_from)
            edge_match = lag is not None and (eid.has_pair((lag, node_from)) and eid.target==node_to)
            if node_match or edge_match:
                to_del.append(eid)
        
        for eid in to_del:
            del self._edge_fn[eid]
        return to_del
    
    def __get_null_edges(self, node_to, in_group=False):
        def null_occp(u, v, k):
            return v == node_to and self[u][node_to][k]['occp'] is None
        edges = nx.subgraph_view(self, filter_edge=null_occp).edges(keys=True)
        items = [(k, u) for (u, _, k) in edges]
    
        
        if not in_group:
            return [EdgeID(node_to, item) for item in items]
        else: 
            return EdgeID(node_to, *items)
        

    # endregion private methods
    ################################################################
    
    
    
    ##############################
    #region relation assingments

    def assign_eid_with_fn(self, eid, func):
        """
        Assigns an EdgeID with an edge function.

        Args:
            eid (EdgeID): The EdgeID to assign the edge function to.
            func (EdgeFunction): The edge function to assign.

        Raises:
            EdgeNotExist: If the provided EdgeID does not exist in the graph.

        Returns:
            str: File name of the assigned edge function.
        """
        self.__assign_edge(eid, func)    
        
    # def assign_eid_with_path(self, eid, epath):
    #     """
    #     Assigns an EdgeID with a path to an edge function file.

    #     Args:
    #         eid (EdgeID): The EdgeID to assign the edge function path to.
    #         epath (str): Path to the edge function file.
    #         lazy (bool, optional): Whether to lazily assign the edge function path.

    #     Raises:
    #         EdgeNotExist: If the provided EdgeID does not exist in the graph.

    #     Returns:
    #         None
    #     """
    #     self.__assign_edge(eid, epath, mode='path')
     
    # def assign_edge_with_path(self, node_from, node_to, path, lag=0):
    #     """
    #     Assigns an edge with a path to an edge function file.

    #     Args:
    #         node_from (str): Source node of the edge.
    #         node_to (str): Target node of the edge.
    #         path (str): Path to the edge function file.
    #         lag (int, optional): Lag value of the edge.

    #     Returns:
    #         None
    #     """
    #     eid = EdgeID(node_to, (lag, node_from))
    #     self.assign_eid_with_path(eid, path)
    
    def assign_edge_with_fn(self, node_from, node_to, func, lag=0):
        """
        Assigns an edge with an edge function.

        Args:
            node_from (str): Source node of the edge.
            node_to (str): Target node of the edge.
            func (EdgeFunction): The edge function to assign.
            lag (int, optional): Lag value of the edge.

        Returns:
            None
        """
        eid = EdgeID(node_to, (lag, node_from))
        self.assign_eid_with_fn(eid, func)
             
    def assign_edges(self, func_dict, lag=None):
        """
        Assigns multiple edges with edge functions.

        Args:
            func_dict (dict): A dictionary where keys are EdgeIDs or edge tuples, and values are edge functions or paths.
            lag (int, optional): Lag value for assigning edge functions.

        Raises:
            ValueError: If the provided relation type is not valid.

        Returns:
            None
        """
        if not func_dict:
            return 
        assert all(type(next(iter(func_dict.keys()))) == type(k) for k in func_dict.keys()), "All keys should be the same type"
        
        # if lag is not speicified, assume user gives eid as keys
        if lag is None:
            for eid, relation in func_dict.items():
                try:
                    if isinstance(relation, (EdgeFunction, Path, str)):
                        self.assign_eid_with_fn(eid, relation)
                    else: 
                        raise ValueError(f"relation of type {type(relation)} is not valid")
                except EdgeNotExist as e:
                    warnings.warn(f"edge with {eid} was skipped for: {type(e)}: {e}", UserWarning)
        
        # if there is a lag, assume user use single edge with lag
        else:
            for edge, relation in func_dict.items():
                try: 
                    if isinstance(relation, (EdgeFunction, Path, str)):
                        self.assign_edge_with_fn(*edge, relation, lag=lag)
                    else: 
                        raise ValueError(f"relation of type {type(relation)} is not valid")
                except Exception as e:
                    warnings.warn(f"{edge} was skipped for: {e}", UserWarning)
  
    #endregion relation assingments
    ##############################
    
    
    
    #######################################
    #region independent signal assignments
    
    def assign_node_with_fn(self, node, func):
        """
        Assigns a node with a signal function.

        Args:
            node (str): The node to assign the signal function to.
            func (SignalFunction): The signal function to assign.

        Raises:
            NodeNotExist: If the provided node does not exist in the graph.

        Returns:
            str: File name of the assigned signal function.
        """
        self.__assign_node(node, func)
        
    def assign_nodes(self, signal_dict):
        """
        Assigns multiple nodes with signal functions.

        Args:
            signal_dict (dict): A dictionary where keys are nodes, and values are signal functions or paths.

        Raises:
            ValueError: If the provided signal function type is not valid.

        Returns:
            None
        """
        if signal_dict is None:
            return
        for node, signal in signal_dict.items():
            try: 
                if isinstance(signal, (str, Path, SignalFunction)):
                    self.assign_node_with_fn(node, signal)
                else: 
                    raise ValueError(f"signal function of type {type(signal)} is invalid")
            except Exception as e:
                warnings.warn(f"{node} was skipped for: {e}", UserWarning)
    
    #endregion independent signal assinments
    #######################################
    
    
    
    ########################################################
    #region overriding add node / edge
    
    @upd_disk_graph
    def add_node(self, node, **attr):
        super().add_node(node, **attr)
       
    @upd_disk_graph     
    def add_edge(self, node_from, node_to, lag=0, **attr):
        key = super().add_edge(node_from, node_to, lag, occp=None, **attr) # new
        return key
    
    @upd_disk_graph
    def remove_node(self, node, force=False, verbose=False):
        """
        Removes a node and related data from the graph.

        Args:
            node (str): The node to remove.
            force (bool, optional): Whether to forcefully remove edge functions related to the node.
            verbose (bool, optional): Whether to display verbose information.

        Returns:
            None
        """
        # force is for deciding whether to delete information from the disk
        # check multi function related to this node
        if force:  #TODO 
            raise NotImplementedError
        
        super().remove_node(node)
        
        self.__remove_occp(node, verbose=verbose)

        self.__clean_edge_fn(node, verbose=verbose)
        
            
        # delete the inhabitant signal for a node
        if node in self._signals:
            del self._signals[node]
            
    @upd_disk_graph   
    def remove_edge(self, node_from, node_to, lag, force=False, verbose=False):
        """
        Removes an edge and related data from the graph.

        Args:
            node_from (str): Source node of the edge.
            node_to (str): Target node of the edge.
            lag (int): Lag value of the edge.
            force (bool, optional): Whether to forcefully remove edge functions related to the edge.
            verbose (bool, optional): Whether to display verbose information.

        Returns:
            None
        """
        if force:  #TODO 
            raise NotImplementedError
        super().remove_edge(node_from, node_to, lag)
        
        self.__remove_occp(node_from, node_to, lag, verbose=verbose) 
        
        self.__clean_edge_fn(node_from, node_to, lag, verbose=verbose)
        
    #endregion overriding add node / edge
    ########################################################
    
    
    
    #####################
    # region properties
    @property
    def edge_functions(self):
        return copy.deepcopy(self._edge_fn)
    
    @property
    def signal_functions(self):
        return copy.deepcopy(self._signals)
    
    def clear_cache(self):
        self._edge_cached = False
        self._efs = None
        self._eids_for_node = None
        self._pre_len = None
    
    @property
    def is_edge_cached(self):
        return self._edge_cached
    
    def null_edges(self, node_to=None, in_group=True):
        self.load_all_edges()
        if node_to:
            return self.__get_null_edges(node_to, in_group)
        else: 
            result = {}
            for node in self.nodes:
                result[node] = self.__get_null_edges(node, in_group)
            return result
      
    def eids_with_node(self, node):
        incoming_eid = []
        outgoing_eid = []
        for eid in self._edge_fn:
            if eid.target == node:
                incoming_eid.append(eid)
            if node in list(zip(*eid.lag_origins))[1]:
                outgoing_eid.append(eid)
        return incoming_eid, outgoing_eid
    
    def load_all_nodes(self):
        """
        Loads all signal functions from disk to the RAM.

        Returns:
            dict: A dictionary of loaded signal functions, where keys are node names and values are signal functions.
        """
        sfs = {}
        for node in self.nodes:
            if node in self._signals:
                temp_sf = self._signals[node]
                if isinstance(temp_sf, SignalFunction):
                    sf = temp_sf
                else:
                    with open(temp_sf, 'rb') as f:
                        sf = pickle.load(f)
                        if not isinstance(sf, SignalFunction):
                            raise NotASignalFunctionError(f"Function for {node} should be a SignalFunction, got {type(sf)}")
                sfs[node] = sf
        return sfs
     
    def load_all_edges(self):
        """
        Loads all edge functions from disk to a memory (in return).

        This method loads edge functions from disk for each EdgeID in the graph,
        ensuring that they are stored in memory for efficient access during simulations.

        Returns:
            tuple: A tuple containing three elements:
                   - A dictionary of loaded edge functions, where keys are EdgeIDs and values are edge functions.
                   - A dictionary of lists of EdgeIDs for each target node.
                   - The maximum lag value among all edge functions.

        Raises:
            NotAEdgeFunctionError: If a loaded object is not an instance of EdgeFunction.
            AssertionError: If the loaded EdgeFunction does not match the specified EdgeID.
        """
        
        ### 1. init for returns 
        self.clear_cache()
        # Create a dictionary to store the list of EdgeIDs associated with each target node
        self._eids_for_node = {node: [] for node in self.nodes}
        # Initialize the minimum lag value as a prepending length during the simulation
        self._pre_len = 1 
        # Create a dictionary to store the loaded edge functions for return
        self._efs = {}
        
        ### 2. Each edge id should be related to ONE and ONLY ONE edge function 
        for eid, temp_ef in self._edge_fn.items():
            ## 2.0 Update the minimum lag value based on the maximum lag in the EdgeID
            self._pre_len = max(self._pre_len, eid.max_lag)
            
            ## 2.1 load the edge function
            if isinstance(temp_ef, EdgeFunction): 
            # when the edge function is already stored in the memory 
                ef = temp_ef
                
            else:
            # when the edge function should be read from the disk                             
                with open(temp_ef, 'rb') as f:
                    ef = pickle.load(f)
                    # Raise an error if the loaded object is not an instance of EdgeFunction
                    if not isinstance(ef, EdgeFunction):
                        raise NotAEdgeFunctionError(f"Function for edge with id: {eid} should be an EdgeFunction, got {type(ef)}")

            ## 2.2 do something with the loaded object
            # Check if the loaded EdgeFunction matches the specified EdgeID
            assert ef.match_with(eid), f"Edge function with in dimension(s) {ef.indim} does not match the edge group {eid}"

            # Determine the input dimension of the EdgeFunction, this should be a dict for slicing the history
            efindim = ef.indim if isinstance(ef.indim, dict) else {eid.lag_origins[0][1]: ef.indim}
            # Update occupancy information for the EdgeID if necessary (this should change the occupancy info only when there are edge function stored as a path)
            self.__update_occp(eid, efindim)

            # Store the loaded EdgeFunction in the dictionary of edge functions
            self._efs[eid] = ef
            # Append the EdgeID to the list of EdgeIDs associated with the target node
            self._eids_for_node[eid.target].append(eid)
            

        # Append null edges
        warned = False
        # Loop through nodes to find incoming edges with null occupancy
        for v in self.nodes:
            for u, _, lag, eid in self.in_edges(v, data='occp', keys=True):
                if not eid:
                    # Create an EdgeID for null occupancy edges
                    eid = EdgeID(v, (lag, u))
                    # Update the minimum lag value
                    self._pre_len = max(self._pre_len, lag)
                    # Display a warning if null occupancy edges are found
                    if not warned:
                        warnings.warn(f"there are null edges, use `DGCM.null_edges()` to check them")
                        warned = True
                    # Append the EdgeID to the list of EdgeIDs associated with the target node
                    self._eids_for_node[v].append(eid)

        self._edge_cached = True
        # Return the loaded edge functions, list of EdgeIDs, and the maximum lag value

    # endregion
    #####################
    
    
    
    #####################
    #region Generation

    def simulate_process(self, T, safe_mode=True, post_process=None):
        # load signal functions from disk
        sfs = self.load_all_nodes()
        
        # load edge functions from disk
        if not self._edge_cached:
            self.load_all_edges()
            
        static_order = self.static_order()
        return self._step_based_generation(T, sfs, self._efs, self._eids_for_node, self._pre_len, static_order, safe_mode=safe_mode, post_process=post_process)
          
    def _step_based_generation(self, 
                               T, 
                               sfs, 
                               efs, 
                               eids_for_node, 
                               pre_len, 
                               static_order, 
                               safe_mode=True, 
                               noisy_signal=False, 
                               noisy_edge=False, 
                               full_offset=True,
                               post_process=None):
        
        if post_process is not None:
            add_len = 0
            for _, config in post_process.items():
                if 'window' in config['params']:
                    add_len = max(add_len, config['params']['window'])
            pre_len += add_len
            
        # initialize the result
        Tp = pre_len + T
        data_raw = {k: np.zeros(Tp) for k in self.nodes}
        
        # generate independent signals
        for node in self.nodes:
            sfunc = sfs[node] if node in sfs else self.null_signal
            if full_offset or self.in_degree(node) == 0:
                data_raw[node] += sfunc(Tp, with_noise=noisy_signal)
            else:
                data_raw[node][:pre_len] = sfunc(pre_len, with_noise=noisy_signal)
                    

        # generate causal part of the signal
        for t in range(pre_len, Tp): 
            
            for node in static_order:
                for eid in eids_for_node[node]:
                    edge_func = efs[eid] if eid in efs else self.null_cause
                        
                    in_dim = edge_func.indim
                    out_dim = edge_func.outdim
                
                    args = {}
                    for lag, parent in eid.lag_origins:
                        if not isinstance(in_dim, int):
                            cur_indim = in_dim[parent]
                        else:
                            cur_indim = in_dim
                            
                        # !!! if instantaneous, then we don't take any history
                        if lag == 0:
                            if cur_indim > 1:
                                if safe_mode:
                                    raise ValueError("Tried to get information from the future")
                            in_a, in_b = t, t+1
                            
                        else:
                            in_a, in_b = t-lag, t-lag+cur_indim
                        
                            if in_b > t:
                                # TODO: better information
                                if safe_mode:
                                    raise ValueError("Tried to get information from the future")
                                else:
                                    in_b = t
                        
                        pad_len = max(0, cur_indim - in_b + in_a)
                        piece = np.pad(data_raw[parent][in_a: in_b], (0, pad_len))
                        # if piece.shape[0] != in_dim[node_from]:
                        #     print(t, pad_len, in_a, in_b, node_from, cur_indim, piece.shape[0], data_raw[node_from][in_a: in_b].shape[0])
                        args[parent] = piece

                    out_a, out_b = t, min(t+out_dim, Tp)
                    result = edge_func(**args, with_noise=noisy_edge)
                    if edge_func.replace:
                        data_raw[node][out_a: out_b] = result[:out_b - out_a]
                    else:
                        data_raw[node][out_a: out_b] += result[:out_b - out_a]
            

        episode = pd.DataFrame(data_raw)
        
        
        if post_process is not None:
            for key, config in post_process.items():
                if config['mode'] == 'rolling_mean':
                    pp_params = config['params']
                    episode[key] = episode[key].rolling(**pp_params).mean()
                else: 
                    raise NotImplementedError("oops!")
        
        return episode[pre_len:].reset_index(drop=True)

    #endregion generalization
    #####################



    ########################
    #region static methods
                            
    @classmethod
    def from_path(cls, path, cached_same=True, mode='out'):
        my_path = Path(path)
        with open(my_path / DGCM.DEFAULT_GRPAH, 'r') as f:
            graph = json.load(f)
        
        edge_funcs = {}
        null_cause = None
        for ef in Path(my_path / DGCM.DEFAULT_EDGE_FOLDER).glob('*.pkl'):
            stem = Path(ef).stem
            if stem == "null":
                with open(ef, 'rb') as f:
                    null_cause = pickle.load(f)
            else:
                eid = EdgeID.from_string(stem)
                edge_funcs[eid] = ef
        
        signal_funcs = {}
        null_signal = None
        for sf in Path(my_path / DGCM.DEFAULT_NODE_FOLDER).glob('*.pkl'):
            stem = Path(sf).stem
            if stem == "null":
                with open(sf, 'rb') as f:
                    null_signal = pickle.load(f)
            else: 
                signal_funcs[stem] = sf
        
        if cached_same:
            cache_path = path
        else:
            cache_path = "./cache"
            
        params = dict(
            edge_functions=edge_funcs, 
            signals=signal_funcs, 
            data_folder=cache_path,
            null_cause=null_cause, 
            null_signal=null_signal
            )
        
        if mode == "out":
            params['out_graph'] = graph
        if mode == "in":
            params['in_graph'] = graph
        return cls(**params)
                   

            
    #endregion static methods
    ########################
    
  