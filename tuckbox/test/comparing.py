import os
import glob
import sys
from functools import reduce
from wand.image import Image, COMPARE_METRICS

folder1 = 'good'
folder2 = 'bad'

filenames = list(map(lambda x: os.path.split(x)[1], glob.glob(os.path.join(os.path.dirname(__file__), folder2, "*.png"))))

metrics_to_use = list(filter(lambda x: x not in ['normalized_cross_correlation'], COMPARE_METRICS))

results = [[0.0 for i in range(len(filenames))] for j in range(len(metrics_to_use))]
name_lengths = [len(filename) for filename in filenames]

metric_max_length = reduce(max, [len(metric) for metric in metrics_to_use])

first_row_format = ' ' * metric_max_length + '\t' + '\t'.join('{{:{}}}'.format(x) for x in name_lengths)
row_format = '{{:{}}}'.format(metric_max_length) + '\t' + '\t'.join('{{:{}.{}f}}'.format(x-3, 3) for x in name_lengths)

for index_f, f in enumerate(filenames):
    image1 = Image(filename=os.path.join(os.path.dirname(__file__), folder1, f))
    image2 = Image(filename=os.path.join(os.path.dirname(__file__), folder2, f))

    image1.resize(image2.width, image2.height)

    for index_m, m in enumerate(metrics_to_use):
        _, compare_metric = image1.compare(image2, metric=m)
        
        results[index_m][index_f] = compare_metric

print(first_row_format.format(*filenames))
str_table = [row_format.format(metrics_to_use[r], *row) for r, row in enumerate(results)]
print('\n'.join(str_table))