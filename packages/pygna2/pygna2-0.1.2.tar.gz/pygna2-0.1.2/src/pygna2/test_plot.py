import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style('whitegrid')

def plot_test_results(null_dists, observed, output: str,
                      figure_type: str = 'box', significance=True,
                      width: float = 7.0, height: float = 7.0,
                      strip_alpha: float = 1,
                      x_label='Topology Internal Degree (%)'):
    n_genesets = len(observed.index)
    if x_label.endswith('(%)'):
        null_dists['Null distribution'] *= 100
        observed['Observed'] *= 100
    if figure_type == 'box':
        ax = sns.boxplot(
            data=null_dists,
            x='Null distribution',
            y='Gene set',
            whis=[0, 100],
            width=.3,
            palette=sns.husl_palette(n_genesets, l=0.9),
            zorder=1
        )
    elif figure_type == 'violin':
        ax = sns.violinplot(
            data=null_dists,
            x='Null distribution',
            y='Gene set',
            inner=None,
            palette=sns.husl_palette(n_genesets, l=0.9),
            zorder=1
        )
    elif figure_type == 'strip':
        ax = sns.stripplot(
            data=null_dists,
            x='Null distribution',
            y='Gene set',
            alpha=strip_alpha,
            palette=sns.husl_palette(n_genesets, s=0.4),
            zorder=1
        )
    sns.pointplot(ax=ax, data=observed, x='Observed', y='Gene set',
                  join=False, markers='d', errorbar=None, color='white',
                  scale=1.1)
    sns.pointplot(ax=ax, data=observed, x='Observed', y='Gene set',
                  join=False, markers='d', errorbar=None, palette='husl',
                  scale=1)
    if significance:
        for tick, (_, (_, observed, sig)) in zip(ax.get_yticks(),
                                                 observed.iterrows()):
            if sig:
                ax.text(observed, tick, sig, horizontalalignment='center',
                        verticalalignment='bottom', color='black')
    sns.despine(left=True, bottom=True)
    plt.xticks(rotation=30, ha='right')
    ax.set(ylabel="", xlabel=x_label)
    fig = ax.get_figure()
    fig.tight_layout()
    fig.set_figwidth(width)
    fig.set_figheight(height)
    fig.savefig(output)
