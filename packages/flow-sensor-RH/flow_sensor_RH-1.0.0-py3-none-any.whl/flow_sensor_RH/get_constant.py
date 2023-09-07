def getConstant():
    """
    Get constants required by the Flow Sensor Model.

    Returns:
        Ma, Mv, P0, R, Rw
        Ma - Molar mass of dry air
        Mv - Molar mass of water vapor
        P0 - Atmospheric pressure
        R  - Molar gas constant
    """
    Ma  = 28.963e-3
    Mv  = 18.02e-3
    P0  = 101325
    R   = 8.314
    return Ma, Mv, P0, R
    
def getConstant_Rw():
    Rw  = 461.5
    return Rw
    
def getDefDict():
    SDict = [
        "L_c",      # Chip length of A-A'
        "L_h",      # Heater length
        "W_h",      # Heater width
        "D_hsm",    # Distance between heater and sensor middle
        "H_ch",     # Channel height
        "H_ca",     # Cavity height
        "t_f",      # Film thickness
        "t_Al",     # Al thickness
        "R_s0",     # Resistance of sensor @ 25_C
        "TCR_s",    # TCR of sensor @ 25_C
        "L_b",      # Beam length
        "W_Al",     # Width of Al on beam
        "W_b",      # Beam width
        "W_s",      # Sensor width
        "D_scaa"    # Distance between sensor and A
    ]
    KDict = [
        "k_s",      # Thermal conductivity of sensor side
        "k_f",      # Thermal conductivity of fluid above
        "k_f1",     # Thermal conductivity of fluid in cavity
        "k_SiO2",   # Thermal conductivity of SiO2
        "k_Al",     # Thermal conductivity of Al
        "k_polySi"  # Thermal conductivity of poly-Si
    ]
    return {"SDict": SDict, "KDict": KDict}