"""
Created on 05 September 2023
@author: HE yanfeng
Version:1.1.0
Citation:
"""
import numpy as np

def __preprocessing(x):
    x=np.asarray(x).astype(np.float) #change x to a ndarray and set data type to float64
    dim=x.ndim
    return dim, x

def interpolate_1d(x1,x2,y1,y2,x):
    y=y1+(x-x1)*(y2-y1)/(x2-x1)
    return y

#s2p 
def s2p(data,p_level,p_data,extrapolation=False):
    """
   This function converts data from hybrid sigma-pressure (model) levels to pressure levels.
   The received data can be 3D[layer,lat,lon] or 4D[time,layer,lat,lon] outputs from a atmospheric model.
   Input:
     data: array_like (in any form that can be converted to an array)
        The data in hybrid sigma-pressure (model) levels that you want to convert to pressure levels.
        The shape of data must be 3D[layer,lat,lon] or 4D[time,layer,lat,lon].
        The dimension "layer" must be ordered from bottom (surface) to top, 
        and the number of layer must larger than 2.
     p_level: array_like (in any form that can be converted to an array)
        The target pressure levels that you want to convert to.
        The shape of p_level must be 1D from bottom (surface) to top.
        The unit of p_level must be the same as p_data.
        Example:
            p_level=np.array([1000.0,950.0,900.0,850.0,700.0,500.0,400.0]) #hPa
     p_data: array_like (in any form that can be converted to an array)
        The pressure data corresponding to "data" in hybrid sigma-pressure (model) levels.
        The shape of p_data must be the same as "data".
        The unit of p_data must be the same as p_level.
     extrapolation: 
        Whether use extrapolation when extrapolation is required to calculate ouput (default:False)
        If it is set to False, when extrapolation is required for a location, 
        the corresponding output will be set to Nan.
        Set extrapolation to true may lead to negative values in the output.
   Output:
     out:ndarray
     The converted data using specified pressure levels (p_level).
     The shape of output should be 3D[p_level.shape,lat,lon] or 4D[time,p_level.shape,lat,lon] 
     depending on your input.
   Examples
   --------
   
   """
    dim_data, data_pro=__preprocessing(data)
    dim_p_data,p_data_pro=__preprocessing(p_data)
    dim_p_level,p_level_pro=__preprocessing(p_level)
    print(dim_data,data_pro.shape)
    
    if dim_p_level == 1:
        p_level_num=p_level_pro.shape[0]
        if dim_data == 3 and dim_p_data == 3:
            layer_num=data_pro.shape[0]
            lat_num=data_pro.shape[1]
            lon_num=data_pro.shape[2]
            data_out=np.zeros((p_level_num,lat_num,lon_num))
            if extrapolation:
                for i in range(lat_num):
                    for j in range(lon_num):
                        for k in range(p_level_num):
                            error_checker=0
                            if p_level_pro[k] > p_data_pro[0,i,j]:
                                data_out[k,i,j]=interpolate_1d(p_data_pro[1,i,j],p_data_pro[0,i,j],
                                                               data_pro[1,i,j],data_pro[0,i,j],p_level_pro[k])
                                error_checker=1
                                #Warning data less than 0
                                #x1,x2,y1,y2,x
                                #x1:p_data_pro[1,i,j]
                                #y1:data_pro[1,i,j]
                                #x2:p_data_pro[0,i,j]
                                #y2:data_pro[0,i,j]
                                #x:p_level_pro[k]
                            elif p_level_pro[k] < p_data_pro[-1,i,j]:
                                data_out[k,i,j]=interpolate_1d(p_data_pro[-2,i,j],p_data_pro[-1,i,j],
                                                               data_pro[-2,i,j],data_pro[-1,i,j],p_level_pro[k])
                                error_checker=1
                                #x1,x2,y1,y2,x
                                #x1:p_data_pro[-2,i,j]
                                #y1:data_pro[-2,i,j]
                                #x2:p_data_pro[-1,i,j]
                                #y2:data_pro[-1,i,j]
                                #x:p_level_pro[k]
                            else:
                                for k_s in range(layer_num):
                                    if p_level_pro[k] < p_data_pro[k_s,i,j] and p_level_pro[k] > p_data_pro[k_s+1,i,j]:
                                        data_out[k,i,j]=interpolate_1d(p_data_pro[k_s,i,j],p_data_pro[k_s+1,i,j],
                                                                       data_pro[k_s,i,j],data_pro[k_s+1,i,j],p_level_pro[k])
                                        error_checker=1
                                        #x1:p_data_pro[k_s,i,j]
                                        #y1:data_pro[k_s,i,j]
                                        #x2:p_data_pro[k_s+1,i,j]
                                        #y2:data_pro[k_s+1,i,j]
                                        #x:p_level_pro[k]
                                    else:
                                        continue
                            if error_checker == 0:
                                raise RuntimeError("data are not found for interpolation at layer:",k,"lat:",i,"lon:",j)

            else:
                for i in range(lat_num):
                    for j in range(lon_num):
                        for k in range(p_level_num):
                            error_checker=0
                            if p_level_pro[k] > p_data_pro[0,i,j] or p_level_pro[k] < p_data_pro[-1,i,j]:
                                data_out[k,i,j]=np.nan
                                error_checker=1
                            else:
                                for k_s in range(layer_num):
                                    if p_level_pro[k] < p_data_pro[k_s,i,j] and p_level_pro[k] > p_data_pro[k_s+1,i,j]:
                                        data_out[k,i,j]=interpolate_1d(p_data_pro[k_s,i,j],p_data_pro[k_s+1,i,j],
                                                                       data_pro[k_s,i,j],data_pro[k_s+1,i,j],p_level_pro[k])
                                        error_checker=1
                                        #x1:p_data_pro[k_s,i,j]
                                        #y1:data_pro[k_s,i,j]
                                        #x2:p_data_pro[k_s+1,i,j]
                                        #y2:data_pro[k_s+1,i,j]
                                        #x:p_level_pro[k]
                                    else:
                                        continue
                            if error_checker == 0:
                                raise RuntimeError("data are not found for interpolation at layer:",k,"lat:",i,"lon:",j)
        elif dim_data == 4 and dim_p_data == 4:
            time_num=data_pro.shape[0]
            layer_num=data_pro.shape[1]
            lat_num=data_pro.shape[2]
            lon_num=data_pro.shape[3]
            data_out=np.zeros((time_num,p_level_num,lat_num,lon_num))
            if extrapolation:
                for t in range(time_num):
                    for i in range(lat_num):
                        for j in range(lon_num):
                            for k in range(p_level_num):
                                error_checker=0
                                if p_level_pro[k] > p_data_pro[t,0,i,j]:
                                    data_out[t,k,i,j]=interpolate_1d(p_data_pro[t,1,i,j],p_data_pro[t,0,i,j],
                                                                     data_pro[t,1,i,j],data_pro[t,0,i,j],p_level_pro[k])
                                    error_checker=1
                                    #Warning data less than 0
                                    #x1,x2,y1,y2,x
                                    #x1:p_data_pro[t,1,i,j]
                                    #y1:data_pro[t,1,i,j]
                                    #x2:p_data_pro[t,0,i,j]
                                    #y2:data_pro[t,0,i,j]
                                    #x:p_level_pro[k]
                                elif p_level_pro[k] < p_data_pro[t,-1,i,j]:
                                    data_out[t,k,i,j]=interpolate_1d(p_data_pro[t,-2,i,j],p_data_pro[t,-1,i,j],
                                                                     data_pro[t,-2,i,j],data_pro[t,-1,i,j],p_level_pro[k])
                                    error_checker=1
                                    #x1,x2,y1,y2,x
                                    #x1:p_data_pro[t,-2,i,j]
                                    #y1:data_pro[t,-2,i,j]
                                    #x2:p_data_pro[t,-1,i,j]
                                    #y2:data_pro[t,-1,i,j]
                                    #x:p_level_pro[k]
                                else:
                                    for k_s in range(layer_num):
                                        if p_level_pro[k] < p_data_pro[t,k_s,i,j] and p_level_pro[k] > p_data_pro[t,k_s+1,i,j]:
                                            data_out[t,k,i,j]=interpolate_1d(p_data_pro[t,k_s,i,j],p_data_pro[t,k_s+1,i,j],
                                                                             data_pro[t,k_s,i,j],data_pro[t,k_s+1,i,j],
                                                                             p_level_pro[k])
                                            error_checker=1
                                            #x1:p_data_pro[t,k_s,i,j]
                                            #y1:data_pro[t,k_s,i,j]
                                            #x2:p_data_pro[t,k_s+1,i,j]
                                            #y2:data_pro[t,k_s+1,i,j]
                                            #x:p_level_pro[k]
                                        else:
                                            continue
                                if error_checker == 0:
                                    raise RuntimeError("data are not found for interpolation at time:",t,"layer:",k,
                                                       "lat:",i,"lon:",j)

            else:
                for t in range(time_num):
                    for i in range(lat_num):
                        for j in range(lon_num):
                            for k in range(p_level_num):
                                error_checker=0
                                if p_level_pro[k] > p_data_pro[t,0,i,j] or p_level_pro[k] < p_data_pro[t,-1,i,j]:
                                    data_out[t,k,i,j]=np.nan
                                    error_checker=1
                                else:
                                    for k_s in range(layer_num):
                                        if p_level_pro[k] < p_data_pro[t,k_s,i,j] and p_level_pro[k] > p_data_pro[t,k_s+1,i,j]:
                                            data_out[t,k,i,j]=interpolate_1d(p_data_pro[t,k_s,i,j],p_data_pro[t,k_s+1,i,j],
                                                                             data_pro[t,k_s,i,j],data_pro[t,k_s+1,i,j],
                                                                             p_level_pro[k])
                                            error_checker=1
                                            #x1:p_data_pro[t,k_s,i,j]
                                            #y1:data_pro[t,k_s,i,j]
                                            #x2:p_data_pro[t,k_s+1,i,j]
                                            #y2:data_pro[t,k_s+1,i,j]
                                            #x:p_level_pro[k]
                                        else:
                                            continue
                                if error_checker == 0:
                                    raise RuntimeError("data are not found for interpolation at time:",t,"layer:",k,
                                                       "lat:",i,"lon:",j)
                                  
        else:
            raise ValueError('The input data must be 3d[layer,lat,lon] or 4d[time,layer,lat,lon]')
    else:
        raise ValueError('The pressure levels data (p_level) must be 1d')

    return data_out  

#Calculate monthly anomalies based on a monthly time-series
def cal_anomaly(data):
   
   if data.ndim != 1:
       raise ValueError('The input data must be 1d')
       
   yr_num=int(data.shape[0]/12)
   data_reshape=data.reshape(yr_num,12);data_climatology=np.mean(data_reshape,axis=0)
   data_anomaly=np.zeros((yr_num,12))
   for i in range(yr_num):
       data_anomaly[i,:]=data_reshape[i,:]-data_climatology.copy()
   data_anomaly_line=data_anomaly.reshape(yr_num*12).copy()
   
   return data_anomaly_line

#Calculate grid area