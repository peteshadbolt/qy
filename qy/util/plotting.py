from matplotlib import pyplot as plt
import numpy as np

alphabet='abcdefghijklmnopqrstuvwxyz'.upper()
detector_labels=dict(zip(range(len(alphabet)), alphabet))

def easy_label(label): return ''.join(map(lambda x: detector_labels[x], label))

def get_total(arrays):
    n=len(arrays[0])
    total=np.zeros(n)
    for array in arrays:
        total+=array[:, -1]
    return total

def bar_plot(y):
    n=len(y)
    plt.bar(range(n), y, color='#5555cc', lw=1)
    plt.xlim(0, n)

def plot_once(file_list):
    arrays=map(np.load, file_list) 
    total=get_total(arrays)
    labels=map(easy_label, arrays[0][:, :-1].tolist())
    bar_plot(total)
    if len(labels)<30:
        plt.xticks(np.arange(n)+.5, labels, rotation=90, fontsize=8)
    else:
        plt.xticks([])

def compare(list1, list2, filename):
    plt.clf()
    plt.figure(figsize=(10,6))
    plt.suptitle(filename)
    plt.subplot(211)
    plot_once(list1)
