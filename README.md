# Visualizing and Training Machine Learning Models with Sinopia Linked Data
Presentation and source code for Jeremy Nelson's workshop, *Visualizing and Training Machine Learning Models with Sinopia Linked Data* at the 02022 LD4 Conference.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jermnelson/ld4-2021-workshop/HEAD)

This workshop provides participants the opportunity to explore [Sinopia][SINOPIA]'s Linked Data resources through a machine-learning lens. The workshop has four sections. 

1.  The first section will be an introduction to [Jupyter Notebooks][IPYNB],   
    harvesting RDF from [Sinopia's API][SINOPIA_API], and analyzing and visualizing the RDF using [Pandas][PANDAS]. 
1.  The second section takes the [Panda dataframes][PANDA_DF] from the first-section 
    and then build a custom [spaCy][SPACY] Named Entity Recognition (NER) pipeline for tagging descriptions with [FAST][FAST] subject headings. 
    We will use [HuggingFace transformers][HF] for NER and summarization pipelines using [PyTorch][PYTRCH]. 
1. The final section focuses on broader machine learning challenges and will introduce participants to [Model Cards][MODELCRDS] and 
    [Data Statements][DATA_STMTS] for describing the work they did during the workshop. 

[DATA_STMTS]: https://techpolicylab.uw.edu/data-statements/
[FAST]: https://fast.oclc.org/searchfast/
[HF]: https://huggingface.co/docs/transformers/index
[IPYNB]: https://jupyter.org/
[MODELCRDS]: https://arxiv.org/pdf/1810.03993.pdf
[PANDAS]: https://pandas.pydata.org/
[PANDA_DF]: https://pandas.pydata.org/docs/reference/frame.htmlspa
[PYTRCH]: https://pytorch.org/
[SINOPIA]: https://sinopia.io/
[SINOPIA_API]: https://ld4p.github.io/sinopia_api/
[SPACY]: https://spacy.io/