from ..mapping.edge_function import *

AUTO_REG_RATIO = 0.8

def glb_normlize(vec):
    return vec / (np.linalg.norm(vec)+0.001)

class RandomMLP(EdgeFunction):
    def __init__(self, target, parents, L, C_u=None, C_l=None, offset=None, h=16, **kwargs):
        self.is_discrete = False
        self.l = L
        self.target = target
        indim = {v: self.l for v in parents}
        super(RandomMLP, self).__init__(None, indim=indim, **kwargs)
        
        # switch cases for setting or calculating a base value for target
        ### this will make sure offset is not None because [continuous values should always be specified ranges TODO: make sure this] 
        if offset is None and C_l is not None and C_u is not None: 
            self.offset = (C_u + C_l) // 2
        else: 
            self.offset = offset # continuous: a value, discrete case: None
            
        # range of target varible (None if discrete)
        self.Cu = C_u
        self.Cl = C_l
        
        # number of parents
        self.v = len(parents)
        
        # mapping noise, gaussian
        self.gauss_loc = 0
        self.gauss_scl = self.offset * 0.01 if self.offset is not None else 1
        
        self.h = h
        self.mat, self.w = self.__generate_mat()
        
        self.var_idx = {v: i for v, i in zip(parents, range(self.v))}
        self.vars = [v for v in parents]

        
    def regenerate_mlp(self):
        self.mat, self.w = self.__generate_mat()
        
        
    def __generate_mat(self):
        # Step 1: Generate a random matrix
        A = self.rng.standard_normal((self.h, self.v*self.l))
        
        # Step 2: Compute its SVD
        U, s, Vh = np.linalg.svd(A, full_matrices=False)

        # Step 3: Scale its singular values
        s_max = s[0]
        s = s / s_max
        
        # Step 4: Reconstruct the matrix using the scaled singular values
        mat = U @ np.diag(s) @ Vh
        
        w = self.rng.standard_normal(self.h)
        w = glb_normlize(w)
        return mat.reshape((self.h, self.l, self.v)), w
        
        
    def __call__(self, with_noise=False, **kwargs):
        
        # step 1: costruct indices to query the submatrix
        alien_idc = []
        slices = []
        for node, slice in kwargs.items():
            if node != self.target and not self.is_discrete: # self effect will take effect afterwards
                ind = self.var_idx[node]
                alien_idc.append(ind)
                slices.append(slice)
        alien_idc.sort()
        
        # calculate the alien effect using a mlp
        
        ### slicing the 1st layer matrix
        sub_mat = self.mat[:, :, alien_idc].reshape((self.h, -1)) 
        ### turn the input into a matirx
        alien_vec = np.vstack(slices) # !!! for discrete case, this is not completely alient
        norms = np.linalg.norm(alien_vec, axis=1, keepdims=True)
        alien_vec = alien_vec / (norms+0.001)

        ### calculate the 1st layer 
        alien_eff = sub_mat@(alien_vec.reshape(-1))
        # alien_eff = glb_normlize(alien_eff)
        
        # ### nonlinearity
        alien_eff = (alien_eff >= 0) * alien_eff
        
        alien_eff = self.w@alien_eff
        
        
        ### if self effect exist and continuous, use history average as an offset
        if self.target in kwargs.keys() and not self.is_discrete:
            ego_eff = np.mean(kwargs[self.target])
        else:
            ego_eff = self.offset
            
        # construct result by adding alien effect and ego effect
        if ego_eff is None: # that means it is discrete
            result = alien_eff
        else:
            eff_scl = (self.Cu - self.offset) if alien_eff >=0 else (self.offset - self.Cl)
            alien_eff *= eff_scl
            result = alien_eff + ego_eff
        
        # TODO: fix it !
        result = np.array(result).reshape((-1))
        if with_noise:
            return result + self.rng.normal(self.gauss_loc, self.gauss_scl, result.shape)
        else: 
            return result
    
    def match_with(self, eid):
        assert isinstance(eid, EdgeID), "Only EdgeID is supported"
        if isinstance(self._indim, int):
            return len(eid.lag_origins) == 1 and self._indim <= 1+eid.lag_origins[0][0] # 1 extra for the instantaneous value
        else:
            o_set = {lo[1] for lo in eid.lag_origins}
            return o_set.issubset(self._indim.keys())


class RandomDiscreteMLP(RandomMLP):
    def __init__(self, target, parents, L, values , h=16, **kwargs):
        self.is_discrete = True
        self.values = values
        
        super().__init__(target, parents, L, h, **kwargs)
        
        # TODO: infer distribution
    
    def __call__(self, **kwargs):
        
        
        kwargs['with_noise'] = True
        result = super().__call__(**kwargs)
        
        scale = max(self.values) - min(self.values)
        
        result *= scale
        
        result = min(self.values, key=lambda x: abs(x - result[0]))
        
        result = np.array(result).reshape((-1))
        
        return result
