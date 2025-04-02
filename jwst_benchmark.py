#!/usr/bin/env python
import os
import sys
from jwst.pipeline import Detector1Pipeline

def run_benchmark(uncal_file='jw01121002001_02101_00001_nrs2_uncal.fits',
    cores="1", test='ramp_fit', ramp_method='OLS_C'):

    det1 = Detector1Pipeline()  # Instantiate the pipeline

    if 'ols' in ramp_method.lower():
        algorithm='OLS_C'
    elif 'like' in ramp_method.lower():
        algorithm='LIKELY'

    step_parameters = {
        'group_scale': {'skip': True},
        'superbias': {'skip': True},
        'linearity': {'skip': True},
        'gain_scale': {'skip': True},
        'charge_migration': {'skip': True},
        'clean_flicker_noise': {'skip': True},
        'dark_current': {'skip': True},
        'saturation': {'skip': True},  # check for saturated pixels, but do not expand to adjacent pixels
        'persistence': {'skip': True},
        'jump': {'skip':True, 'maximum_cores': str(cores)},  # parallelize
        'ramp_fit': {'maximum_cores': str(cores), 'algorithm': algorithm},  # parallelize
    }

    if test=='ramp_fit':
        step_parameters['jump']['skip']=True
        step_parameters['ramp_fit']['skip']=False
    elif test=='jump':
        step_parameters['jump']['skip']=False
        step_parameters['ramp_fit']['skip']=True

    det1.call(uncal_file, save_results=True, output_dir='.',
        steps=step_parameters)

    if os.path.exists(uncal_file.replace('uncal.fits','rate.fits')):
        os.remove(uncal_file.replace('uncal.fits','rate.fits'))
    if os.path.exists(uncal_file.replace('uncal.fits','rateints.fits')):
        os.remove(uncal_file.replace('uncal.fits','rateints.fits'))


if __name__ == "__main__":
    ncores = str(sys.argv[1])
    test = str(sys.argv[2])
    ramp_method = str(sys.argv[3])
    run_benchmark(cores=ncores, test=test, ramp_method=ramp_method)
