import geom
import fields
import tidy3d as td
import numpy as np
import materials
import matplotlib.pyplot as plt
def get_crosshatch_simulation_defaults(z_sim,z_film =0,source_buffer = 0.5,monitor_buffer= 0.5,resolution = [20,20,10],wvl_range = (.25,1),spacing_type = "wvl"):
    '''
    Default parameters for the crosshatch simulation
    simulation size and slit dimensions ARE NOT defaults--they are specified elsewhere
    :return: dict
    '''
    auto_x = td.AutoGrid(min_steps_per_wvl = resolution[0])
    auto_y = td.AutoGrid(min_steps_per_wvl = resolution[1])
    auto_z = td.AutoGrid(min_steps_per_wvl = resolution[2])
    grid_spec = td.GridSpec(grid_x =auto_x,grid_y = auto_y,grid_z = auto_z)
    wvl_range = wvl_range # 250 to 1000 nm by default
    freq_range = (td.C_0/wvl_range[1],td.C_0/wvl_range[0])
    freq_0= np.mean(freq_range)
    wvl_0 =td.C_0/freq_0
    n_freq = 1001
    if (spacing_type == "freq"): #frequency equal spacing
        monitor_freq_array = np.linspace(freq_range[0],freq_range[1],n_freq)
        monitor_wvl_array = td.C_0/monitor_freq_array
    else: #defaults to wavelength equal spacing
        monitor_wvl_array = np.linspace(wvl_range[0],wvl_range[1],n_freq)
        monitor_freq_array = td.C_0/monitor_wvl_array
    bandwidth = .2
    freq_width = (freq_range[1]-freq_range[0])*bandwidth
    time_end = 100/freq_0
    l_film= .1 #100 nm thick
    l_coating = .2 #200 nm thick (glass) coating
    material_film = materials.gold_jc #gold, Johnson Christy 1972
    film = td.Structure(geometry =td.Box(
        center = (0,0,z_film),
        size= (td.inf,td.inf,l_film)),
        medium = material_film,
        name = "film")
    material_substrate = materials.glass
    substrate = td.Structure(geometry = td.Box(
        center = (0,0,z_film+l_film/2+z_sim/2),
        size= (td.inf,td.inf,z_sim)),
        medium = material_substrate,
        name = "substrate") #designed to go out of simulation boundaries
    material_coating = materials.glass
    coating = td.Structure(geometry = td.Box(
        center = (0,0,z_film-l_film/2-l_coating/2),
        size= (td.inf,td.inf,l_coating)),
        medium = material_coating,
        name = "coating")
    material_fill = materials.glass
    wvl_spacing_source = source_buffer*wvl_range[1] # spacing is from coating surface
    wvl_spacing_monitor= monitor_buffer*wvl_range[1] #to prevent issues with PML, spacing is from z boundaries
    structure_list= [coating,film,substrate]
    if (-z_sim/2+wvl_spacing_source+wvl_spacing_monitor+l_coating+l_film/2>0):
        ValueError("Not enough spacing for source signal")
    if (-z_sim / 2 *wvl_spacing_monitor + l_film / 2 > 0):
        ValueError("Not enough spacing for monitor signal")
    monitor_transmission = td.FluxMonitor(center= (0,0,z_sim/2-wvl_spacing_monitor),size= (td.inf,td.inf,0),freqs = monitor_freq_array,name = "transmission")
    monitor_reflection = td.FluxMonitor(center= (0,0,-z_sim/2+wvl_spacing_monitor),size= (td.inf,td.inf,0),freqs = monitor_freq_array,name = "reflection")
    monitor_list = [monitor_transmission,monitor_reflection]
    z_source = z_film-l_film/2-l_coating-wvl_spacing_source
    return grid_spec,z_source,wvl_spacing_monitor,structure_list,monitor_list, material_fill,monitor_wvl_array,time_end,freq_0,freq_width,l_film


def create_source_basic(pol_angle=0,phase=0,freq_0=1,f_width=1,z_height=1,direction = '+'):
    '''
    Basic Guassian source at normal incidence going either in positive or negative z direction
    :param pol_angle:
    :param phase:
    :param freq_0:
    :param f_width:
    :param z_height:
    :param direction:
    :return:
    '''
    source_wave = td.PlaneWave(pol_angle= pol_angle,source_time=  td.GaussianPulse(freq0 = freq_0,fwidth = f_width,phase=phase),
        size = (td.inf,td.inf,0),
        center = (0,0,z_height),
        direction = direction)
    return source_wave

def create_polarized_source_basic(pol_str,**kwargs):
    '''
    High level function for creating sets of polarized sources, specfically to ensure
    coherence between x and y components of circularly-polarized sources.
    Note that these are normal Gaussian pulses polarized in the xy-plane
    NOTE: convention is the RHP is (1,i) in Jones vector
    :param pol_str: str
    :param kwargs: dict
    :return:
    '''
    pol_str = pol_str.lower()
    if pol_str == "x":
        source = [create_source_basic(pol_angle=0,phase=0,**kwargs)]
    elif pol_str == "y":
        source = [create_source_basic(pol_angle=np.pi/2,phase=0,**kwargs)]
    elif pol_str == "r":
        source = [create_source_basic(pol_angle=0,phase=0,**kwargs),
                  create_source_basic(pol_angle= np.pi/2,phase= np.pi/2,**kwargs)]
    elif pol_str == "l":
        source = [create_source_basic(pol_angle=0, phase=0, **kwargs),
                  create_source_basic(pol_angle=np.pi/2, phase=-np.pi / 2, **kwargs)]
    return source

def create_xy_etch(center= np.array([0,0,0]),length=0,width =0,thickness = 0,theta_y=0,medium = td.Medium()):
    '''
    NOTE: theta is define_from Y axis. That is--the default is a slit in the y direction
    :param center:
    :param length:
    :param width:
    :param thickness:
    :param theta_y:
    :param medium:
    :return:
    '''
    #the ordering of the vertices matters in order to draw the quadrilateral correctly
    init_vertices = np.array([[-width/2,+length/2],
                              [+width/2,+length/2],
                            [+width/2,-length/2],
                            [-width/2,-length/2]]).T
    rotation_matrix = np.array([[np.cos(theta_y), -np.sin(theta_y)],
                        [np.sin(theta_y), np.cos(theta_y)]])
    rot_vertices = np.einsum("ij,ja->ia",rotation_matrix,init_vertices)
    final_vertices = rot_vertices+np.tile(center[:2],(4,1)).T
    etch_xy_box = td.PolySlab(vertices= final_vertices.T,axis=2,slab_bounds = [center[2]-thickness/2,center[2]+thickness/2])
    etch = td.Structure(geometry = etch_xy_box,medium = medium)
    return etch
class crosshatch_Simulation():
    '''
    This is a simulation that allows crosshatch and unit cell dimensions for a gold film to vary
    Gold film is always at center of simulation (for now, anyway)
    '''
    def __init__(self,simulation_size,etch_width,etch_1_y_ratio,etch_1_etch_2_ratio,etch_2_angle,pol_str,z_film =0,source_buffer = 0.5,monitor_buffer= 0.5,resolution = [20,20,10],wvl_range = [.25,1],spacing_type = "wvl"):
        '''
        Set up to minimize core free parameters into x_size, y_size, etch_width,ratio of etch_1 to y_dimension, and
        ratio of etch_1 to etch_2. Note that etch 2 CAN leave boundaries of simulation
        :param simulation_size:
        :param etch_width:
        :param etch_1_y_ratio:
        :param etch_1_etch_2_ratio:
        '''

        grid_spec, z_source, wvl_spacing_monitor, structure_list, monitor_list, material_fill, monitor_wvl_array, time_end,freq_0,freq_width,l_film=\
              get_crosshatch_simulation_defaults(z_sim =simulation_size[2],z_film=z_film,source_buffer=source_buffer,monitor_buffer = monitor_buffer,resolution=resolution,wvl_range=wvl_range,spacing_type=spacing_type)
        etch_1 = create_xy_etch(center = np.array([0,0,z_film]),length = etch_1_y_ratio*simulation_size[1],width = etch_width,theta_y =0,thickness = l_film,medium =material_fill)
        etch_2 = create_xy_etch(center = np.array([0,0,z_film]),length = etch_1_y_ratio/etch_1_etch_2_ratio*simulation_size[1],width = etch_width,theta_y =etch_2_angle,thickness= l_film,medium =material_fill)
        structure_list.extend([etch_1, etch_2])
        #for some configurations, the second slit may go through x or y boundaries in unit cells
        if (np.any(etch_2.geometry.vertices[:,0]>simulation_size[0]/2)):
            #for periodic boundaries
            etch_2_left = create_xy_etch(center = np.array([simulation_size[0],0,z_film]),length = etch_1_y_ratio/etch_1_etch_2_ratio*simulation_size[1],width = etch_width,theta_y =etch_2_angle,thickness= l_film,medium =material_fill)
            etch_2_right = create_xy_etch(center = np.array([-simulation_size[0],0,z_film]),length = etch_1_y_ratio/etch_1_etch_2_ratio*simulation_size[1],width = etch_width,theta_y =etch_2_angle,thickness= l_film,medium =material_fill)
            structure_list.extend([etch_2_left,etch_2_right])
        if (np.any(etch_2.geometry.vertices[:,1]>simulation_size[1]/2)):
            etch_2_up = create_xy_etch(center=np.array([0, simulation_size[1], z_film]),
                                         length=etch_1_y_ratio / etch_1_etch_2_ratio * simulation_size[1],
                                         width=etch_width, theta_y=etch_2_angle, thickness=l_film, medium=material_fill)
            etch_2_down = create_xy_etch(center=np.array([0, -simulation_size[1], z_film]),
                                          length=etch_1_y_ratio / etch_1_etch_2_ratio * simulation_size[1],
                                          width=etch_width, theta_y=etch_2_angle, thickness=l_film,
                                          medium=material_fill)
            structure_list.extend([etch_2_up, etch_2_down])
        source_list= create_polarized_source_basic(pol_str=pol_str,freq_0 = freq_0,f_width=freq_width,z_height=z_source,direction="+")
        self.simulation = td.Simulation(center = (0,0,0),size = simulation_size,grid_spec=grid_spec,structures=structure_list,sources= source_list,monitors= monitor_list,
                         run_time = time_end,boundary_spec = td.BoundarySpec(x = td.Boundary.periodic(),y=td.Boundary.periodic(),z=td.Boundary.pml()))
        self.z_film = z_film
        self.etch_width = etch_width
        self.etch_1_y_ratio = etch_1_y_ratio
        self.etch_1_etch_2_ratio = etch_1_etch_2_ratio
        self.pol_str = pol_str
    def plot_self(self,title = ""):
        #plotting first source
        self.simulation.sources[0].source_time.plot_spectrum(times = np.linspace(0,self.simulation.run_time,1001),val="abs")
        plt.savefig(title+"source_spectrum.png")
        plt.show()
        #plotting structures and grid
        figure, (axis_1, axis_2) = plt.subplots(nrows =1,ncols= 2, tight_layout=True, figsize=(10, 4))
        axis_1 = self.simulation.plot(y=0, ax=axis_1)
        axis_1 = self.simulation.plot_grid(y=0, ax=axis_1)
        ax2 = self.simulation.plot(z=self.z_film, ax=axis_2)
        axis_2 = self.simulation.plot_grid(z=self.z_film, ax=ax2)
        figure.savefig(title+"structure.png")
        figure.show()
