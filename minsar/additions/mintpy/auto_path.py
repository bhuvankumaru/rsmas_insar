#!/usr/bin/env python3
############################################################
# Program is part of MintPy                                #
# Copyright (c) 2013, Zhang Yunjun, Heresh Fattahi         #
# Author: Zhang Yunjun, Mar 2018                           #
############################################################


import os
import re
import glob
import numpy as np

# Auto setting for file structure of Univ. of Miami, as shown below.
# It required 3 conditions: 1) autoPath = True
#                           2) $SCRATCHDIR is defined in environmental variable
#                           3) input custom template with basename same as project_name
# Change it to False if you are not using it.
autoPath = True


# Default path of data files from different InSAR processors to be loaded into MintPy
isceAutoPath = '''##----------Default file path of ISCE-topsStack products
mintpy.load.processor      = isce
mintpy.load.metaFile       = ${PROJECT_DIR}/master/IW*.xml
mintpy.load.baselineDir    = ${PROJECT_DIR}/baselines

mintpy.load.unwFile        = ${PROJECT_DIR}/merged/interferograms/*/filt*.unw
mintpy.load.corFile        = ${PROJECT_DIR}/merged/interferograms/*/filt*.cor
mintpy.load.connCompFile   = ${PROJECT_DIR}/merged/interferograms/*/filt*.unw.conncomp
mintpy.load.ionoFile       = None
mintpy.load.intFile        = None

mintpy.load.demFile        = ${PROJECT_DIR}/merged/geom_master/hgt.rdr
mintpy.load.lookupYFile    = ${PROJECT_DIR}/merged/geom_master/lat.rdr
mintpy.load.lookupXFile    = ${PROJECT_DIR}/merged/geom_master/lon.rdr
mintpy.load.incAngleFile   = ${PROJECT_DIR}/merged/geom_master/los.rdr
mintpy.load.azAngleFile    = ${PROJECT_DIR}/merged/geom_master/los.rdr
mintpy.load.shadowMaskFile = ${PROJECT_DIR}/merged/geom_master/shadowMask.rdr
mintpy.load.bperpFile      = None
'''
iscestripmapAutoPath = '''##----------Default file path of ISCE-topsStack products
mintpy.load.processor      = isce
mintpy.load.metaFile       = ${PROJECT_DIR}/masterShelve/data.dat
mintpy.load.baselineDir    = ${PROJECT_DIR}/baselines

mintpy.load.unwFile        = ${PROJECT_DIR}/Igrams/*/filt*.unw
mintpy.load.corFile        = ${PROJECT_DIR}/Igrams/*/filt*.cor
mintpy.load.connCompFile   = ${PROJECT_DIR}/Igrams/*/filt*.unw.conncomp
mintpy.load.ionoFile       = None
mintpy.load.intFile        = None

mintpy.load.demFile        = ${PROJECT_DIR}/geom_master/hgt.rdr
mintpy.load.lookupYFile    = ${PROJECT_DIR}/geom_master/lat.rdr
mintpy.load.lookupXFile    = ${PROJECT_DIR}/geom_master/lon.rdr
mintpy.load.incAngleFile   = ${PROJECT_DIR}/geom_master/los.rdr
mintpy.load.azAngleFile    = ${PROJECT_DIR}/geom_master/los.rdr
mintpy.load.shadowMaskFile = ${PROJECT_DIR}/geom_master/shadowMask.rdr
mintpy.load.bperpFile      = None
'''

roipacAutoPath = '''##----------Default file path of ROI_PAC products
mintpy.load.processor      = roipac
mintpy.load.unwFile        = ${PROJECT_DIR}/PROCESS/DONE/IFG*/filt*.unw
mintpy.load.corFile        = ${PROJECT_DIR}/PROCESS/DONE/IFG*/filt*.cor
mintpy.load.connCompFile   = ${PROJECT_DIR}/PROCESS/DONE/IFG*/filt*snap_connect.byt
mintpy.load.intFile        = None

mintpy.load.demFile        = ${PROJECT_DIR}/PROCESS/DONE/*${m_date12}*/radar_*rlks.hgt
mintpy.load.lookupYFile    = ${PROJECT_DIR}/PROCESS/GEO/geo_${m_date12}/geomap_*rlks.trans
mintpy.load.lookupXFile    = ${PROJECT_DIR}/PROCESS/GEO/geo_${m_date12}/geomap_*rlks.trans
mintpy.load.incAngleFile   = None
mintpy.load.azAngleFile    = None
mintpy.load.shadowMaskFile = None
mintpy.load.bperpFile      = None
'''

gammaAutoPath = '''##----------Default file path of GAMMA products
mintpy.load.processor      = gamma
mintpy.load.unwFile        = ${PROJECT_DIR}/PROCESS/DONE/IFG*/diff*rlks.unw
mintpy.load.corFile        = ${PROJECT_DIR}/PROCESS/DONE/IFG*/*filt*rlks.cor
mintpy.load.connCompFile   = None
mintpy.load.intFile        = None

mintpy.load.demFile        = ${PROJECT_DIR}/PROCESS/SIM/sim_${m_date12}/sim*.hgt_sim
mintpy.load.lookupYFile    = ${PROJECT_DIR}/PROCESS/SIM/sim_${m_date12}/sim*.UTM_TO_RDC
mintpy.load.lookupXFile    = ${PROJECT_DIR}/PROCESS/SIM/sim_${m_date12}/sim*.UTM_TO_RDC
mintpy.load.incAngleFile   = None
mintpy.load.azAngleFile    = None
mintpy.load.shadowMaskFile = None
mintpy.load.bperpFile      = ${PROJECT_DIR}/merged/baselines/*/*.base_perp
'''

autoPathDict = {
    'isce'  : isceAutoPath,
    'iscestripmap' : iscestripmapAutoPath,
    'roipac': roipacAutoPath,
    'gamma' : gammaAutoPath,
}

prefix = 'mintpy.load.'


##----------------- Functions from mintpy.utils.readfile to be independnt module ---------##
def read_str2dict(inString, delimiter='=', print_msg=False):
    '''Read multiple lines of string into dict
    Based on mintpy.utils.readfile.read_template()
    '''
    strDict = {}
    lines = inString.split('\n')
    for line in lines:
        c = [i.strip() for i in line.strip().split(delimiter, 1)]
        if len(c) < 2 or line.startswith(('%', '#')):
            next
        else:
            key = c[0]
            value = str.replace(c[1], '\n', '').split("#")[0].strip()
            if value != '':
                strDict[key] = value

    # set 'None' to None
    for key, value in strDict.items():
        if value.lower() == 'none':
            strDict[key] = None
    return strDict


##----------------------------------------------------------------------------------------##
def get_auto_path(processor, project_name, template=dict()):
    """Update template options with auto path defined in autoPathDict
    Parameters: processor : str, isce / roipac / gamma
                project_name : str, Project name, e.g. GalapagosSenDT128
                template : dict, 
    Returns:    template : dict,
    """
    # read auto_path_dict
    if processor== 'isce' and template['acquisition_mode']=='stripmap':
        processor='iscestripmap'
    auto_path_dict = read_str2dict(autoPathDict[processor], print_msg=False)

    # grab variable value: SCRATCHDIR, m_date12
    project_dir = os.path.join(os.getenv('SCRATCHDIR'), project_name)
    m_date12 = None
    if processor in ['roipac', 'gamma']:
        m_date12 = get_master_date12(project_dir, processor=processor)
        if m_date12 and processor == 'roipac':
            # determine nlooks in case both radar_2rlks.hgt and radar_8rlks.hgt exist.
            lookup_file = os.path.join(project_dir, 'PROCESS/GEO/geo_{}/geomap*.trans'.format(m_date12))
            lks = re.findall('_\d+rlks', glob.glob(lookup_file)[0])[0]
            dem_file = os.path.join('${PROJECT_DIR}/PROCESS/DONE/*${m_date12}*', 'radar{}.hgt'.format(lks))
            auto_path_dict[prefix+'demFile'] = dem_file

    var_dict = {}
    var_dict['${PROJECT_DIR}'] = project_dir
    if m_date12:
        var_dict['${m_date12}'] = m_date12

    # update auto_path_dict
    for key, value in auto_path_dict.items():
        if value:
            for var1, var2 in var_dict.items():
                value = value.replace(var1, var2)    
            auto_path_dict[key] = value

    # update template option with auto value
    for key, value in auto_path_dict.items():
        if value and template[key] == 'auto':
            template[key] = value
    return template


def get_master_date12(project_dir, processor='roipac'):
    """date12 of reference interferogram in YYMMDD-YYMMDD format"""
    m_date12 = None

    # opt 1 - master_ifgram.txt
    m_ifg_file = os.path.join(project_dir, 'PROCESS', 'master_ifgram.txt')
    if os.path.isfile(m_ifg_file):
        m_date12 = str(np.loadtxt(m_ifg_file, dtype=bytes).astype(str))
        return m_date12

    # opt 2 - folders under GEO/SIM
    if processor == 'roipac':
        try:
            lookup_file = glob.glob(os.path.join(project_dir, 'PROCESS/GEO/geo_*/geomap*.trans'))[0]
            m_date12 = re.findall('\d{6}-\d{6}', lookup_file)[0]
        except:
            print("No master interferogram found! Check the PROCESS/GEO/geo_* folder")

    elif processor == 'gamma':
        geom_dir = os.path.join(project_dir, 'PROCESS/SIM')
        try:
            m_date12 = os.walk(geom_dir).next()[1][0].split('sim_')[1]
        except:
            print("No master interferogram found! Check the PROCESS/SIM/sim_* folder")
    return m_date12
