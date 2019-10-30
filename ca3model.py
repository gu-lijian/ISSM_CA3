# -*- coding: utf-8 -*-
"""CA3data1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yiYoWA1sOAuClB_WKXB4QwbQwWdww8oT
"""

# Commented out IPython magic to ensure Python compatibility.
# Load necessary packages
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import pywt
import pandas as pd
import time
from sklearn.neural_network import MLPClassifier 
from sklearn.metrics import confusion_matrix
from warnings import filterwarnings # Avoid training warning message in MLPClassifier
filterwarnings('ignore')
import time
import csv
from enum import Enum
from scipy.signal import butter, filtfilt


WINDOW_SIZE = 10 * 30 - 15
DURATION = 30
VERBOSE = False
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 3600 * 24

Path_to_file = 'D:\GoogleDrive\MTech\Courses\ISY5002 Pattern Recognition Systems\Intelligent Sensing & Sense Making\CA3\sleep_classifiers-master\data\\'
Path_to_clearned_file = 'D:\GoogleDrive\MTech\Courses\ISY5002 Pattern Recognition Systems\Intelligent Sensing & Sense Making\CA3\sleep_classifiers-master\cleaneddata\\'

# Load data from Excel
# from google.colab import drive
# drive.mount('/content/data')

# def get_all_subject_ids():
#     train_subjects_as_ints = [1360686]
#     '''subjects_as_ints = [3509524, 5132496, 1066528, 5498603, 2638030, 2598705, 5383425, 1455390, 4018081, 9961348,
#                         1449548, 8258170, 781756, 9106476, 8686948, 8530312, 3997827, 4314139, 1818471, 4426783,
#                         8173033, 7749105, 5797046, 759667, 8000685, 6220552, 844359, 9618981, 1360686, 46343,
#                         8692923] '''
#     subjects_as_strings = []
#
#     for subject in train_subjects_as_ints:
#         subjects_as_strings.append(str(subject))
#     return subjects_as_strings

def get_all_train_subject_ids():
    train_subjects_as_ints = [1066528]
    '''subjects_as_ints = [3509524, 5132496, 1066528, 5498603, 2638030, 2598705, 5383425, 1455390, 4018081, 9961348,
                        1449548, 8258170, 781756, 9106476, 8686948, 8530312, 3997827, 4314139, 1818471, 4426783,
                        8173033, 7749105, 5797046, 759667, 8000685, 6220552, 844359, 9618981, 1360686, 46343,
                        8692923] '''
    train_subjects_as_strings = []

    for subject in train_subjects_as_ints:
        train_subjects_as_strings.append(str(subject))
    return train_subjects_as_strings

def get_all_test_subject_ids():
    test_subjects_as_ints = [1360686]
    '''subjects_as_ints = [3509524, 5132496, 1066528, 5498603, 2638030, 2598705, 5383425, 1455390, 4018081, 9961348,
                        1449548, 8258170, 781756, 9106476, 8686948, 8530312, 3997827, 4314139, 1818471, 4426783,
                        8173033, 7749105, 5797046, 759667, 8000685, 6220552, 844359, 9618981, 1360686, 46343,
                        8692923] '''
    test_subjects_as_strings = []

    for subject in test_subjects_as_ints:
        test_subjects_as_strings.append(str(subject))
    return test_subjects_as_strings

def load_data(subject_id):
    # Load data from csv
    psg_output_path = Path_to_clearned_file + subject_id + '_cleaned_psg.csv'
    hr_output_path = Path_to_clearned_file + subject_id + '_cleaned_heartrate.csv'
    counts_output_path = Path_to_clearned_file + subject_id + '_cleaned_counts.txt'
    motion_output_path = Path_to_clearned_file + subject_id + '_cleaned_motion.csv'

    psg = pd.read_csv(psg_output_path, header=None)
    hr = pd.read_csv(hr_output_path, header=None)
    counts = pd.read_csv(counts_output_path, header=None)
    motion = pd.read_csv(motion_output_path, header=None)

    time_psg = psg[0].values
    time_hr = hr[0].values
    time_motion = motion[0].values
    time_counts = counts[0].values
    signal_psg = psg[1].values
    signal_hr = hr[1].values
    signal_motion = motion[1].values
    signal_counts = counts[1].values

    plt.plot(time_counts, signal_counts)
    plt.title('Original counts data')
    plt.show()
    print(time_counts.shape)

    plt.plot(time_psg, signal_psg)
    plt.title('Original psg data')
    plt.show()
    print(time_psg.shape)

    plt.plot(time_hr, signal_hr)
    plt.title('Original heart rate data')
    plt.show()
    print(time_hr.shape)

    plt.plot(time_motion, signal_motion)
    plt.title('Original motion data')
    plt.show()
    print(time_motion.shape)

    # Decompose wave
    decompose_wave(signal_psg, "PSG");
    decompose_wave(signal_hr, "Heart Rate");
    decompose_wave(signal_motion, "Motion");
    decompose_wave(signal_counts, "Step Counts");

def decompose_wave(orig_singal, signal_name):
    waveletname = 'db4'
    waveletlevel = 2

    # Step 1: Perform wavelet decomposition
    coeffs_orig = pywt.wavedec(orig_singal, waveletname, level=waveletlevel)
    coeffs_filter = coeffs_orig.copy()

    # Step 2: Perform thresholding on the wavelet coefficients
    # Set the threshold
    threshold = 0.8

    for i in range(1, len(coeffs_orig)):
        coeffs_filter[i] = pywt.threshold(coeffs_orig[i], threshold*max(coeffs_orig[i]))

    # Step 3: Perform reconstruction on the filered coefficients
    signal_denoised = pywt.waverec(coeffs_filter, waveletname)

    # Step 4: Plot and compare the original signal and the denoised signal
    plt.figure()
    plt.plot(orig_singal, 'g', label='Original ' + signal_name + ' signal')
    plt.plot(signal_denoised, 'r', label='Denoised ' + signal_name + ' signal')
    plt.legend()
    plt.show()

# Define the feature extraction method for each subband
def calculate_statistics(list_values):
    mean = np.nanmean(list_values)
    std = np.nanstd(list_values)
    var = np.nanvar(list_values)
    return [mean, std, var]

# Define feature extraction methods
def get_features(list_values):
    statistics = calculate_statistics(list_values)
    return statistics

def get_sleeping_features(dataset, labels, waveletname):
    sleeping_features = []
    for signal_no in range(0, len(dataset)):

        if ((signal_no % 500) == 0):
            print('get_sleeping_features, loop %d/%d' % (signal_no, len(dataset)))
        features = []
        # for signal_comp in range(0, len(dataset[signal_no])):
        signal = dataset[signal_no]
        list_coeff = pywt.wavedec(signal, waveletname)
        for coeff in list_coeff:
            features += get_features(coeff)
        sleeping_features.append(features)
    X = np.array(sleeping_features)
    Y = np.array(labels)
    return X, Y

def load_label(subject_id):
    # Load label from psg csv
    psg_output_path = Path_to_clearned_file + subject_id + '_cleaned_psg.csv'
    psg = pd.read_csv(psg_output_path, header=None)
    label_psg = psg[1].values
    return label_psg

def load_normalize_signal(subject_id, label):
    # Load label from heart rate csv
    hr_output_path = Path_to_clearned_file + subject_id + '_cleaned_heartrate.csv'
    counts_output_path = Path_to_clearned_file + subject_id + '_cleaned_counts.txt'
    motion_output_path = Path_to_clearned_file + subject_id + '_cleaned_motion.csv'
    hr = pd.read_csv(hr_output_path, header=None)
    counts = pd.read_csv(counts_output_path, header=None)
    motion = pd.read_csv(motion_output_path, header=None)
    signal_hr = hr[1].values
    signal_counts = counts[1].values
    signal_motion_x = motion[1].values
    signal_motion_y = motion[2].values
    signal_motion_z = motion[3].values
    if len(signal_hr) > len(label):
        hr_multiple = len(signal_hr) / len(label)
        counts_multiple = len(signal_counts) / len(label)
        motion_multiple = len(signal_motion_x) / len(label)
        normalized_signal = [];
        for index in range(0, len(label)) :
            signals_arr = [];
            signals_arr.append(signal_hr[int(index * hr_multiple)])
            signals_arr.append(signal_counts[int(index * counts_multiple)])
            signals_arr.append(signal_motion_x[int(index * motion_multiple)])
            signals_arr.append(signal_motion_y[int(index * motion_multiple)])
            signals_arr.append(signal_motion_z[int(index * motion_multiple)])
            normalized_signal.append(signals_arr);

    return normalized_signal

def run_modeling(train_subject_set, test_subject_set):
    start_time = time.time()

    for train_subject in train_subject_set:
        print("Load cleaned training data from subject " + str(train_subject) + "...")
        # load_data(str(train_subject))
        train_label = load_label(str(train_subject))
        train_signal = load_normalize_signal(str(train_subject), train_label)

    for test_subject in test_subject_set:
        print("Load cleaned testing data from subject " + str(test_subject) + "...")
        # load_data(str(test_subject))
        test_label = load_label(str(test_subject))
        test_signal = load_normalize_signal(str(train_subject), test_label)

    # Extract features for both train and test signals
    start = time.time()

    waveletname = 'db4'
    print('Generate features for training data')
    X_train, Y_train = get_sleeping_features(train_signal, np.array(train_label), waveletname)
    print('Generate features for testing data')
    X_test, Y_test = get_sleeping_features(test_signal, np.array(test_label), waveletname)

    end = time.time()
    print('Time needed: %.2f seconds' % (end - start))

    end_time = time.time()
    print("Execution took " + str((end_time - start_time) / 60) + " minutes")

    # Perform classification
    # use the default setting of MLPClassifier
    clf = MLPClassifier()
    clf.fit(X_train, Y_train)
    test_score = clf.score(X_test, Y_test)

    print('Classification accuracy for test data set: %.4f' % test_score)
    stage_label = ['WAKE', 'N1', 'N2', 'N3', 'N4', 'REM']

    Y_predict = clf.predict(X_test)
    print(pd.DataFrame(confusion_matrix(Y_test, Y_predict), index=stage_label, columns=stage_label))

# Start to run here
train_subject_ids = get_all_train_subject_ids()
test_subject_ids = get_all_test_subject_ids()
run_modeling(train_subject_ids, test_subject_ids)