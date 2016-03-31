__author__ = 'matt'

"""
Bar chart demo with pairs of bars grouped for easy comparison.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#corps = [('NT', (0, 1, 2, 3, 4, 5)), ('LXX', (0, 1, 2, 3, 4, 5)), ('Josephus', (0, 1, 2, 3, 4, 5)), ('Philo', (0, 1, 2, 3, 4, 5)), ('Plutarch', (0, 1, 2, 3, 4, 5)), ('Perseus', (0, 1, 2, 3, 4, 5))]

corps = pd.DataFrame(np.random.random(size=(6, 6)), index=['NT', 'LXX', 'Josephus', 'Philo', 'Plutarch', 'Perseus'], columns=['NT', 'LXX', 'Josephus', 'Philo', 'Plutarch', 'Perseus'])

fig, ax = plt.subplots()

index = np.arange(len(corps))*1.2
bar_width = 0.15

opacity = 0.4
#error_config = {'ecolor': '0.3'}
mult = 0

for corp in corps:
    rects = plt.bar(index + bar_width * mult, corps.ix[corp], bar_width, color='.9', label=corp)
    rects.remove()
    for i, rect in enumerate(rects):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height / 2, corp, size='small', rotation='vertical', ha='center', va='bottom')
    mult += 1

plt.xlabel('Group')
plt.ylabel('Scores')
plt.title('Scores by group and gender')
plt.xticks(index + 3 * bar_width, [x for x in corps])
plt.savefig('cs_corps_test.png', dpi=500)