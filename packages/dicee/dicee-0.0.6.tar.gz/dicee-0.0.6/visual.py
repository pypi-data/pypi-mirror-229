import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import seaborn as sns

# sns.set(style="whitegrid")
pd.set_option('display.max_columns', None)

directory = "UMLS-P"
sub_folder_str_paths = os.listdir(directory)


def get_epoch_losses(path):
    for i in path:
        di = directory + "/" + i
        for j in os.listdir(di):
            if j == "summary.csv":
                continue
            dij = di + "/" + j
            for z in os.listdir(dij):
                if z == "epoch_losses.csv":
                    df = pd.read_csv(f"{dij}/epoch_losses.csv", index_col=0).values
                    plt.plot(df)
        plt.show()


# get_epoch_losses(sub_folder_str_paths)


def get_summaries(sub_folder_str_paths):
    summaries = []
    for i in sub_folder_str_paths:
        for j in os.listdir(directory + "/" + i):
            if j == "summary.csv":
                df = pd.read_csv(f"{directory}/{i}/summary.csv", index_col=0)
                summaries.append(df)

    df = pd.concat(summaries)
    df.sort_values(by=['test_mrr'], ascending=False, inplace=True)

    df["model_name"] = df["model_name"].str.replace("Pykeen_QuatE", "QuatE")
    df["model_name"] = df["model_name"].str.replace("Pykeen_TransE", "TransE")
    return df


df = get_summaries(sub_folder_str_paths)
conditions = [
    (df['callbacks'] == "{}"),
    (df['callbacks'].str.contains("'level': 'input'")),
    (df['callbacks'].str.contains("'level': 'param'")),
    (df['callbacks'].str.contains("'level': 'out'")),
]

values = ["Base", "Input", "Param", "Out"]

# create a new column and use np.select to assign values to it using our lists as arguments
df["label"] = np.select(conditions, values)

sub_df = df[["model_name", "train_mrr", "test_mrr", "callbacks", "label"]]


sns.boxplot(data=sub_df, x="label", y="test_mrr",order=values)
ax=sns.swarmplot(data=sub_df, x="label", y="test_mrr",# hue="model_name",
                 order=values,c="black")
# remove legend from axis 'ax'
#ax.legend_.remove()
plt.ylim(0.0, 1.1)
plt.xlabel("")
plt.ylabel("MRR")
plt.title("Test MRR performances")
plt.savefig('test_robust.pdf')
plt.show()

sns.boxplot(data=sub_df, x="label", y="train_mrr",order=values)
ax=sns.swarmplot(data=sub_df, x="label", y="train_mrr",# hue="model_name",
                 order=values,c="black")
# remove legend from axis 'ax'
#ax.legend_.remove()
plt.ylim(0.0, 1.1)
plt.xlabel("")
plt.ylabel("MRR")
plt.title("Train MRR performances")
plt.savefig('train_robust.pdf')
plt.show()
exit(1)

test_kge_mrr = sub_df[sub_df["label"] == "Base"]["test_mrr"].to_numpy()

test_kge_in_perturb = sub_df[sub_df["label"] == "Input"]["test_mrr"].to_numpy()
test_kge_param_perturb = sub_df[sub_df["label"] == "Param"]["test_mrr"].to_numpy()
test_kge_out_perturb = sub_df[sub_df["label"] == "Out"]["test_mrr"].to_numpy()

# Multiple box plots on one Axes
# fig, ax = plt.subplots()

# ax = sns.boxplot(x="day", y="total_bill", data=tips, showfliers = False)
# ax = sns.swarmplot(x="day", y="total_bill", data=tips, color=".25")

ax = sns.boxplot(data=[test_kge_mrr, test_kge_in_perturb, test_kge_param_perturb, test_kge_out_perturb],
                 # order=["Base", "Input", "Param", "Out"]
                 )
print(ax)
ax = sns.swarmplot(data=[test_kge_mrr, test_kge_in_perturb, test_kge_param_perturb, test_kge_out_perturb],
                   color=".25"
                   # labels=["Base", "Input", "Param", "Out"],
                   )
# fig.supylabel('Test MRR')
# plt.savefig('test_robust.pdf')
plt.show()
exit(1)
fig, ax = plt.subplots()
ax.boxplot([train_kge_mrr, train_kge_in_perturb, train_kge_param_perturb, train_kge_out_perturb], sym='gD',
           labels=["Base", "Input", "Param", "Out"])
fig.supylabel('Train MRR')
plt.savefig('train_robust.pdf')
plt.show()
exit(1)

# Fixing random state for reproducibility
np.random.seed(19680801)

# fake up some data
spread = np.random.rand(50) * 100
center = np.ones(25) * 50
flier_high = np.random.rand(10) * 100 + 100
flier_low = np.random.rand(10) * -100
data = np.concatenate((spread, center, flier_high, flier_low))
"""
fig, axs = plt.subplots(2, 3)

# basic plot
axs[0, 0].boxplot(data)
axs[0, 0].set_title('basic plot')

# notched plot
axs[0, 1].boxplot(data, 1)
axs[0, 1].set_title('notched plot')

# change outlier point symbols
axs[0, 2].boxplot(data, 0, 'gD')
axs[0, 2].set_title('change outlier\npoint symbols')

# don't show outlier points
axs[1, 0].boxplot(data, 0, '')
axs[1, 0].set_title("don't show\noutlier points")

# horizontal boxes
axs[1, 1].boxplot(data, 0, 'rs', 0)
axs[1, 1].set_title('horizontal boxes')

# change whisker length
axs[1, 2].boxplot(data, 0, 'rs', 0, 0.75)
axs[1, 2].set_title('change whisker length')

fig.subplots_adjust(left=0.08, right=0.98, bottom=0.05, top=0.9,
                    hspace=0.4, wspace=0.3)
"""

# fake up some more data
spread = np.random.rand(50) * 100
center = np.ones(25) * 40
flier_high = np.random.rand(10) * 100 + 100
flier_low = np.random.rand(10) * -100
d2 = np.concatenate((spread, center, flier_high, flier_low))
# Making a 2-D array only works if all the columns are the
# same length.  If they are not, then use a list instead.
# This is actually more efficient because boxplot converts
# a 2-D array into a list of vectors internally anyway.
data = [data, d2, d2[::2]]

# Multiple box plots on one Axes
fig, ax = plt.subplots()
ax.boxplot(data)

plt.show()
exit(1)

df = pd.read_csv("UMLS-ComplEx-Perturb/summary.csv", index_col=0)

print(df.head())
exit(1)

# https://matplotlib.org/stable/gallery/statistics/boxplot_demo.html
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

random_dists = ['Normal(1, 1)', 'Lognormal(1, 1)', 'Exp(1)', 'Gumbel(6, 4)',
                'Triangular(2, 9, 11)']
N = 500

norm = np.random.normal(1, 1, N)
logn = np.random.lognormal(1, 1, N)
expo = np.random.exponential(1, N)
gumb = np.random.gumbel(6, 4, N)
tria = np.random.triangular(2, 9, 11, N)

# Generate some random indices that we'll use to resample the original data
# arrays. For code brevity, just use the same random indices for each array
bootstrap_indices = np.random.randint(0, N, N)
data = [
    norm, norm[bootstrap_indices],
    logn, logn[bootstrap_indices],
    expo, expo[bootstrap_indices],
    gumb, gumb[bootstrap_indices],
    tria, tria[bootstrap_indices],
]

fig, ax1 = plt.subplots(figsize=(10, 6))
fig.canvas.manager.set_window_title('A Boxplot Example')
fig.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

bp = ax1.boxplot(data, notch=False, sym='+', vert=True, whis=1.5)
plt.setp(bp['boxes'], color='black')
plt.setp(bp['whiskers'], color='black')
plt.setp(bp['fliers'], color='red', marker='+')

# Add a horizontal grid to the plot, but make it very light in color
# so we can use it for reading data values but not be distracting
ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
               alpha=0.5)

ax1.set(
    axisbelow=True,  # Hide the grid behind plot objects
    title='Comparison of IID Bootstrap Resampling Across Five Distributions',
    xlabel='Distribution',
    ylabel='Value',
)

# Now fill the boxes with desired colors
box_colors = ['darkkhaki', 'royalblue']
num_boxes = len(data)
medians = np.empty(num_boxes)
for i in range(num_boxes):
    box = bp['boxes'][i]
    box_x = []
    box_y = []
    for j in range(5):
        box_x.append(box.get_xdata()[j])
        box_y.append(box.get_ydata()[j])
    box_coords = np.column_stack([box_x, box_y])
    # Alternate between Dark Khaki and Royal Blue
    ax1.add_patch(Polygon(box_coords, facecolor=box_colors[i % 2]))
    # Now draw the median lines back over what we just filled in
    med = bp['medians'][i]
    median_x = []
    median_y = []
    for j in range(2):
        median_x.append(med.get_xdata()[j])
        median_y.append(med.get_ydata()[j])
        ax1.plot(median_x, median_y, 'k')
    medians[i] = median_y[0]
    # Finally, overplot the sample averages, with horizontal alignment
    # in the center of each box
    ax1.plot(np.average(med.get_xdata()), np.average(data[i]),
             color='w', marker='*', markeredgecolor='k')

# Set the axes ranges and axes labels
ax1.set_xlim(0.5, num_boxes + 0.5)
top = 40
bottom = -5
ax1.set_ylim(bottom, top)
ax1.set_xticklabels(np.repeat(random_dists, 2),
                    rotation=45, fontsize=8)

# Due to the Y-axis scale being different across samples, it can be
# hard to compare differences in medians across the samples. Add upper
# X-axis tick labels with the sample medians to aid in comparison
# (just use two decimal places of precision)
pos = np.arange(num_boxes) + 1
upper_labels = [str(round(s, 2)) for s in medians]
weights = ['bold', 'semibold']
for tick, label in zip(range(num_boxes), ax1.get_xticklabels()):
    k = tick % 2
    ax1.text(pos[tick], .95, upper_labels[tick],
             transform=ax1.get_xaxis_transform(),
             horizontalalignment='center', size='x-small',
             weight=weights[k], color=box_colors[k])

# Finally, add a basic legend
fig.text(0.80, 0.08, f'{N} Random Numbers',
         backgroundcolor=box_colors[0], color='black', weight='roman',
         size='x-small')
fig.text(0.80, 0.045, 'IID Bootstrap Resample',
         backgroundcolor=box_colors[1],
         color='white', weight='roman', size='x-small')
fig.text(0.80, 0.015, '*', color='white', backgroundcolor='silver',
         weight='roman', size='medium')
fig.text(0.815, 0.013, ' Average Value', color='black', weight='roman',
         size='x-small')

plt.show()

exit(1)
