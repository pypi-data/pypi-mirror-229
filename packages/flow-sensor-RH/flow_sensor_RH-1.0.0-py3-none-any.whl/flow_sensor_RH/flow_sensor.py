import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.interpolate as interp
from . import get_constant

def getTh_C(Ta_C = 25, DTh = 50):
    """
    Get the heater temperature in degrees Celsius.
    
    Parameters:
        Ta_C - Ambient temperature in degrees Celsius
        DTh  - Constant temperature difference (Overheated temperature difference)
        default: 
            Ta_C = 25
            DTh = 50
        
    Returns:
        Th_C - Heater temperature in degrees Celsius
    """
    Th_C = Ta_C + DTh
    return Th_C

def getTf_C(Ta_C = 25, DTh = 50):
    """
    Get the film temperature in degrees Celsius.
    
    Parameters:
        Ta_C - Ambient temperature in degrees Celsius
        DTh  - Constant temperature difference (Overheated temperature difference)
        default: 
            Ta_C = 25
            DTh = 50
        
    Returns:
        Tf_C - Film temperature in degrees Celsius
    """
    Th_C = getTh_C(Ta_C = Ta_C, DTh = DTh)
    Tf_C = (Ta_C + Th_C) / 2.0
    return Tf_C

def getTf_K(Tf_C):
    """
    Get the film temperature in Kelvin.
    
    Parameters:
        Tf_C - Film temperature in degrees Celsius
        
    Returns:
        Tf_K - Film temperature in Kelvin
    """
    Tf_K = Tf_C + 273.15
    return Tf_K
    
def getPsv(T_C):
    """
    Get the saturated vapor pressure.
    
    Parameters:
        Tf_C - Film temperature in degrees Celsius
        
    Returns:
        Psv  - Saturated vapor pressure
    """
    Psv = 610.7 * 10**(7.5 * T_C / (237.3 + T_C))
    return Psv
    
def getFactor_PT(P, T_C):
    xi_1 = 3.53624e-4 + 2.93228e-5 * T_C \
           + 2.61474e-7 * T_C**2 + 8.57538e-9 * T_C**3
    xi_2 = np.exp(-10.7588 + 6.32529e-2 * T_C \
           - 2.53591e-4 * T_C**2 + 6.33784e-7 * T_C**3)
    _, _, P0, _ = get_constant.getConstant()
    Factor_PT = np.exp(xi_1 * (1 - P / P0) + xi_2 * (P / P0 - 1))
    return Factor_PT

def getxsv(T_C):
    Psv = getPsv(T_C)
    Factor_PT = getFactor_PT(Psv, T_C)
    _, _, P0, _ = get_constant.getConstant()
    xsv = Factor_PT * Psv / P0
    return xsv

def getxv_old(Tf_C, RH):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    xsv = getxsv(Tf_C)
    xv = xsv * RH
    return xv
    
def getRHf(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Ta_C = Tf_C - 1.0 / 2.0 * DTh
    xsva = getxsv(Ta_C)
    xsv = getxsv(Tf_C)
    #Rw = get_constant.getConstant_Rw()
    #AH = RHa * Psva / (Rw * Ta_C)
    RHf = xsva * RH / xsv
    return RHf

def getxv(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    xsv = getxsv(Tf_C)
    RHf = getRHf(Tf_C, RH, DTh)
    xv = xsv * RHf
    return xv

def getZm_xvT(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    xv = getxv(Tf_C, RH, DTh)
    Psv = getPsv(Tf_C)
    Factor_PT = getFactor_PT(Psv, Tf_C)
    Tf_K = getTf_K(Tf_C)
    A = 0.7e-8 - 0.147184e-8 * np.exp(1734.29 / Tf_K)
    B = 0.104e-14 - 0.335297e-17 * np.exp(3645.09 / Tf_K)
    Psv = getPsv(Tf_C)
    Zv = 1 + A * Psv + B * Psv**2
    Zm_xvT = 1 + xv * Factor_PT * (Zv - 1)
    return Zm_xvT

def getDensity(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Tf_K = getTf_K(Tf_C)
    xv = getxv(Tf_C, RH, DTh)
    Zm_xvT = getZm_xvT(Tf_C, RH, DTh)
    Ma, Mv, P0, R = get_constant.getConstant()
    Density = (1 / Zm_xvT) * (P0 / (R * Tf_K)) * Ma * (1 - xv * (1 - Mv / Ma))
    return Density
    
def getMua_v(Tf_C):
    Tf_K = getTf_K(Tf_C)
    Mua = -0.98601 + 9.080125e-2 * Tf_K \
          - 1.17635575e-4 * Tf_K**2 + 1.2349703e-7 * Tf_K**3 \
          - 5.7971299e-11 * Tf_K**4
    Muv = 8.058131868 + 4.000549451e-2 * Tf_C
    return Mua, Muv

def getPhiav_va(Tf_C):
    Mua, Muv = getMua_v(Tf_C)
    Ma, Mv, _, _ = get_constant.getConstant()
    Phiav = np.sqrt(2) / 4 * ((1 + ((Mua / Muv)**0.5) \
            * ((Mv / Ma)**0.25))**2) / ((1 + Ma / Mv)**0.5)
    Phiva = np.sqrt(2) / 4 * ((1 + ((Muv / Mua)**0.5) \
            * ((Ma / Mv)**0.25))**2) / ((1 + Mv / Ma)**0.5)
    return Phiav, Phiva

def getkm(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Tf_K = getTf_K(Tf_C)
    ka = -2.276501e-3 + 1.2598485e-4 * Tf_K \
         - 1.4815235e-7 * Tf_K**2 + 1.73550646e-10 * Tf_K**3 \
         - 1.066657e-13 * Tf_K**4 + 2.47663035e-17 * Tf_K**5
    kv = (17.61758242 + 5.558941059e-2 * Tf_C + 1.663336663e-4 * Tf_C**2) / 1000
    Phiav, Phiva = getPhiav_va(Tf_C)
    xv = getxv(Tf_C, RH, DTh)
    km = (1 - xv) * ka / (1 - xv + xv * Phiav) \
         + xv * kv / (xv + (1 - xv) * Phiva)
    return km

def getViscosity(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Mua, Muv = getMua_v(Tf_C)
    Phiav, Phiva = getPhiav_va(Tf_C)
    xv = getxv(Tf_C, RH, DTh)
    Viscosity = (1 - xv) * Mua / (1 - xv + xv * Phiav) \
                + xv * Muv / (xv + (1 - xv) * Phiva)
    return Viscosity

def getCpm(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Tf_K = getTf_K(Tf_C)
    Cpa = 1000 * (1.03409 - 0.284887e-3 * Tf_K \
          + 0.7816818e-6 * Tf_K**2 - 0.4970786e-9 * Tf_K**3 \
          + 0.1077024e-12 * Tf_K**4)
    Cpv = 1000 * (1.86910989 - 2.578421578e-4 * Tf_C \
          + 1.941058941e-5 * Tf_C**2)
    Ma, Mv, _, _ = get_constant.getConstant()
    xv = getxv(Tf_C, RH, DTh)
    Cpm = (Cpa * (1 - xv) * Ma + Cpv * xv * Mv) / (Ma * (1 - xv) + Mv * xv)
    return Cpm

def getPr_N2(Tf_C, RH, DTh):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Cp = getCpm(Tf_C, RH, DTh)
    D_Viscosity = getViscosity(Tf_C, RH, DTh) / 1e+6
    Lambda = getkm(Tf_C, RH, DTh)
    Pr_N2 = Cp * D_Viscosity / Lambda
    return Pr_N2

def getDelta_Tem_Openspace(Tf_C, RH, DTh, Velocity, SensorParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Pr_N2 = getPr_N2(Tf_C, RH, DTh)
    L = SensorParam["L_h"]
    Ls = SensorParam["L_c"]
    l = L / 2
    ls = Ls / 2
    rr = l / ls
    D_Viscosity = getViscosity(Tf_C, RH, DTh) / 1e+6
    Density = getDensity(Tf_C, RH, DTh)
    Delta = (1.1 * (Ls * (D_Viscosity / Density) / Velocity)**0.5) \
            * ((1 + rr)**1.5 - (1 - rr)**1.5) / rr
    Delta_Tem = Delta / 1.026 * Pr_N2**(-1 / 3) * (1 - (1 - rr)**(3 / 4))**(1 / 3)
    return Delta_Tem, Delta

def getDelta_Tem_Channel(Tf_C, RH, DTh, Velocity, SensorParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    Pr_N2 = getPr_N2(Tf_C, RH, DTh)
    Hc = SensorParam["H_ch"]
    L = SensorParam["L_h"]
    Density = getDensity(Tf_C, RH, DTh)
    D_Viscosity = getViscosity(Tf_C, RH, DTh) / 1e+6
    Delta_Tem = 1.17 * Hc * (L / \
                (Hc * Density * Velocity * Hc / D_Viscosity * Pr_N2))**(1 / 3)
    return Delta_Tem

def getDelta_Tem(Tf_C, RH, DTh, Velocity, TYPE, SensorParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    if TYPE == "open-space":
        Delta_Tem, Delta = getDelta_Tem_Openspace(Tf_C, RH, DTh, Velocity, SensorParam)
    elif TYPE == "channel":
        Delta_Tem = getDelta_Tem_Channel(Tf_C, RH, DTh, Velocity, SensorParam)
        Delta = 0
    return Delta_Tem, Delta

def calcbeta(Tf_C, RH, DTh, Velocity, TYPE, SensorParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    Delta_Tem, Delta = getDelta_Tem(Tf_C, RH, DTh, Velocity, TYPE, SensorParam)
    if TYPE == "open-space":
        beta = Delta_Tem**2 / (6 * Delta)
    elif TYPE == "channel":
        Hc = SensorParam["H_ch"]
        beta = Delta_Tem**2 / Hc - Delta_Tem**3 / (2 * Hc**2)
    return beta
    
def calcr1_2(A, B, C):
    r1 = (-B + np.sqrt(B**2 - 4 * A * C)) / (2 * A)
    r2 = (-B - np.sqrt(B**2 - 4 * A * C)) / (2 * A)
    return r1, r2

def calcA_B_C_WithoutEndLoss(Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    km = getkm(Tf_C, RH, DTh)
    ks, kf, kf1 = kParam["k_s"], kParam["k_f"], kParam["k_f1"]
    if not kf:
        kf = km
    if not kf1:
        kf1 = km
    Thickness_mem = SensorParam["t_f"]
    Delta_Tem = getDelta_Tem(Tf_C, RH, DTh, Velocity, TYPE, SensorParam)[0]
    H = SensorParam["H_ca"]
    Density = getDensity(Tf_C, RH, DTh)
    Cpm = getCpm(Tf_C, RH, DTh)
    beta = calcbeta(Tf_C, RH, DTh, Velocity, TYPE, SensorParam)
    A = ks * Thickness_mem + 1 / 2 * (kf * Delta_Tem + kf1 * H)
    B = -Density * Cpm * Velocity * beta
    C = -(kf / Delta_Tem + kf1 / H)
    return A, B, C

def calcA_B_C_WithEndLoss(Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    km = getkm(Tf_C, RH, DTh)
    ks, _, kf1 = kParam["k_s"], kParam["k_f"], kParam["k_f1"]
    if not kf1:
        kf1 = km
    Thickness_mem = SensorParam["t_f"]
    H = SensorParam["H_ca"]
    l0, l1 = SensorParam["L_h"], SensorParam["L_b"]
    A, B, C = calcA_B_C_WithoutEndLoss( \
              Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam)
    C = C - (2 * ks * Thickness_mem + kf1 * H) / (l0 * l1)
    return A, B, C

def calcA_B_C(Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam, EndLoss = False):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    if EndLoss:
        A, B, C = calcA_B_C_WithEndLoss( \
            Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam)
    else:
        A, B, C = calcA_B_C_WithoutEndLoss( \
            Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam)
    return A, B, C
    
def calcT(x, r1, r2, SensorParam, DTh = 50):
    l = SensorParam["L_h"] / 2
    wh = SensorParam["W_h"] / 2
    assert(x >= -l and x <= l), "x is out of range [-l, l]"
    if x >= -l and x < -wh:
        T = DTh * (np.exp(r2 * x) - np.exp(-r2 * l + r1 * (x + l))) / \
            (np.exp(-r2 * wh) - np.exp(-r2 * l - r1 * (wh - l)))
    elif x >= -wh and x <= wh:
        T = DTh
    else:
        T = DTh * (np.exp(r2 * x) - np.exp(r2 * l + r1 * (x - l))) / \
            (np.exp(r2 * wh) - np.exp(r2 * l + r1 * (wh - l)))
    return T
    
def getDiffT(Ta_C, RH, Velocity, TYPE, SensorParam, kParam, DTh = 50, EndLoss = False):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    Tf_C = getTf_C(Ta_C, DTh)
    A, B, C = calcA_B_C(Tf_C, RH, DTh, Velocity, TYPE, SensorParam, kParam, EndLoss)
    r1, r2 = calcr1_2(A, B, C)
    Distance = SensorParam["D_hs"]
    Td = calcT(Distance, r1, r2, SensorParam, DTh)
    Tu = calcT(-Distance, r1, r2, SensorParam, DTh)
    DiffT = Td - Tu
    return DiffT, Td, Tu
    
def getDiffV(Ta_C, RH, Velocity, TYPE, SensorParam, kParam, 
             Voltage = 0.5, Gain = 200, DTh = 50, EndLoss = False, Fitting_Factor = 2.0):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    assert(TYPE == "open-space" or TYPE == "channel"), \
            "TYPE should be \"open-space\" or \"channel\""
    R0 = SensorParam["R_s0"]
    TCR = SensorParam["TCR_s"]
    _, Td, Tu = getDiffT(Ta_C, RH, Velocity, TYPE, SensorParam, kParam, DTh, EndLoss)
    Rd1 = R0 * (1 + TCR * (Ta_C - 25)) * (1 + TCR * Td / Fitting_Factor)
    Ru1 = R0 * (1 + TCR * (Ta_C - 25)) * (1 + TCR * Tu / Fitting_Factor)
    Rd2 = R0 * (1 + TCR * (Ta_C - 25)) * (1 + TCR * Td / Fitting_Factor)
    Ru2 = R0 * (1 + TCR * (Ta_C - 25)) * (1 + TCR * Tu / Fitting_Factor)
    DiffV = Gain * Voltage * (Rd2 / (Ru2 + Rd2) - Ru1 / (Ru1 + Rd1))
    return DiffV
    
def getLambdaThermal(Tf_C, RH, DTh, Velocity, SensorParam, kParam):
    assert(RH >= 0.0 and RH <= 1.0), "RH should be in range [0, 1]"
    km = getkm(Tf_C, RH, DTh)
    _, k_f, k_f1, k_Al, k_SiO2, k_polySi = \
    kParam["k_s"],  kParam["k_f"],      kParam["k_f1"], \
    kParam["k_Al"], kParam["k_SiO2"],   kParam["k_polySi"]
    if not k_f1:
        k_f1 = km
    if not k_f:
        k_f  = km
        
    L_c, L_h, W_h, D_hsm, H_ca, t_f, t_Al, L_b, W_Al, W_b, W_s, D_scaa = \
    SensorParam["L_c"],     SensorParam["L_h"],     SensorParam["W_h"], \
    SensorParam["D_hsm"],   SensorParam["H_ca"],    SensorParam["t_f"], \
    SensorParam["t_Al"],    SensorParam["L_b"],     SensorParam["W_Al"], \
    SensorParam["W_b"],     SensorParam["W_s"],     SensorParam["D_scaa"]
    
    D_hs = D_hsm - W_s / 2.0
    R_eqs0 = D_hs   / (L_h * t_f) / k_f + \
             W_s    / (L_h * t_f) / k_SiO2 + \
             D_scaa / (L_h * t_f) / k_f
    Lambda_cond_s0_bx = 1.0 / R_eqs0 * 2.0
    
    R_eqf1 = H_ca   / (L_h * W_h) / k_f1
    Lambda_cond_f1_my = 1.0 / R_eqf1
    
    R_eqs1 = L_b    / (W_b * t_f) / k_SiO2
    R_eqs2_= L_b    / (W_Al* t_Al)/ k_Al
    Lambda_cond_s1_mz = 1.0 / R_eqs1 * 2.0
    Lambda_cond_s2_pz = Lambda_cond_s1_mz + 1.0 / R_eqs2_ * 2.0
    
    W_bf = W_h - 2.0 * W_b
    R_eqf1_= L_b    / (W_bf* t_f) / k_f1
    Lambda_cond_f1_bz = 1.0 / R_eqf1_ * 2.0
    
    l_c         = L_c / 2.0
    w_h         = W_h / 2.0
    lc_p_wh     = l_c + w_h
    lc_m_wh     = l_c - w_h
    Density     = getDensity(Tf_C, RH, DTh)
    Pr_N2       = getPr_N2(Tf_C, RH, DTh)
    D_Viscosity = getViscosity(Tf_C, RH, DTh) / 1e+6
    h_l = 0.332 * k_f * (Pr_N2**(1.0 / 3.0)) * \
          ((Density * Velocity / D_Viscosity / lc_p_wh)**(1.0 / 2.0)) * \
          (1.0 - (lc_m_wh / lc_p_wh)**(3.0 / 4.0))**(-1.0 / 3.0)
    h_bar = lc_p_wh * h_l / w_h * \
            (1.0 - (lc_m_wh / lc_p_wh)**(3.0 / 4.0))
    Lambda_conv_f0_px = h_bar * W_h * L_h
    
    LambdaThermal = [\
        Lambda_cond_s0_bx + \
        Lambda_cond_f1_my + \
        Lambda_cond_s1_mz + \
        Lambda_cond_s2_pz + \
        Lambda_cond_f1_bz + \
        Lambda_conv_f0_px,  \
        Lambda_cond_s0_bx,  \
        Lambda_cond_f1_my,  \
        Lambda_cond_s1_mz,  \
        Lambda_cond_s2_pz,  \
        Lambda_cond_f1_bz,  \
        Lambda_conv_f0_px]
    
    return LambdaThermal
