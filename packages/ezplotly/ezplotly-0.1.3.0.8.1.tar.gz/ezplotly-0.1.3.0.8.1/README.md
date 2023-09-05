# EZPlotly and EZPlotly_bio For Jupyter Notebooks
Introducing EZPlotly: An easy, intuitive wrapper for making Plotly plots in Jupyter notebooks

Plotly offers interactive plots, as opposed to the static plots that most other python visualization tools provide. However, Plotly syntax can be challenging to write, whereas the other libraries are a lot easier to plot with. EZPlotly helps bridge the gap. EZPlotly makes plotting with Plotly simpler and more matplotlib or matlab-like for experienced users of those toolsets.

In addition, EZPlotly offers domain-specific extensions for making interactive domain-specific plots in Plotly. <br><br>
*The YayROCS package enables common Deep Learning / Machine Learning plotting functions such as making interactive ROC curves, AUCs, and p-Value comparison charts. <br><br>
*The EZPlotly_bio extension offers a rich toolset for bioinformaticians to make common bioinformatics plots such as qqplots, chromosome rolling medians, chromosome frequency histograms and barcharts. 

# Installation

pip install ezplotly

# Example syntax:

```python
import ezplotly as ep
import numpy as np
a = np.arange(0.0, 1.0, 0.01)
b = a+1
exampleHist = ep.hist(data=a, min_bin=0.0, max_bin=1.0, bin_size=0.1, title='MyHistogram', xlabel='a')
exampleScatter = ep.scattergl(x=a, y=b, title='Test', xlabel='x', ylabel='y')
ep.plot_all([exampleHist, exampleScatter])
```

For more examples, checkout run the EZPlotlyExamples.ipynb and EZPlotlyBioExamples.ipynb in Jupyter!

# EasyPlotly_bio for Bioinformaticians:

In the bioinformatics domain? EasyPlotly_bio supports making common bioinformatics plots such as qqplots, chromosome rolling medians, chromsome count bar charts, and chromosome histograms.