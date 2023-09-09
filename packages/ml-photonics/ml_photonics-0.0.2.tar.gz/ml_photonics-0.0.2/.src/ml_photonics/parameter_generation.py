import numpy as np


class UniformParameterGenerator():
    def __init__(self,*bounds):
        self.bounds_list = list(bounds)
        self.num_params = len(self.bounds_list)
    def get_random_parameter_set(self,n=1):
        '''
        Generates n parameter sets from a uniform distribution with the associated bounds. Returns
        as np.ndarray of shape (num_params,n)
        :param n:
        :return:
        '''
        random_parameter_set = np.zeros((self.num_params,n)) #initializing array
        for i in range(self.num_params):
            random_parameter_set[i,:] = np.random.uniform(self.bounds_list[i][0],self.bounds_list[i][1],size=n)
        return random_parameter_set

class WeightedParameterGenerator():
    def __init__(self,parameter_array,weight_array,bound_array):
        '''
        :param parameter_array:
        :param weight_array:
        :param bound_array
        '''
        self.num_params = np.size(parameter_array,0)
        # entire parameter distribution to pick from
        #should be generated via a uniform sweep over the desired bounds
        self.parameter_array = parameter_array
        self.parameter_index_count = np.size(parameter_array,axis=1)
        self.weight_array = weight_array
        self.bound_array = bound_array
        self.bound_range_array = np.abs(self.bound_array[:,1]-self.bound_array[:,0])
    def get_random_parameter_set(self,n=1,kick = 0):
        '''
        Generates n parameter sets from a uniform distribution with the associated bounds. Returns
        as np.ndarray of shape (num_params,n). If kick is not 0, performs a Gaussian kick again
        :param n:
        :return:
        '''
        random_parameter_indices = np.random.choice(self.parameter_index_count,size =n,p=self.weight_array)
        random_parameter_set = self.parameter_array[:,random_parameter_indices]
        if (kick !=0):
            random_kicks = self.get_kick(kick,num_kicks= n)
            random_parameter_set= random_parameter_set+random_kicks
            for i in range(self.num_params):
                cur_params = random_parameter_set[i,:]
                clipped_params = np.clip(cur_params,self.bound_array[i,0],self.bound_array[i,1])
                random_parameter_set[i,:] = clipped_params
        return random_parameter_set
    def get_kick(self,kick=0,num_kicks=1):
        x = self.num_params
        #kick is set of gaussian kicks centered at 0 with std of kick value
        kick_direction = np.random.normal(scale = kick,size=(x,num_kicks))
        #kick is scaled by the range of the bounds for each parameter
        kick_vector = np.einsum("ij,i->ij",kick_direction,self.bound_range_array)
        return kick_vector

