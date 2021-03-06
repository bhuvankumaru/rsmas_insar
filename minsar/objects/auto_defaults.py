## ALL path and default strings used in the program
# Author: Sara Mirzaee

import os
import datetime
import glob


class PathFind:
    def __init__(self):
        self.logdir = os.getenv('OPERATIONS') + '/LOGS'
        self.scratchdir = os.getenv('SCRATCHDIR')
        self.defaultdir = os.path.expandvars('${RSMASINSAR_HOME}/minsar/defaults')
        self.orbitdir = os.path.expandvars('$SENTINEL_ORBITS')
        self.auxdir = os.path.expandvars('$SENTINEL_AUX')
        self.geomasterdir = 'merged/geom_master'
        self.minopydir = 'minopy'
        self.mintpydir = 'mintpy'
        self.rundir = 'run_files'
        self.configdir = 'configs'
        self.mergedslcdir = 'merged/SLC'
        self.mergedintdir = 'merged/interferograms'
        self.geomlatlondir = 'geom_master_noDEM'
        self.wrappercommandtops = 'SentinelWrapper.py -c '
        self.wrappercommandstripmap = 'stripmapWrapper.py -c '
        self.masterdir = 'master'
        self.stackdir = 'stack'
        self.tiffdir = 'image_products'
        self.daskconfig = os.path.expandvars('${RSMASINSAR_HOME}/minsar/defaults/dask/dask.yaml')
        self.auto_template = self.defaultdir + '/minsar_template.cfg'
        return

    def required_template_options(self, acquisition_mode):
        if acquisition_mode == 'tops':
            return ['topsStack.subswath', 'topsStack.boundingBox']
        elif acquisition_mode == 'stripmap':
            return ['stripmapStack.sensor', 'stripmapStack.boundingBox']
        else:
            return None

    def set_isce_defaults(self, inps):

        inps_dict = vars(inps)

        inps_dict['template'][inps.prefix + 'Stack.slcDir'] = inps.work_dir + '/SLC'
        inps_dict['template'][inps.prefix + 'Stack.demDir'] = inps.work_dir + '/DEM'
        inps_dict['template'][inps.prefix + 'Stack.workingDir'] = inps.work_dir

        if 'cleanopt' not in inps.template:
            inps_dict['template']['cleanopt'] = '0'

        if inps.prefix == 'tops':
            inps_dict['template']['topsStack.orbitDir'] = self.orbitdir
            inps_dict['template']['topsStack.auxDir'] = self.auxdir

        return

    @staticmethod
    def grab_cropbox(inps):

        cropbox = inps.template[inps.prefix + 'Stack.boundingBox']
        #if not inps.template['minopy.subset'] == 'None':
        #        cropbox = inps.template['minopy.subset']
        #else:
        #    cropbox = inps.template['topsStack.boundingBox']
        return cropbox

    @staticmethod
    def correct_for_ssara_date_format(template_options):

        inps_dict = template_options
        
        if 'ssaraopt.startDate' in inps_dict:
            inps_dict['ssaraopt.startDate'] = \
                datetime.datetime.strptime(inps_dict['ssaraopt.startDate'], '%Y%m%d').strftime('%Y-%m-%d')
        
        if 'ssaraopt.endDate' in inps_dict:
            inps_dict['ssaraopt.endDate'] = \
                datetime.datetime.strptime(inps_dict['ssaraopt.endDate'], '%Y%m%d').strftime('%Y-%m-%d')
        
        return inps_dict

    @staticmethod
    def isce_clean_list():
        cleanlist = []
        cleanlist.append(['stack',  'misreg', 'orbits', 'coarse_interferograms', 'ESD',
                          'interferograms', 'slaves'])
        cleanlist.append(['merged', 'master', 'coreg_slaves', 'baselines', 'geom_master'])
        cleanlist.append(['SLC'])
        cleanlist.append(['MINTPY', 'run_files', 'configs', 'DEM'])

        return cleanlist

    @staticmethod
    def get_email_file_list():

        fileList = ['velocity.png', 'avgSpatialCoherence.png', 'temporalCoherence.png', 'maskTempCoh.png', 'mask.png',
                     'demRadar_error.png', 'velocityStd.png', 'geo_velocity.png', 'coherence*.png', 'unwrapPhase*.png',
                     'rms_timeseriesResidual_quadratic.pdf', 'CoherenceHistory.pdf', 'CoherenceMatrix.pdf',
                     'bl_list.txt', 'Network.pdf', 'geo_velocity_masked.kmz', 'timeseries*.png', 'geo_timeseries*.png']
        return fileList

    @staticmethod
    def get_geom_master_lists():
        list_geo = ['lat', 'lon', 'los', 'hgt', 'shadowMask', 'incLocal']
        return list_geo

    @staticmethod
    def correct_for_isce_naming_convention(inps):

        inps_dict = {}
        for item in inps.template:
            if item.startswith('topsStack') or item.startswith('stripmapStack'):
                inps_dict[item] = inps.template[item]

        if 'stripmap' in inps.template['acquisition_mode']:
            stackprefix = 'stripmapStack'

            isceKey = ['slc_directory', 'working_directory', 'dem', 'bbox', 'master_date', 'time_threshold',
                       'baseline_threshold', 'azimuth_looks', 'range_looks', 'sensor', 'low_band_frequency',
                       'high_band_frequency', 'subband_bandwidth', 'unw_method', 'filter_strength',
                       'filter_sigma_x', 'filter_sigma_y', 'filter_size_x', 'filter_size_y', 'filter_kernel_rotation',
                       'workflow', 'applyWaterMask', 'zero', 'nofocus', 'text_cmd', 'useGPU']

            templateKey = ['slcDir', 'workingDir', 'demDir', 'boundingBox', 'master', 'timeThreshold',
                           'baselineThreshold', 'azimuthLooks', 'rangeLooks', 'sensor',
                           'LowBandFrequency', 'HighBandFrequency', 'subbandBandwith', 'unwMethod',
                           'golsteinFilterStrength', 'filterSigmaX', 'filterSigmaY', 'filterSizeX', 'filterSizeY',
                           'filterKernelRotation', 'workflow', 'watermask', 'zerodop', 'nofocus', 'textCmd', 'useGPU']

        else:
            stackprefix = 'topsStack'

            isceKey = ['slc_directory', 'orbit_directory', 'aux_directory', 'working_directory', 'dem', 'master_date',
                       'num_connections', 'num_overlap_connections', 'swath_num', 'bbox', 'text_cmd', 'exclude_dates',
                       'include_dates', 'azimuth_looks', 'range_looks', 'filter_strength', 'esd_coherence_threshold',
                       'snr_misreg_threshold', 'unw_method', 'polarization', 'coregistration', 'workflow', 'start_date',
                       'stop_date', 'useGPU', 'rmFilter']

            templateKey = ['slcDir', 'orbitDir', 'auxDir', 'workingDir', 'demDir', 'master', 'numConnections',
                           'numOverlapConnections', 'subswath', 'boundingBox', 'textCmd', 'excludeDates',
                           'includeDates', 'azimuthLooks', 'rangeLooks', 'filtStrength', 'esdCoherenceThreshold',
                           'snrMisregThreshold', 'unwMethod', 'polarization', 'coregistration', 'workflow', 'startDate',
                           'stopDate', 'useGPU', 'rmFilter']

        templateKey = [stackprefix + '.' + x for x in templateKey]

        for old_key, new_key in zip(templateKey, isceKey):
            inps_dict[new_key] = inps_dict.pop(old_key)
            if inps_dict[new_key] == 'None':
                inps_dict[new_key] = None

        if stackprefix == 'topsStack':
            if not inps_dict['start_date'] in [None, 'auto']:
                print(inps_dict['start_date'])
                inps_dict['start_date'] = datetime.datetime.strptime(inps_dict['start_date'],
                                                                                '%Y%m%d').strftime('%Y-%m-%d')
            if not inps_dict['stop_date'] in [None, 'auto']:
                inps_dict['stop_date'] = datetime.datetime.strptime(inps_dict['stop_date'],
                                                                           '%Y%m%d').strftime('%Y-%m-%d')

        return inps_dict

    @staticmethod
    def process_rsmas_help():

        STEP_LIST = [
            'download',
            'dem',
            'ifgrams',
            'timeseries',
            'insarmaps',
            'imageProducts',
        ]

        STEP_HELP = """Command line options for steps processing with names are chosen from the following list:
            {}

            In order to use either --start or --step, it is necessary that a
            previous run was done using one of the steps options to process at least
            through the step immediately preceding the starting step of the current run.
            
            """.format(STEP_LIST[0:6])

        return STEP_LIST, STEP_HELP

    @staticmethod
    def minopy_help():

        STEP_LIST = [
            'crop',
            'patch',
            'inversion',
            'ifgrams',
            'unwrap',
            'mintpy',
            'email']

        STEP_HELP = """Command line options for steps processing with names are chosen from the following list:
                {}
                
                In order to use either --start or --step, it is necessary that a
                previous run was done using one of the steps options to process at least
                through the step immediately preceding the starting step of the current run.
                """.format(STEP_LIST[0:7])

        return STEP_LIST, STEP_HELP

    @staticmethod
    def minopy_corrections():

        runSteps = ['load_data',
                    'modify_network',
                    'reference_point',
                    'stack_interferograms',
                    'correct_unwrap_error',
                    'correct_troposphere',
                    'deramp',
                    'correct_topography',
                    'residual_RMS',
                    'reference_date',
                    'velocity',
                    'geocode',
                    'google_earth',
                    'hdfeos5']

        return runSteps

    



