# Author: Denis A. Engemann <denis.engemann@gmail.com>
# License: BSD (3-clause)

import os
import os.path as op
from subprocess import call

from ..io.file_mapping import get_s3_keys_anatomy, get_s3_keys_meg


hcp_prefix = 's3://hcp-openaccess/HCP_900'
subject = '105923'


hcp_data_types = [
    'rest',
    'task_working_memory',
    'task_story_math',
    'task_motor',
    'noise_empty_room'
]


hcp_outputs = [
    'raw',
    'epochs',
    'ica',
    'evoked',
    'trial_info',
    'bads'
]

hcp_cheap = os.getenv('MNE_HCP_CHEAP', False)

hcp_onsets = ['stim']

# allow for downloading fewer data
run_inds = [0, 1, 2]
max_runs = int(os.getenv('MNE_HCP_N_RUNS', 3))
s3_keys = list()

s3_keys += get_s3_keys_meg(
    subject,
    data_types=hcp_data_types,
    onsets=hcp_onsets,
    hcp_path_bucket=hcp_prefix,
    outputs=[dd for dd in hcp_outputs if dd in ('raw',)],
    run_inds=run_inds[:max_runs])

if hcp_cheap:
    s3_keys = [kk for kk in s3_keys if
               'Rest' in kk or ('Rest' not in kk and 'config' in kk)]

s3_keys += get_s3_keys_meg(
    subject,
    data_types=hcp_data_types,
    onsets=hcp_onsets,
    hcp_path_bucket=hcp_prefix,
    outputs=[dd for dd in hcp_outputs if dd in ('epochs')],
    run_inds=run_inds[:max_runs])

s3_keys += get_s3_keys_meg(
    subject,
    data_types=hcp_data_types,
    onsets=hcp_onsets,
    hcp_path_bucket=hcp_prefix,
    outputs=[dd for dd in hcp_outputs if dd not in ('raw', 'epochs')],
    run_inds=run_inds)

s3_keys += get_s3_keys_anatomy(subject, hcp_path_bucket=hcp_prefix)


##############################################################################
# Downloading data

def _download_testing_data():
    """Download testing data.

    .. note:: requires python 2.7
    """
    for s3key in s3_keys:
        new_path = op.dirname(s3key).split(hcp_prefix)[-1][1:]
        new_path = op.join(hcp_path, new_path)
        fname = op.basename(s3key)
        new_file = op.join(new_path, fname)
        if not op.exists(new_path):
            os.makedirs(new_path)
        if not op.exists(new_file):
            print('downloading:\n\tfrom %s\n\tto %s' % (s3key, new_path))
            call(['s3cmd', 'get', s3key, new_path], shell=False)
            assert op.exists(new_file)

##############################################################################
# variable used in different tests

hcp_path = op.expanduser('~/mne-hcp-data/HCP')
subjects_dir = op.expanduser('~/mne-hcp-data/subjects')

bti_chans = {'A' + str(i) for i in range(1, 249, 1)}

test_subject = '105923'
task_types = ['task_story_math', 'task_working_memory', 'task_motor']
noise_types = ['noise_empty_room']
sfreq_preproc = 508.63
sfreq_raw = 2034.5101
lowpass_preproc = 150
highpass_preproc = 1.3

epochs_bounds = {
    'task_motor': (-1.2, 1.2),
    'task_working_memory': (-1.5, 2.5),
    'task_story_math': (-1.5, 4),
    'rest': (0, 2)
}


def nottest(f):
    """Decorator to mark a function as not a test"""
    f.__test__ = False
    return f


@nottest
def expensive_test(f):
    """Decorator for expensive testing"""
    f.expensive_test = True
    return f
