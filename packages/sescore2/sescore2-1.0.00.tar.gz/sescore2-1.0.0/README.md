<h1>SESCORE2: Learning Text Generation Evaluation via Synthesizing Realistic Mistakes</h1>

SESCORE2, is a SSL method to train a metric for general text generation tasks without human ratings. We develop a technique to synthesize candidate sentences with varying levels of mistakes for training. To make these self-constructed samples realistic, we introduce retrieval augmented synthesis on anchor text; It outperforms SEScore in four text generation tasks with three languages (The overall kendall correlation improves 14.3%).

<h3>Paper: https://arxiv.org/abs/2212.09305</h3>

<h3>Author Email: wendaxu@cs.ucsb.edu</h3>

<h3>Maintainer Email: zihan_ma@ucsb.edu</h3>

<h3>Install all dependencies:</h3>

````
```
pip install SEScore2
```
````

<h3>Instructions to score sentences using SEScore2:</h3>

Currently, the PyPI version only support English Checkpoint. To run SEScore2 for text generation evaluation:

````
```
from SEScore2 import SEScore2

scorer = SEScore2('en') # Download and load in metric with specified language, en (English), de (German), ja ('Japanese')

refs = ["SEScore is a simple but effective next generation text generation evaluation metric", "SEScore it really works"]

outs = ["SEScore is a simple effective text evaluation metric for next generation", "SEScore is not working"]

scores_ls = scorer.score(refs, outs, 1)
```
````
