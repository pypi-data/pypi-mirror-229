import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import re
import os
import statsmodels.api as sm
from . import data_process

def genSpectreDataExcel_T_TCRRC_RC0_Th(input_file_name, output_file_name, \
                                       velocity_row_num_csv = 0):
    assert(os.path.exists(input_file_name)), input_file_name + " does not exist, please check it"
    assert(input_file_name != output_file_name), "You cannot modify the input file"
    assert(not os.path.exists(output_file_name)), output_file_name + " exists, please rename or delete it"
    dataset = pd.read_csv(input_file_name)
    dataset_save = pd.DataFrame()
    dataset_col = dataset.columns
    dataset_len = int(len(dataset_col) / 2)
    val_save = np.zeros((dataset_len, 4))
    col_val_str = dataset_col[0].replace("/", "")
    col_val_arr = re.search("(?<=\().+?(?=\))", col_val_str).group().split(" ")
    col_val_str_out = re.search(".+?(?=\()", col_val_str).group().replace(" ", "")
    val_label = np.array([
        col_val_arr[0].split("=")[0],
        col_val_arr[1].split("=")[0],
        col_val_arr[2].split("=")[0],
        col_val_str_out
    ])
    if not velocity_row_num_csv:
        velocity_row_num_csv = dataset.shape[0] + 1
    velocity_row_num = velocity_row_num_csv - 2
    for i in range(dataset_len):
        col_val_str = dataset_col[int(2 * i + 1)]
        col_val_arr = re.search("(?<=\().+?(?=\))", col_val_str).group().split(" ")
        val_save[i, 0] = col_val_arr[0].split("=")[1]
        val_save[i, 1] = col_val_arr[1].split("=")[1]
        val_save[i, 2] = col_val_arr[2].split("=")[1]
        val_save[i, 3] = dataset[col_val_str][velocity_row_num]
    for i in range(len(val_label)):
        dataset_save[val_label[i]] = val_save[:, i]
    dataset_save.to_excel(output_file_name)
    save_path = data_process.getSavePath(output_file_name)
    return save_path

def OLSFitting_C_T_TCRRC_RC0_2x3__Th(file_name, \
                                     T_TCRRC_RC0_Th_col_name_arr = [ \
                                         "temp", "TCR_Rc", "Rc0", "Th" \
                                     ]):
    assert(os.path.exists(file_name)), file_name + " does not exist, please check it"
    dataset = pd.read_excel(file_name)
    dataset_col = T_TCRRC_RC0_Th_col_name_arr
    dataset_new = pd.DataFrame()
    T_name, TCRRC_name, RC0_name, Th_name = dataset_col[0], dataset_col[1], \
                                            dataset_col[2], dataset_col[3]
    dataset_new["T"]         = dataset[T_name]
    dataset_new["TCRRC"]     = dataset[TCRRC_name]
    dataset_new["RC0"]       = dataset[RC0_name]
    dataset_new["TCRRC_x_T"] = dataset_new["TCRRC"] * dataset_new["T"]
    dataset_new["Th"]        = dataset[Th_name]
    x = sm.add_constant(dataset_new[["T", "TCRRC", "RC0", "TCRRC_x_T"]])
    y = dataset_new["Th"]
    model = sm.OLS(y, x)
    print(model.fit().summary())
    coefs = model.fit().params
    return coefs
    
def CalcTh(coefs, Ta_C, Rc0, TCR_Rc):
    const_, T_coef, TCRRC_coef, RC0_coef, TCRRC_x_T_coef = coefs
    Th_C = T_coef * Ta_C + TCRRC_coef * TCR_Rc + \
           TCRRC_x_T_coef * (Ta_C * TCR_Rc) + \
           RC0_coef * Rc0 + const_
    return Th_C
    
def CalcTh_new2(Ta_C, Rc0, TCRc, \
               Rr0, Rh0, TCRr, TCRh, R1, R2, T0_C):
    k = R1 / R2
    beta = lambda _R_, _TCR_: _R_ * _TCR_
    betar, betac, betah = beta(Rr0, TCRr), beta(Rc0, TCRc), beta(Rh0, TCRh)
    Th_C = T0_C - 1.0 / TCRh + ((betac + betar) * (Ta_C - T0_C) + (Rc0 + Rr0)) / (k * betah)
    return Th_C
    
def LRFitting_Exp_T__RC(T_arr, RC_arr):
    return
