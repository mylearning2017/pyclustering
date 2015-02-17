'''

Cluster analysis algorithm: Hierarchical Sync (HSyncNet)

Based on article description:
 - J.Shao, X.He, C.Bohm, Q.Yang, C.Plant. Synchronization-Inspired Partitioning and Hierarchical Clustering. 2013.

Copyright (C) 2015    Andrei Novikov (spb.andr@yandex.ru)

pyclustering is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyclustering is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import pyclustering.core.wrapper as wrapper;

from pyclustering.nnet import *;

from pyclustering.clustering.syncnet import syncnet;
from pyclustering.support import average_neighbor_distance, read_sample;

class hsyncnet(syncnet):
    """!
    @brief Class represents clustering algorithm HSyncNet. HSyncNet is bio-inspired algorithm that is based on oscillatory network that uses modified Kuramoto model.
    
    Example:
    @code
        # read list of points for cluster analysis
        sample = read_sample(file);
        
        # create network for allocation three clusters using CCORE (C++ implementation)
        network = hsyncnet(sample, 3, ccore = True);
        
        # run cluster analysis and output dynamic of the network
        (time, dynamic) = network.process(0.995, collect_dynamic = True);
        
        # get allocated clusters
        clusters = network.get_clusters();
        
        # show output dynamic of the network
        draw_dynamics(time, dynamic);
    @endcode
    """
    _number_clusters = 0;    
    __ccore_network_pointer = None;      # Pointer to CCORE HSyncNet implementation of the network.
    
    def __init__(self, source_data, number_clusters, osc_initial_phases = initial_type.RANDOM_GAUSSIAN, ccore = False):
        """!
        @brief Costructor of the oscillatory network hSyncNet for cluster analysis.
            
        @param[in] source_data (list): Input data set defines structure of the network.
        @param[in] number_clusters (uint): Number of clusters that should be allocated.
        @param[in] osc_initial_phases (initial_type): Type of initialization of initial values of phases of oscillators.
        @param[in] ccore (bool): If True than DLL CCORE (C++ solution) will be used for solving.
        
        """
        
        if (ccore is True):
            self.__ccore_network_pointer = wrapper.create_hsyncnet(source_data, number_clusters, osc_initial_phases);
        else: 
            super().__init__(source_data, 0, initial_phases = osc_initial_phases);
            self._number_clusters = number_clusters;
    
    
    def __del__(self):
        """!
        @brief Destructor of oscillatory network HSyncNet.
        
        """
        
        if (self.__ccore_network_pointer is not None):
            wrapper.destroy_hsyncnet_network(self.__ccore_network_pointer);
            self.__ccore_network_pointer = None;
            
            
    def process(self, order = 0.998, solution = solve_type.FAST, collect_dynamic = False):
        """!
        @brief Performs clustering of input data set in line with input parameters.
        
        @param[in] order (double): Level of local synchronization between oscillator that defines end of synchronization process, range [0..1].
        @param[in] solution (solve_type) Type of solving differential equation.
        @param[in] collect_dynamic (bool): If True - returns whole history of process synchronization otherwise - only final state (when process of clustering is over).
        
        @return (tuple) Returns dynamic of the network as tuple of lists on each iteration (time, oscillator_phases) that depends on collect_dynamic parameter. 
        
        @see get_clusters()
        
        """
        
        if (self.__ccore_network_pointer is not None):
            return wrapper.process_hsyncnet(self.__ccore_network_pointer, order, solution, collect_dynamic);
        
        number_neighbors = 3;
        current_number_clusters = float('inf');
        
        dyn_phase = [];
        dyn_time = [];
        
        radius = average_neighbor_distance(self._osc_loc, number_neighbors);
        
        while(current_number_clusters > self._number_clusters):                
            self._create_connections(radius);
        
            (t, dyn) = self.simulate_dynamic(order, solution, collect_dynamic);
            if (collect_dynamic == True):
                dyn_phase += dyn;
                
                if (len(dyn_time) > 0):
                    point_time_last = dyn_time[len(dyn_time) - 1];
                    dyn_time += [time_point + point_time_last for time_point in t];
                else:
                    dyn_time += t;
            
            clusters = self.get_clusters(0.05);
            
            # Get current number of allocated clusters
            current_number_clusters = len(clusters);
            
            # Increase number of neighbors that should be used
            number_neighbors += 1;
            
            # Update connectivity radius and check if average function can be used anymore
            if (number_neighbors >= len(self._osc_loc)):
                radius = radius * 0.1 + radius;
            else:
                radius = average_neighbor_distance(self._osc_loc, number_neighbors);
        
        
        return (dyn_time, dyn_phase);
    
    
    def get_clusters(self, eps = 0.1):
        """!
        @brief Return list of clusters in line with state of oscillators (phases).
        
        @param[in] eps (double): Tolerance level that define maximal difference between phases of oscillators in one cluster, range [0..2 * pi].
        
        @return (list) List of clusters, for example [ [cluster1], [cluster2], ... ].
        
        """
        
        if (self.__ccore_network_pointer is not None):
            return wrapper.get_clusters_syncnet(self.__ccore_network_pointer, eps);
        else:
            return self.allocate_sync_ensembles(eps);
