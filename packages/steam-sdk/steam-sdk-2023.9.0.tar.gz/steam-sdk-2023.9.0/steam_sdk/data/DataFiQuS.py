from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, NonNegativeFloat
from typing import (Union, Dict, List, Literal)

from steam_sdk.data.DataConductor import ConstantJc, Bottura, CUDI3, Bordini, BSCCO_2212_LBNL, CUDI1, Summers, Round, \
    Rectangular, Rutherford, Mono, Ribbon
from steam_sdk.data.DataRoxieParser import RoxieData


from steam_sdk.data.DataModelCommon import Circuit
from steam_sdk.data.DataModelCommon import PowerSupply


class CCTGeometryCWSInputs(BaseModel):
    """
        Level 3: Class for controlling if and where the conductor files and brep files are written for the CWS (conductor with step) workflow
    """
    write: bool = False             # if true only conductor and brep files are written, everything else is skipped.
    output_folder: str = None       # this is relative path to the input file location


class CCTGeometryWinding(BaseModel):  # Geometry related windings _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = None  # name to use in gmsh and getdp
    r_wms: List[float] = None  # radius of the middle of the winding
    n_turnss: List[float] = None  # number of turns
    ndpts: List[int] = None  # number of divisions of turn, i.e. number of hexagonal elements for each turn
    ndpt_ins: List[int] = None  # number of divisions of terminals ins
    ndpt_outs: List[int] = None  # number of divisions of terminals outs
    lps: List[float] = None  # layer pitch
    alphas: List[float] = None  # tilt angle
    wwws: List[float] = None  # winding wire widths (assuming rectangular)
    wwhs: List[float] = None  # winding wire heights (assuming rectangular)


class CCTGeometryFQPCs(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = []  # name to use in gmsh and getdp
    fndpls: List[int] = None  # fqpl number of divisions per length
    fwws: List[float] = None  # fqpl wire widths (assuming rectangular) for theta = 0 this is x dimension
    fwhs: List[float] = None  # fqpl wire heights (assuming rectangular) for theta = 0 this is y dimension
    r_ins: List[float] = None  # radiuses for inner diameter for fqpl (radial (or x direction for theta=0) for placing the fqpl
    r_bs: List[float] = None  # radiuses for bending the fqpl by 180 degrees
    n_sbs: List[int] = None  # number of 'bending segmetns' for the 180 degrees turn
    thetas: List[float] = None  # rotation in deg from x+ axis towards y+ axis about z axis.
    z_starts: List[str] = None  # which air boundary to start at. These is string with either: z_min or z_max key from the Air region.
    z_ends: List[float] = None  # z coordinate of loop end


class CCTGeometryFormer(BaseModel):  # Geometry related formers _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = None  # name to use in gmsh and getdp
    r_ins: List[float] = None  # inner radius
    r_outs: List[float] = None  # outer radius
    z_mins: List[float] = None  # extend of former  in negative z direction
    z_maxs: List[float] = None  # extend of former in positive z direction
    rotates: List[float] = None  # rotation of the former around its axis in degrees


class CCTGeometryAir(BaseModel):  # Geometry related air_region _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    name: str = None  # name to use in gmsh and getdp
    sh_type: str = None  # cylinder or cuboid are possible
    ar: float = None  # if box type is cuboid a is taken as a dimension, if cylinder then r is taken
    z_min: float = None  # extend of air region in negative z direction
    z_max: float = None  # extend of air region in positive z direction


class CCTGeometry(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    CWS_inputs: CCTGeometryCWSInputs = CCTGeometryCWSInputs()
    windings: CCTGeometryWinding = CCTGeometryWinding()
    fqpcs: CCTGeometryFQPCs = CCTGeometryFQPCs()
    formers: CCTGeometryFormer = CCTGeometryFormer()
    air: CCTGeometryAir = CCTGeometryAir()


class CCTMesh(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    MaxAspectWindings: float = None  # used in transfinite mesh_generators settings to define mesh_generators size along two longer lines of hex elements of windings
    ThresholdSizeMin: float = None  # sets field control of Threshold SizeMin
    ThresholdSizeMax: float = None  # sets field control of Threshold SizeMax
    ThresholdDistMin: float = None  # sets field control of Threshold DistMin
    ThresholdDistMax: float = None  # sets field control of Threshold DistMax


class CCTSolveWinding(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = None  # current in the wire
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability


class CCTSolveFormer(BaseModel):  # Solution time used formers _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigmas: List[float] = None  # electrical conductivity
    mu_rs: List[float] = None  # relative permeability


class CCTSolveFQPCs(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = []  # current in the wire
    sigmas: List[float] = []  # electrical conductivity
    mu_rs: List[float] = []  # relative permeability


class CCTSolveAir(BaseModel):  # Solution time used air _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigma: float = None  # electrical conductivity
    mu_r: float = None  # relative permeability


class CCTSolve(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    windings: CCTSolveWinding = CCTSolveWinding()  # windings solution time _inputs
    formers: CCTSolveFormer = CCTSolveFormer()  # former solution time _inputs
    fqpcs: CCTSolveFQPCs = CCTSolveFQPCs()  # fqpls solution time _inputs
    air: CCTSolveAir = CCTSolveAir()  # air solution time _inputs
    pro_template: str = None  # file name of .pro template file
    variables: List[str] = None  # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: List[str] = None  # Name of volume to post-process by GetDP, line Winding_1
    file_exts: List[str] = None  # Name of file extensions to post-process by GetDP, like .pos


class CCTPostproc(BaseModel):
    """
        Level 2: Class for  FiQuS CCT
    """
    windings_wwns: List[int] = None  # wires in width direction numbers
    windings_whns: List[int] = None  # wires in height direction numbers
    additional_outputs: List[str] = None  # Name of software specific input files to prepare, like :LEDET3D
    winding_order: List[int] = None
    fqpcs_export_trim_tol: List[
        float] = None  # this multiplier times winding extend gives 'z' coordinate above(below) which hexes are exported for LEDET, length of this list must match number of fqpls
    variables: List[str] = None  # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volumes: List[str] = None  # Name of volume to post-process by python Gmsh API, line Winding_1
    file_exts: List[str] = None  # Name of file extensions o post-process by python Gmsh API, like .pos


class CCT(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    type: Literal['CCT_straight']
    geometry: CCTGeometry = CCTGeometry()
    mesh: CCTMesh = CCTMesh()
    solve: CCTSolve = CCTSolve()
    postproc: CCTPostproc = CCTPostproc()


class CWSGeometryConductors(BaseModel):  # Conductor file data for geometry building
    """
        Level 2: Class for FiQuS CWS
    """
    resample: List[int] = None
    skip_middle_from: List[int] = None  # decides which bricks are skipped in fuse operation, basically only a few bricks should overlap with the former.
    skip_middle_to: List[int] = None  # decides which bricks are skipped in fuse operation, basically only a few bricks should overlap with the former.
    combine_from: List[List[int]] = None
    combine_to: List[List[int]] = None
    swap_p_s: List[List[int]] = None # swap points source - point indices for source points, only valid for numbers in range from 1 to 8. If 0, do not swap.
    swap_p_d: List[List[int]] = None # swap points destination - point indices for destination points, only valid for numbers in range from 1 to 8. If 0, do not swap.
    file_names_large: List[str] = None
    file_names: List[str] = None  # Inner_17.1mm #[inner_FL, outer_FL] #
    ends_need_trimming: bool = False    # If there are windings "sticking out" of the air region this needs to set to True. It removes 2 volumes per winding after the fragment operation


class CWSGeometryFormers(BaseModel):  # STEP file data for geometry building
    """
        Level 2: Class for FiQuS CWS
    """
    file_names: List[str] = None    # STEP file names to use
    air_pockets: List[int] = None   # number of air pockets (for e.g. for heater or temperature sensor pads) on the formers


class CWSGeometryShells(BaseModel):  # STEP file data for geometry building
    """
        Level 2: Class for FiQuS CWS
    """
    file_names: List[str] = None    # STEP file names to use


class CWSGeometryAir(BaseModel):  # Geometry related air_region _inputs
    """
        Level 2: Class for FiQuS CWS
    """
    name: str = None  # name to use in gmsh and getdp
    sh_type: str = None  # cylinder or cuboid are possible
    ar: float = None  # if box type is cuboid 'a' is taken as a dimension, if cylinder then 'r' is taken
    z_min: float = None  # extend of air region in negative z direction, for cylinder_cov this is ignored
    z_max: float = None  # extend of air region in positive z direction, for cylinder_cov this is ignored


class CWSGeometry(BaseModel):
    """
        Level 2: Class for FiQuS CWS for FiQuS input
    """
    conductors: CWSGeometryConductors = CWSGeometryConductors()
    formers: CWSGeometryFormers = CWSGeometryFormers()
    shells: CWSGeometryShells = CWSGeometryShells()
    air: CWSGeometryAir = CWSGeometryAir()


class CWSSolveMaterialPropertyListConductors(BaseModel):
    constant: List[float] = None  # list of values if constant is used


class CWSSolveMaterialPropertyList(BaseModel):
    constant: List[float] = None  # list of values if constant is used
    function: List[str] = None  # list of material property function names if function is used


class CWSSolveMaterialPropertySingle(BaseModel):
    constant: float = None  # value if constant is used
    function: str = None  # material property function name if function is used
    use: str = None # allowed values are: constant or function and decide which value above is used


class CWSSolveConductorsExcitationFunction(BaseModel):  # Solution time used Conductor _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    names: List[str] = Field(default=None, description="Currently, these function names are supported: exp_decrease, exp_increase, linear_decrease, linear_increase ")
    taus: List[float] = Field(default=None, description="Time constant for exponential: Amplitude*Exp(-time/tau), for linear: Amplitude*(time-time_initial)/tau ")


class CWSSolveConductorsExcitationFromFile(BaseModel):  # Solution time used Conductor _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    file_name: str = None  # full file name (i.e. with extension) in the input folder or complete path
    multips: List[float] = None  # constant multipliers for values in the input file. One value at one time, but multiplied for each conductor by these constants.
    time_header: str = None  # string defining the time signal header in the txt file
    value_header: str = None  # string defining the value (typically current) signal header in the txt file


class CWSSolveConductorsExcitation(BaseModel):  # Solution time used Conductor _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    initials: List[float] = None  # initial current or voltage in the conductor
    function: CWSSolveConductorsExcitationFunction = CWSSolveConductorsExcitationFunction()
    from_file: CWSSolveConductorsExcitationFromFile = CWSSolveConductorsExcitationFromFile()
    transient_use: str = None  # function or from_file allowed


class CWSSolveConductors(BaseModel):  # Solution time used Conductor _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    excitation: CWSSolveConductorsExcitation = CWSSolveConductorsExcitation()
    conductivity_el: CWSSolveMaterialPropertyListConductors = CWSSolveMaterialPropertyListConductors()
    permeability: List[float] = None  # relative permeability


class CWSSolveInduced(BaseModel):  # Solution time used fqpls _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    RRR_functions: List[float] = None  # RRR to use in material functions
    mass_density_functions: List[float] = None  # mass density to use in material functions
    conductivity_el: CWSSolveMaterialPropertyList = CWSSolveMaterialPropertyList()
    permeability: List[float] = []  # relative permeability
    conductivity_th: CWSSolveMaterialPropertyList = Field(default=CWSSolveMaterialPropertyList(), alias="conductivity_th", description="W/mK")
    heat_capacity: CWSSolveMaterialPropertyList = Field(default=CWSSolveMaterialPropertyList(), alias="heat_capacity", description="J/m^3 K")


class CWSSolveInsulation(BaseModel):
    """
        Level 2: Class for FiQuS CWS
    """
    thickness: float = None     # thickness of insulation former to former or former to shell
    conductivity_th: CWSSolveMaterialPropertySingle = CWSSolveMaterialPropertySingle()  # W/mK
    heat_capacity: CWSSolveMaterialPropertySingle = Field(default=CWSSolveMaterialPropertySingle(), alias="heat_capacity", description="J/m^3 K")


class CWSSolveAir(BaseModel):  # Solution time used air _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CWS
    """
    conductivity_el: float = None  # electrical conductivity
    permeability: float = None  # relative permeability


class CWSSolveOutputResample(BaseModel):  # Solution outputs definition
    enabled: bool = None # flat to decide if the output is resampled or not
    delta_t: float = None  # delta time for resampling

class CWSSolveOutput(BaseModel):  # Solution outputs definition
    saved: bool = None # flat to decide if the output is saved
    resample: CWSSolveOutputResample = CWSSolveOutputResample()
    variables: List[str] = Field(default=None, description="Name of variable to post-process by GetDP | This only applies to static solution for now") # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: List[str] = Field(default=None, description="Name of volume to post-process by GetDP | This only applies to static solution for now") # Name of volume to post-process by GetDP, line Winding_1
    file_exts: List[str] = Field(default=None, description="Name of file extensions to output by GetDP | This only applies to static solution for now") # Name of file extensions to post-process by GetDP, like .pos


class CWSSolveStaticSettings(BaseModel):
    solved: bool = None # chooses if static solution is solved. Note the transient solution starts with a static solution, so if this and the transient are set to true, the static is solved twice
    output: CWSSolveOutput = CWSSolveOutput()


class CWSSolveTime(BaseModel):
    initial: float = Field(default=None, description="Initial time")
    end: float = Field(default=None, description="End time")


class CWSSolveTimeFixed(BaseModel):
    step: float = Field(default=None, description="Time step")
    theta: float = Field(default=None, description="Time stepping scheme")


class CWSSolveTimeAdaptiveLTEInputs(BaseModel):
    names: List[str] = Field(default=None, description="string: name of post operation to use")
    relatives: List[float] = Field(default=None, description="relative tolerance")
    absolutes: List[float] = Field(default=None, description="absolute tolerance")
    normTypes: List[str] = Field(default=None, description="string with norm type, allowed: L1Norm, MeanL1Norm, L2Norm, MeanL2Norm, LinfNorm")


class CWSSolveTimeAdaptiveLTE(BaseModel):
    System: CWSSolveTimeAdaptiveLTEInputs = CWSSolveTimeAdaptiveLTEInputs()         # Quantities of interest specified at system level
    PostOperation: CWSSolveTimeAdaptiveLTEInputs = CWSSolveTimeAdaptiveLTEInputs()  # Quantities of interest specified at PostOperation level


class CWSSolveTimeAdaptive(BaseModel):
    initial_step: float = Field(default=None, description="Initial time step. Note this is only used when not starting from previous result")
    min_step: float = Field(default=None, description="Minimum time step")
    max_step: float = Field(default=None, description="Maximum time step")
    integration_method: str = Field(default=None, description="string: Euler, Trapezoidal, Gear_2, Gear_3, Gear_4, Gear_5, Gear_6")
    breakpoints_every: float = Field(default=None, description="this creates a list from initial to end time with this step") # list of time points to be hit
    additional_breakpoints: List[float] = Field(default=None, description="Additional break points to request, typically when the solution is expected to change steeply, like t_PC_off of LEDET")
    LTE: CWSSolveTimeAdaptiveLTE = CWSSolveTimeAdaptiveLTE()  # local_truncation_errors


class CWSSolveNonLinearThermalSettingsTolerance(BaseModel):
    name: str = Field(default=None, description="string: name of post operation to use")
    relative: float = Field(default=None, description="relative tolerance")
    absolute: float = Field(default=None, description="absolute tolerance")
    normType: str = Field(default=None, description="string with norm type, allowed: L1Norm, MeanL1Norm, L2Norm, MeanL2Norm, LinfNorm")


class CWSSolveNonLinearThermalSettings(BaseModel):
    enabled: bool = None  # flag to decide if constant material properties or nonlinear material functions should be used
    maximumNumberOfIterations: int = Field(default=None, description="Number of iterations to use")
    relaxationFactor: float = Field(default=None, description="Relaxation factor to use")
    tolerance: CWSSolveNonLinearThermalSettingsTolerance = CWSSolveNonLinearThermalSettingsTolerance()


class CWSSolveTransientSettings(BaseModel):
    solved: bool = None # flag to decide if a transient solution is solved
    with_thermal: bool = None # flag to decide if thermal solution is solved
    thermal_TSA_N_elements: int = None # if set to 0 the thermal TSA is disabled so the is no heat flow between induced parts. Otherwise, this is number of elements across the thin shell
    nonlinear_thermal_iterations: CWSSolveNonLinearThermalSettings = CWSSolveNonLinearThermalSettings()
    time_stepping: str = Field(default=None, description="either 'fixed' or 'adaptive'")
    start_from_previous: bool = Field(default=None, description="not implemented yet, just a placeholder") # flag to decide if the previous solution (time window of transient should be used as a starting point for this time window)
    time: CWSSolveTime = CWSSolveTime()
    fixed: CWSSolveTimeFixed = CWSSolveTimeFixed()
    adaptive: CWSSolveTimeAdaptive = CWSSolveTimeAdaptive()
    em_output: CWSSolveOutput = CWSSolveOutput()
    th_output: CWSSolveOutput = CWSSolveOutput()


class CWSSolve(BaseModel):
    """
        Level 2: Class for FiQuS CWS
    """
    verbose_level: int = None # Verbosity level for GetDP
    temperature: float = None  # Initial temperature for the thermal solve
    conductors: CWSSolveConductors = CWSSolveConductors()  # windings solution time _inputs
    formers: CWSSolveInduced = CWSSolveInduced()  # formers solution time _inputs
    shells: CWSSolveInduced = CWSSolveInduced()   # shells solution time _inputs
    insulation: CWSSolveInsulation = CWSSolveInsulation()  # insulation former to former or former to shell, thermal properties only. Electrically it is fully insulated.
    air: CWSSolveAir = CWSSolveAir()  # air solution time _inputs
    pro_template: str = None  # file name of .pro template file
    static: CWSSolveStaticSettings = CWSSolveStaticSettings()  # transient solution settings
    transient: CWSSolveTransientSettings = CWSSolveTransientSettings() # transient solution settings


class CWSMesh(BaseModel):
    """
        Level 2: Class for FiQuS CWS
    """
    MaxAspectWindings: float = None  # used in transfinite mesh_generators settings to define mesh_generators size along two longer lines of hex elements of windings
    Min_length_windings: float = None  # sets how small the edge length for the winding geometry volumes could be used. Overwrites the calculated value if it is smaller than this number.
    ThresholdSizeMinWindings: float = None  # sets field control of Threshold SizeMin
    ThresholdSizeMaxWindings: float = None  # sets field control of Threshold SizeMax
    ThresholdDistMinWindings: float = None  # sets field control of Threshold DistMin
    ThresholdDistMaxWindings: float = None  # sets field control of Threshold DistMax
    ThresholdSizeMinFormers: float = None  # sets field control of Threshold SizeMin
    ThresholdSizeMaxFormers: float = None  # sets field control of Threshold SizeMax
    ThresholdDistMinFormers: float = None  # sets field control of Threshold DistMin
    ThresholdDistMaxFormers: float = None  # sets field control of Threshold DistMax


class CWSPostproc_FieldMap(BaseModel):
    process_static: bool = None # flag to switch on and off processing of static solution for field map
    process_transient: bool = None # flag to switch on and off processing of transient solution for field map
    conductors_wwns: List[int] = None  # wires in width number of divisions
    conductors_whns: List[int] = None  # wires in height number of divisions
    channel_ws: List[float] = None # wire width
    channel_hs: List[float] = None # wire height
    winding_order: List[int] = Field(default=None, description="[1, 2, 3, 4, 5, 6, 7, 8]")
    trim_from: List[int] = None
    trim_to: List[int] = None
    n_points_for_B_avg: List[int] = None    # number of points to extract for calculating average for B in the center of each wire turn
    variable: str = Field(default=None, description="Name of variable to post-process by gmsh for LEDET") # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volume: str = Field(default=None, description="Name of volume to post-process by gmsh for LEDET") # Name of volume to post-process by python Gmsh API, line Winding_1
    file_ext: str = Field(default=None, description="Name of file extensions to output to by gmsh for LEDET") # Name of file extensions o post-process by python Gmsh API, like .pos


class CWSPostproc_Inductance(BaseModel):
    process_static: bool = None # flag to switch on and off processing of static solution for inductance
    process_transient: bool = None # flag to switch on and off processing of transient solution for inductance


class CWSPostproc_TemperatureMap(BaseModel):
    process_transient: bool = None # flag to switch on and off processing of transient solution of temperature


class CWSPostproc_CircuitValues(BaseModel):
    process_static_and_transient: bool = None # flag to switch on and off processing of static and transient solutions for circuit values


class CWSPostproc(BaseModel):
    """
        Class for FiQuS CWS input file
    """
    field_map: CWSPostproc_FieldMap = CWSPostproc_FieldMap()
    inductance: CWSPostproc_Inductance = CWSPostproc_Inductance()
    temperature_map: CWSPostproc_TemperatureMap = CWSPostproc_TemperatureMap()
    circuit_values: CWSPostproc_CircuitValues = CWSPostproc_CircuitValues()


class CWS(BaseModel):
    """
        Level 1: Class for FiQuS CWS
    """
    type: Literal['CWS']
    geometry: CWSGeometry = CWSGeometry()
    mesh: CWSMesh = CWSMesh()
    solve: CWSSolve = CWSSolve()
    postproc: CWSPostproc = CWSPostproc()


# Multipole
class MultipoleSolveTemperatureBoundaryCondition(BaseModel):
    """
        Level 5: Class for FiQuS Multipole
    """
    boundaries: List[str] = []
    const_temperature: float = None
    # function_temperature: str = None


class MultipoleSolveHeatFluxBoundaryCondition(BaseModel):
    """
        Level 5: Class for FiQuS Multipole
    """
    boundaries: List[str] = None
    const_heat_flux: float = None
    #function_heat_flux: str = None


class MultipoleSolveConvectionBoundaryCondition(BaseModel):
    """
        Level 5: Class for FiQuS Multipole
    """
    boundaries: List[str] = []
    const_heat_transfer_coefficient: float = None
    function_heat_transfer_coefficient: str = None


class MultipoleSolveTimeParameters(BaseModel):
    """
        Level 5: Class for FiQuS Multipole
    """
    initial_time: float = None
    final_time: float = None
    time_step: float = None


class MultipoleSolveQuenchInitiation(BaseModel):
    """
        Level 5: Class for FiQuS Multipole
    """
    turns: List[int] = []
    temperatures: List[float] = []


class MultipoleSolveBoundaryConditionsElectromagnetics(BaseModel):
    """
        Level 4: Class for FiQuS Multipole
    """
    currents: List[float] = []


class MultipoleSolveBoundaryConditionsThermal(BaseModel):
    """
        Level 4: Class for FiQuS Multipole
    """
    temperature: Dict[str, MultipoleSolveTemperatureBoundaryCondition] = {}
    heat_flux: Dict[str, MultipoleSolveHeatFluxBoundaryCondition] = {}
    cooling: Dict[str, MultipoleSolveConvectionBoundaryCondition] = {}


class MultipoleSolveTransientElectromagnetics(BaseModel):
    """
        Level 4: Class for FiQuS Multipole
    """
    time_pars: MultipoleSolveTimeParameters = MultipoleSolveTimeParameters()
    initial_current: float = None


class MultipoleSolveHeCooling(BaseModel):
    """
        Level 4: Class for FiQuS Multipole
    """
    sides: str = None
    const_heat_transfer_coefficient: float = None
    function_heat_transfer_coefficient: str = None


class MultipoleSolveTransientThermal(BaseModel):
    """
        Level 4: Class for FiQuS Multipole
    """
    time_pars: MultipoleSolveTimeParameters = MultipoleSolveTimeParameters()
    quench_initiation: MultipoleSolveQuenchInitiation = MultipoleSolveQuenchInitiation()


class MultipoleSolveElectromagnetics(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    solved: str = None
    boundary_conditions: MultipoleSolveBoundaryConditionsElectromagnetics = MultipoleSolveBoundaryConditionsElectromagnetics()
    transient: MultipoleSolveTransientElectromagnetics = MultipoleSolveTransientElectromagnetics()


class MultipoleSolveThermal(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    solved: str = None
    initial_temperature: float = None
    He_cooling: MultipoleSolveHeCooling = MultipoleSolveHeCooling()
    isothermal_conductors: bool = False
    boundary_conditions: MultipoleSolveBoundaryConditionsThermal = MultipoleSolveBoundaryConditionsThermal()
    transient: MultipoleSolveTransientThermal = MultipoleSolveTransientThermal()


class MultipoleMeshThreshold(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    SizeMin: float = None
    SizeMax: float = None
    DistMin: float = None
    DistMax: float = None


class MultipoleGeometry(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    simplified_coil: bool = None
    with_iron_yoke: bool = None
    with_wedges: bool = None
    symmetry: str = None


class MultipoleMesh(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    default_mesh: bool = None
    conductors_transfinite_edges: str = None
    mesh_iron: MultipoleMeshThreshold = MultipoleMeshThreshold()
    mesh_coil: MultipoleMeshThreshold = MultipoleMeshThreshold()
    Algorithm: int = None  # sets gmsh Mesh.Algorithm
    ElementOrder: int = None  # sets gmsh Mesh.ElementOrder
    Optimize: int = None  # sets gmsh Mesh.Optimize


class MultipoleSolve(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    electromagnetics: MultipoleSolveElectromagnetics = MultipoleSolveElectromagnetics()
    thermal: MultipoleSolveThermal = MultipoleSolveThermal()
    thin_shells: bool = None
    pro_template: str = None  # file name of .pro template file


class MultipolePostProc(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    compare_to_ROXIE: str = None
    plot_all: str = None
    variables: List[str] = None  # Name of variables to post-process, like "b" for magnetic flux density
    volumes: List[str] = None  # Name of domains to post-process, like "powered"
    file_exts: List[str] = None  # Name of file extensions to output to, like "pos"
    additional_outputs: List[str] = None  # Name of software specific input files to prepare, like "LEDET3D"


class Multipole(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    type: Literal['multipole']
    geometry: MultipoleGeometry = MultipoleGeometry()
    mesh: MultipoleMesh = MultipoleMesh()
    solve: MultipoleSolve = MultipoleSolve()
    postproc: MultipolePostProc = MultipolePostProc()


# Pancake3D
class Pancake3DGeometryWinding(BaseModel):
    r_i: PositiveFloat = Field(alias='innerRadius', description='inner radius of the winding', default=1.0)
    t: PositiveFloat = Field(alias='thickness', description='tape thickness of the winding', default=1.0)
    N: PositiveFloat = Field(alias='numberOfTurns', description='number of turns of the winding', default=1.0)
    h: PositiveFloat = Field(alias='height', description='height or tape width of the winding', default=1.0)
    name: str = Field(default='dummy', description='name to be used in the mesh')
    NofVolPerTurn: PositiveInt = Field(default=1, alias='numberOfVolumesPerTurn', description='number of volumes per turn (CAD related, not physical)')
    theta_i: float = Field(default=0.0, alias='startAngle', description='start angle of the first pancake coil in radians')

class Pancake3DGeometryInsulation(BaseModel):
    tsa: bool = Field(alias='thinShellApproximation', description='thin shell approximation (TSA) for insulations or full 3D model', default=True)
    t: PositiveFloat = Field(alias='thickness', description='insulation thickness', default=1.0)
    name: str = Field(default='dummy', description='name to be used in the mesh')

class Pancake3DGeometryTerminal(BaseModel):
    name: str = Field(description='name to be used in the mesh', default='dummy')
    t: PositiveFloat = Field(alias='thickness', description="terminal's tube thickness", default=1.0)

class Pancake3DGeometryTerminals(BaseModel):
    i: Pancake3DGeometryTerminal = Field(alias='inner', default=Pancake3DGeometryTerminal())
    o: Pancake3DGeometryTerminal = Field(alias='outer', default=Pancake3DGeometryTerminal())
    firstName: str = Field(default='dummy', description='name of the first terminal')
    lastName: str = Field(default='dummy', description='name of the last terminal')

class Pancake3DGeometryAir(BaseModel):
    r: PositiveFloat = Field(default=1.0, alias='radius', description='radius (for cylinder type air)')
    a: PositiveFloat = Field(default=1.0, alias='sideLength', description='side length (for cuboid type air)')
    margin: PositiveFloat = Field(alias='axialMargin', description='axial margin between the ends of the air and first/last pancake coils', default=1.0)
    name: str = Field(default='dummy', description='name to be used in the mesh')
    type: Literal['cylinder', 'cuboid'] = Field(default='cylinder', description='choices: cylinder, cuboid')
    shellTransformation: bool = Field(default=True, alias='shellTransformation', description='apply shell transformation if True (GetDP related, not physical)')
    shellTransformationMultiplier: PositiveFloat = Field(default=1.0, alias='shellTransformationMultiplier', description="multiply the air's outer dimension by this value to get the shell's outer dimension")
    cutName: str = Field(default='dummy', description='name of the cut (cochain) to be used in the mesh')
    shellVolumeName: str = Field(default='dummy', description='name of the shell volume to be used in the mesh')
    fragment: bool = Field(default=True, alias='generateGapAirWithFragment', description='generate the gap air with gmsh/model/occ/fragment if true (CAD related, not physical)')

class Pancake3DMeshWinding(BaseModel):
    axne: List[PositiveInt] = Field(alias='axialNumberOfElements', description='axial number of elements (list of integers)', default=[1])
    ane: List[PositiveInt] = Field(alias='azimuthalNumberOfElementsPerTurn', description='azimuthal number of elements per turn (list of integers)', default=[1])
    rne: List[PositiveInt] = Field(alias='radialNumberOfElementsPerTurn', description='radial number of elements per turn (list of integers)', default=[1])
    axbc: List[PositiveFloat] = Field(default=[1.0], alias='axialBumpCoefficients', description='axial bump coefficient (axial elemnt distribution, smaller values for more elements at the ends) (list of floats)')
    elementType: List[Literal['tetrahedron', 'hexahedron', 'prism']] = Field(default=['tetrahedron'], description='choices: tetrahedron, hexahedron, prism')

class Pancake3DMeshInsulation(BaseModel):
    rne: List[PositiveInt] = Field(alias='radialNumberOfElementsPerTurn', description='radial number of elements per turn (list of integers) (only used if TSA is False)', default=[1])

class Pancake3DMeshAir(BaseModel):
    structured: bool = Field(default=True, alias='structureTopAndBottomParts', description='structure the top and bottom parts of the first and last pancake coils if True')

class Pancake3DSolveAir(BaseModel):
    permeability: PositiveFloat = Field(description='permeability of air', default=1.0)

class Pancake3DSolveCERNSuperConductorMaterial(BaseModel):
    name: Literal['HTSSuperPower'] = Field(description='choices: HTSSuperPower', default='HTSSuperPower')
    IcAtTinit: PositiveFloat = Field(alias='criticalCurrentDensityAtInitialTemperature', default=1.0)
    nValue: PositiveFloat = Field(default=1.0, description='n-value for E–J power law')
    relativeThickness: PositiveFloat = Field(default=1.0, description='(thickness of the material) / (thickness of the winding)')
    electricFieldCriterion: PositiveFloat = Field(default=1.0, description='the electric field at which the current density reaches the critical current density')
    minimumPossibleResistivity: PositiveFloat = Field(default=1.0)

class Pancake3DSolveCERNNormalMaterial(BaseModel):
    name: Literal['Copper', 'Hastelloy', 'Silver', 'Indium', 'Stainless Steel'] = Field(description='choices: Copper, Hastelloy, Silver, Indium, Stainless Steel', default='Copper')
    relativeThickness: PositiveFloat = Field(default=1.0, description='(thickness of the material) / (thickness of the winding)')
    rrr: PositiveFloat = Field(default=1.0, alias='residualResistanceRatio', description='residual resistance ratio = (rho at refTemperature) / (rho at 0 K)')
    rrrRefT: PositiveFloat = Field(default=1.0, alias='residualResistanceRatioReferenceTemperature', description='reference temperature for residual resistance ratio')

class Pancake3DSolveMaterial(BaseModel):
    numberOfThinShellElements: PositiveInt = Field(default=1, description='number of thin shell elements (GetDP related, not physical and only used when TSA is set to True)')
    resistivity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    thermalConductivity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    specificHeatCapacity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    material: Pancake3DSolveCERNNormalMaterial = Field(default=Pancake3DSolveCERNNormalMaterial(), description='material from CERN material library')

class Pancake3DSolveWindingMaterial(BaseModel):
    resistivity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    thermalConductivity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    specificHeatCapacity: PositiveFloat = Field(default=1.0, description='a scalar (linear material)')
    material: List[Union[Pancake3DSolveCERNNormalMaterial, Pancake3DSolveCERNSuperConductorMaterial]] = Field(default=[Pancake3DSolveCERNNormalMaterial()], description='list of materials for the winding (sum of the thicknesses must be equal to the thickness of the winding)')

class Pancake3DSolveTolerance(BaseModel):
    name: Literal['solutionVector', 'totalResistiveHeating'] = Field(description='choices: solutionVector, totalResistiveHeating', default='solutionVector')
    relative: PositiveFloat = Field(description='relative tolerance', default=1.0)
    absolute: PositiveFloat = Field(description='absolute tolerance', default=1.0)
    normType: Literal['L1Norm', 'MeanL1Norm', 'L2Norm', 'MeanL2Norm', 'LinfNorm'] = Field(default='L1Norm', alias='normType', description='choices: L1Norm, MeanL1Norm, L2Norm, MeanL2Norm, LinfNorm')

class Pancake3DSolveAdaptiveTimeLoopSettings(BaseModel):
    initialStep: PositiveFloat = Field(default=1.0, alias='initialStep', description='initial step for adaptive time stepping')
    minimumStep: PositiveFloat = Field(default=1.0, alias='minimumStep', description='minimum step for adaptive time stepping')
    maximumStep: PositiveFloat = Field(default=1.0, alias='maximumStep', description='maximum step for adaptive time stepping')
    tolerances: List[Pancake3DSolveTolerance] = Field(default=[Pancake3DSolveTolerance()], description='tolerances for adaptive time stepping')
    integrationMethod: Literal['Euler', 'Gear_2', 'Gear_3', 'Gear_4', 'Gear_5', 'Gear_6'] = Field(default='Euler', alias='integrationMethod', description='choices: Euler, Gear_2, Gear_3, Gear_4, Gear_5, Gear_6')
    breakPoints: List[float] = Field(default=[0.0], alias='breakPoints', description='list of break points for adaptive time stepping')

class Pancake3DSolveFixedTimeLoopSettings(BaseModel):
    step: PositiveFloat = Field(default=1.0, alias='step', description='time step for fixed time stepping')

class Pancake3DSolveTime(BaseModel):
    adaptive: Pancake3DSolveAdaptiveTimeLoopSettings = Field(default=Pancake3DSolveAdaptiveTimeLoopSettings(), alias='adaptiveSteppingSettings', description='adaptive time loop settings (only used if stepping type is adaptive)')
    fixed: Pancake3DSolveFixedTimeLoopSettings = Field(default=Pancake3DSolveFixedTimeLoopSettings(), alias='fixedSteppingSettings', description='fixed time loop settings (only used if stepping type is fixed)')
    start: float = Field(description='start time of the simulation', default=0.0)
    end: float = Field(description='end time of the simulation', default=0.0)
    timeSteppingType: Literal['fixed', 'adaptive'] = Field(description='time stepping type (fixed or adaptive)', default='fixed')
    extrapolationOrder: Literal[0, 1, 2, 3] = Field(default=0, alias='extrapolationOrder', description='extrapolation order (0, 1, 2 or 3)')

class Pancake3DSolveNonlinearSolverSettings(BaseModel):
    tolerances: List[Pancake3DSolveTolerance] = Field(description='tolerances for nonlinear solver', default=[Pancake3DSolveTolerance()])
    maxIter: PositiveInt = Field(default=1, alias='maximumNumberOfIterations', description='maximum number of iterations')
    relaxationFactor: PositiveFloat = Field(default=1.0, alias='relaxationFactor', description='relaxation factor')

class Pancake3DSolveInitialConditions(BaseModel):
    T: PositiveFloat = Field(alias='temperature', description='initial temperature of pancake coils', default=1.0)

class Pancake3DSolveLocalDefect(BaseModel):
    value: NonNegativeFloat = Field(alias='value', description='value of the local defect', default=0.0)
    startTurn: NonNegativeFloat = Field(alias='startTurn', description='start turn of the local defect', default=0.0)
    endTurn: PositiveFloat = Field(alias='endTurn', description='end turn of the local defect', default=1.0)
    startTime: NonNegativeFloat = Field(alias='startTime', description='start time of the local defect', default=0.0)

class Pancake3DSolveLocalDefects(BaseModel):
    jCritical: Pancake3DSolveLocalDefect = Field(default=Pancake3DSolveLocalDefect(), alias='criticalCurrentDensity', description='set critical current density locally')
    T: Pancake3DSolveLocalDefect = Field(default=Pancake3DSolveLocalDefect(), alias='temperature', description='set temperature locally')

class Pancake3DSolveSaveQuantity(BaseModel):
    name: Literal['magneticField', 'magnitudeOfMagneticField', 'currentDensity', 'magnitudeOfCurrentDensity', 'resistiveHeating', 'temperature', 'voltageBetweenTerminals', 'currentThroughCoil', 'axialComponentOfTheMagneticFieldAtOrigin'] = Field(description='choices: magneticField, magnitudeOfMagneticField, currentDensity, magnitudeOfCurrentDensity, resistiveHeating, temperature, voltageBetweenTerminals, currentThroughCoil, axialComponentOfTheMagneticFieldAtOrigin', default='magneticField')
    timesToBeSaved: List[float] = Field(default=[0.0], description='list of times that wanted to be saved')

class Pancake3DGeometry(BaseModel):
    wi: Pancake3DGeometryWinding = Field(alias='winding', default=Pancake3DGeometryWinding())
    ii: Pancake3DGeometryInsulation = Field(alias='insulation', default=Pancake3DGeometryInsulation())
    ti: Pancake3DGeometryTerminals = Field(alias='terminals', default=Pancake3DGeometryTerminals())
    ai: Pancake3DGeometryAir = Field(alias='air', default=Pancake3DGeometryAir())
    N: PositiveInt = Field(alias='numberOfPancakes', description='number of pancake coils stacked on top of each other', default=1)
    gap: PositiveFloat = Field(alias='gapBetweenPancakes', description='gap distance between the pancake coils', default=1.0)
    dimTol: PositiveFloat = Field(default=1.0, alias='dimensionTolerance', description='dimension tolerance (CAD related, not physical)')
    pancakeBoundaryName: str = Field(default='dummy', description="name of the pancake's curves that touches the air to be used in the mesh")
    insulationBoundaryName: str = Field(default='dummy', description="name of the insulation's curves that touches the air to be used in the mesh (only for TSA)")

class Pancake3DMesh(BaseModel):
    wi: Pancake3DMeshWinding = Field(alias='winding', default=Pancake3DMeshWinding())
    ii: Pancake3DMeshInsulation = Field(alias='insulation', default=Pancake3DMeshInsulation())
    ai: Pancake3DMeshAir = Field(default=Pancake3DMeshAir(), alias='air')
    relSizeMin: PositiveFloat = Field(alias='minimumElementSize', description='minimum mesh element size in terms of the largest mesh size in the winding (for meshes close to the pancake coils)', default=1.0)
    relSizeMax: PositiveFloat = Field(alias='maximumElementSize', description='maximum mesh element size in terms of the largest mesh size in the winding (for meshes far to the pancake coils)', default=1.0)

class Pancake3DSolve(BaseModel):
    t: Pancake3DSolveTime = Field(alias='time', description='time settings', default=Pancake3DSolveTime())
    nls: Pancake3DSolveNonlinearSolverSettings = Field(alias='nonlinearSolver', description='nonlinear solver settings', default=Pancake3DSolveNonlinearSolverSettings())
    wi: Pancake3DSolveWindingMaterial = Field(alias='winding', default=Pancake3DSolveWindingMaterial())
    ii: Pancake3DSolveMaterial = Field(alias='insulation', default=Pancake3DSolveMaterial())
    ti: Pancake3DSolveMaterial = Field(alias='terminals', default=Pancake3DSolveMaterial())
    ai: Pancake3DSolveAir = Field(alias='air', default=Pancake3DSolveAir())
    ic: Pancake3DSolveInitialConditions = Field(alias='initialConditions', description='initial conditions', default=Pancake3DSolveInitialConditions())
    localDefects: Pancake3DSolveLocalDefects = Field(default=Pancake3DSolveLocalDefects(), alias='localDefects')
    save: List[Pancake3DSolveSaveQuantity] = Field(alias='quantitiesToBeSaved', default=[Pancake3DSolveSaveQuantity()], description='list of quantities to be saved')
    type: Literal['electromagnetic', 'thermal', 'coupled'] = Field(description='choices: electromagnetic, thermal, coupled', default='electromagnetic')
    proTemplate: str = Field(default='dummy', description='file name of the .pro template file')
    systemsOfEquationsType: Literal['linear', 'nonlinear'] = Field(default='linear', description='choices: linear, nonlinear')

class Pancake3DPostprocess(BaseModel):
    a: int = Field(default=0)

class Pancake3D(BaseModel):
    type: Literal['Pancake3D'] = Field(default='Pancake3D')
    geometry: Pancake3DGeometry = Field(default=Pancake3DGeometry())
    mesh: Pancake3DMesh = Field(default=Pancake3DMesh())
    solve: Pancake3DSolve = Field(default=Pancake3DSolve())
    postproc: Pancake3DPostprocess = Field(default=Pancake3DPostprocess())
# ---- cable properties ----


class MultipoleMonoSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Mono']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleRibbonSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Ribbon']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleRutherfordSet(BaseModel):
    """
        Rutherford cable type for settings (.set)
    """
    type: Literal['Rutherford']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class MultipoleConductorSet(BaseModel):
    """
        Class for conductor type for settings (.set)
    """
    cable: Union[MultipoleRutherfordSet, MultipoleRibbonSet, MultipoleMonoSet] = {'type': 'Rutherford'}


class MultipoleConductor(BaseModel):
    """
        Class for conductor type for FiQuS input (.yaml)
    """
    version: str = None
    case: str = None
    state: str = None
    cable: Union[Rutherford, Ribbon, Mono] = {'type': 'Rutherford'}
    strand: Union[Round, Rectangular] = {'type': 'Round'}  # TODO: Tape, WIC
    Jc_fit: Union[ConstantJc, Bottura, CUDI1, CUDI3, Summers, Bordini, BSCCO_2212_LBNL] = {
        'type': 'CUDI1'}  # TODO: CUDI other numbers? , Roxie?


class MultipoleRoxieGeometry(BaseModel):
    """
        Class for FiQuS multipole Roxie data (.geom)
    """
    Roxie_Data: RoxieData = RoxieData()


class MultipoleGeneralSetting(BaseModel):
    """
        Class for general information on the case study
    """
    I_ref: List[float] = None


class MultipoleModelDataSetting(BaseModel):
    """
        Class for model data for settings (.set)
    """
    general_parameters: MultipoleGeneralSetting = MultipoleGeneralSetting()
    conductors: Dict[str, MultipoleConductorSet] = {}


class MultipoleSettings(BaseModel):
    """
        Class for FiQuS multipole settings (.set)
    """
    Model_Data_GS: MultipoleModelDataSetting = MultipoleModelDataSetting()


class RunFiQuS(BaseModel):
    """
        Class for FiQuS run
    """
    type: str = None
    geometry: str = None
    mesh: str = None
    solution: str = None
    launch_gui: bool = None
    overwrite: bool = None


class General(BaseModel):
    """
        Class for FiQuS general
    """
    magnet_name: str = None


class EnergyExtraction(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    t_trigger: float = None
    R_EE: float = None
    power_R_EE: float = None
    L: float = None
    C: float = None


class QuenchHeaters(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    N_strips: int = None
    t_trigger: List[float] = None
    U0: List[float] = None
    C: List[float] = None
    R_warm: List[float] = None
    w: List[float] = None
    h: List[float] = None
    h_ins: List[List[float]] = []
    type_ins: List[List[str]] = []
    h_ground_ins: List[List[float]] = []
    type_ground_ins: List[List[str]] = []
    l: List[float] = None
    l_copper: List[float] = None
    l_stainless_steel: List[float] = None
    ids: List[int] = None
    turns: List[int] = None
    turns_sides: List[str] = None


class Cliq(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    t_trigger: float = None
    current_direction: List[int] = None
    sym_factor: int = None
    N_units: int = None
    U0: float = None
    C: float = None
    R: float = None
    L: float = None
    I0: float = None


class QuenchProtection(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    energy_extraction:  EnergyExtraction = EnergyExtraction()
    quench_heaters: QuenchHeaters = QuenchHeaters()
    cliq: Cliq = Cliq()


class DataFiQuS(BaseModel):
    """
        This is data structure of FiQuS Input file
    """
    general: General = General()
    run: RunFiQuS = RunFiQuS()
    magnet: Union[CCT, CWS, Multipole, Pancake3D] = {'type': 'multipole'}
    circuit: Circuit = Circuit()
    power_supply: PowerSupply = PowerSupply()
    quench_protection: QuenchProtection = QuenchProtection()
    conductors: Dict[str, MultipoleConductor] = {}
