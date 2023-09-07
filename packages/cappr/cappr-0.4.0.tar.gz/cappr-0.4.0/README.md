# CAPPr: zero-shot text classification using autoregressive language models

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Documentation Status](https://readthedocs.org/projects/cappr/badge/?version=latest)](https://cappr.readthedocs.io/en/latest/?badge=latest)
[![tests](https://github.com/kddubey/cappr/actions/workflows/test.yml/badge.svg)](https://github.com/kddubey/cappr/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/kddubey/cappr/branch/main/graph/badge.svg?token=NYIL076PSM)](https://codecov.io/gh/kddubey/cappr)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Package Version](https://img.shields.io/pypi/v/cappr?logo=pypi&style=flat&color=orange)](https://pypi.org/project/cappr/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Perform zero-shot text classification by estimating the probability that an inputted
completion comes after an inputted prompt. Hence the name:

> **C**ompletion<br>
  **A**fter<br>
  **P**rompt<br>
  **Pr**obability<br>

The method is fleshed out in my [question on Cross Validated](https://stats.stackexchange.com/q/601159/337906).


## Usage

<details>
<summary>Use a model from the OpenAI API</summary>

Specifically, this model must be compatible with the
[/v1/completions](https://platform.openai.com/docs/models/model-endpoint-compatibility)
endpoint.

```python
from cappr.openai.classify import predict

prompt = """
Tweet about a movie: "Oppenheimer was pretty good. But 3 hrs...cmon Nolan."

This tweet contains the following criticism:
""".strip("\n")

class_names = ("bad message", "too long", "unfunny")

preds = predict(
    prompts=[prompt],
    completions=class_names,
    model="text-ada-001",
)
print(preds)
# ['too long']
```

Notice that the completions can contain many tokens.
</details>

<details>
<summary>Extract the final answer from a step-by-step completion</summary>

Step-by-step and chain-of-thought prompts are highly effective ways to get an LLM to
"reason" about more complex tasks. But if you need a structured output, a step-by-step
completion is unwieldy. Use CAPPr to extract the final answer from these types of
completions, given a list of possible answers.

See this idea in action [here in the
docs](https://cappr.readthedocs.io/en/latest/4_user_guide.html#select-a-prompt-completion-format).
CAPPr is **100% guaranteed** to return an output from the list of answers.
</details>

<details>
<summary>Use a model from the HuggingFace model hub</summary>

Specifically, this model must be able to be loaded using
`transformers.AutoModelForCausalLM.from_pretrained`.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from cappr.huggingface.classify import predict

prompt = "Which planet is closer to the Sun: Mercury or Earth?"
class_names = ("Mercury", "Earth")

# load model and tokenizer
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

preds = predict(
    prompts=[prompt],
    completions=class_names,
    model_and_tokenizer=(model, tokenizer),
)
print(preds)
# ['Mercury']
```

For an example with Llama 2, see the notebook
[`demos/llama2/copa.ipynb`](https://github.com/kddubey/cappr/blob/main/demos/llama2/copa.ipynb)
or
[`demos/llama2/quick_check_correctness.ipynb`](https://github.com/kddubey/cappr/blob/main/demos/llama2/quick_check_correctness.ipynb).
So far, CAPPr has been tested for correctness on the following architectures:
  - GPT-2
  - GPT-J
  - Llama
  - Llama 2 (chat, raw, and its GPTQd versions).

Raise an issue to lmk that you don't see your architecture on this list.

</details>

<details>
<summary>Run in batches</summary>

Let's use `huggingface` for this example cuz it's free. And let's predict probabilities
instead of the class.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from cappr.huggingface.classify import predict_proba

prompts = [
    "Stephen Curry is a",
    "Martina Navratilova was a",
    "Dexter, from the TV Series Dexter's Laboratory, is a",
    "LeBron James is a",
]

# each of the prompts could be completed with one of these:
class_names = ("basketball player", "tennis player", "scientist")
prior =       (      1/6,                1/6,            2/3    )
# say I expect most of my data to have scientists

# load model and tokenizer
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

pred_probs = predict_proba(
    prompts=prompts,
    completions=class_names,
    model_and_tokenizer=(model, tokenizer),
    batch_size=32,  # whatever fits on your CPU/GPU
    prior=prior,
)

# pred_probs[i,j] = probability that prompts[i] is classified as class_names[j]
print(pred_probs.round(1))
# [[0.5 0.3 0.2]
#  [0.3 0.6 0.2]
#  [0.1 0.1 0.8]
#  [0.8 0.2 0. ]]

# for each prompt, which completion is most likely?
pred_class_idxs = pred_probs.argmax(axis=1)
print([class_names[pred_class_idx] for pred_class_idx in pred_class_idxs])
# ['basketball player',
#  'tennis player',
#  'scientist',
#  'basketball player']
```
</details>

<details>
<summary>Run in batches, where each prompt has a different set of possible completions
</summary>

Again, let's use `huggingface` to predict probabilities.

```python
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer

from cappr import Example
from cappr.huggingface.classify import predict_proba_examples

examples = [
    Example(
        prompt="Jodie Foster played",
        completions=("Clarice Starling", "Trinity in The Matrix"),
    ),
    Example(
        prompt="Batman, from Batman: The Animated Series, was played by",
        completions=("Pete Holmes", "Kevin Conroy", "Spongebob!"),
        prior=      (     1/3      ,      2/3     ,      0      ),
    ),
]

model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
pred_probs = predict_proba_examples(examples, model_and_tokenizer=(model, tokenizer))

# pred_probs[i][j] = probability that examples[i].prompt is classified as
# examples[i].completions[j]
print([example_pred_probs.round(2) for example_pred_probs in pred_probs])
# [array([0.7, 0.3]),
#  array([0.03, 0.97, 0.  ])]

# for each example, which completion is most likely?
pred_class_idxs = [np.argmax(example_pred_probs) for example_pred_probs in pred_probs]
print(
    [
        example.completions[pred_class_idx]
        for example, pred_class_idx in zip(examples, pred_class_idxs)
    ]
)
# ['Clarice Starling',
#  'Kevin Conroy']
```
</details>

More examples are linked [here in the
documentation](https://cappr.readthedocs.io/en/latest/5_examples.html).

See
[`demos/superglue/copa.ipynb`](https://github.com/kddubey/cappr/blob/main/demos/superglue/copa.ipynb)
for a demonstration of a slightly harder classification task.


## Documentation

https://cappr.readthedocs.io


## Setup

If you intend on using OpenAI models, [sign up for the OpenAI API
here](https://platform.openai.com/signup), and then set the environment variable
`OPENAI_API_KEY`. For zero-shot classification, OpenAI models are currently far ahead of
others. But using them will cost ya 💰!

Install with `pip`:

```
pip install cappr
```

(Optional) Install requirements for HuggingFace models

```
pip install cappr[hf]
```

(Optional) Install requirements for running
[`demos`](https://github.com/kddubey/cappr/tree/main/demos)

```
pip install cappr[demos]
```


## Motivation

Create a more usable zero-shot text classification interface than
[classification via sampling (CVS)](https://platform.openai.com/docs/guides/completion/classification).

<details>
<summary>Short</summary>

With CVS, your job is to write up your classification task in a `prompt` string, and
then write custom code to post-process arbitrary `completion`/output strings.

With CAPPr, your job starts and stops at writing up your classification task as a
`{prompt}{end_of_prompt}{completion}` string.
</details>

<details>
<summary>Long</summary>

Please see [this page of the
documentation](https://cappr.readthedocs.io/en/latest/2_motivation.html).

</details>

<details>
<summary>Unstudied</summary>

I'm curious to see how much easier estimation/discrimination is than generation. In
[`demos/superglue/copa.ipynb`](https://github.com/kddubey/cappr/blob/main/demos/superglue/copa.ipynb),
CVS using OpenAI's `text-curie-001` is less than 50% accurate, while CAPPr is 80%
accurate.

</details>

<details>
<summary>Honest</summary>

Keep myself busy

</details>


## Results

<details>
<summary>
Statistical performance
</summary>

Not too shabby. TODO: summary table comparing CVS vs. CAPPr vs. few-shot methods like
SetFit and PET.

[2 SuperGLUE datasets](https://github.com/kddubey/cappr/blob/main/demos/superglue)

[RAFT zero-shot training sets](https://github.com/kddubey/cappr/blob/main/demos/raft)
</details>


<details>
<summary>
Computational performance
</summary>

One concern was that CAPPr requires as many `model()` calls as there are classes. But in
the CAPPr scheme, we can simply cache each attention block's keys and values for the
prompts. This feature is already supported by `AutoModelForCausalLM`s. See [this
code](https://github.com/kddubey/cappr/blob/main/src/cappr/huggingface/classify.py) for
the implementation. Note that this caching is not implemented for OpenAI models, as I
can't control their backend. **This means that when running `cappr.openai` functions,
you'll be on the *cappr (no cache)* line** :-(

![](/docs/source/_static/scaling_classes/batch_size_32.png)

*Figure 1: [COPA](https://people.ict.usc.edu/~gordon/copa.html) dataset, repeating the
choices to simulate multi-class classification tasks. [GPT-2
(small)](https://huggingface.co/gpt2) was run on a Tesla K80 GPU (whatever was free in
Google Colab in March 2023). 96 classification inputs were processed in batches of size
32. Each point in the graph is a median of 5 runs. For classification via sampling
(CVS), exactly 4 tokens were generated for each prompt, which is the number of tokens in
`'\n\nAnswer A'`. 1-token times are also shown. But for COPA (and other multiple-choice
style prompts), that may result in lower zero-shot accuracy, as most of the sampled
choices come after the first token.*

See the [`demos/computational_analysis.ipynb`
notebook](https://github.com/kddubey/cappr/blob/main/demos/computational_analysis.ipynb).

</details>


## Related work

The idea behind CAPPr is very well known. There are many papers where averaging token
log-probabilities is a useful subroutine. Here are some papers which focus on this idea.

While [benchmarking this
method](https://github.com/kddubey/cappr/blob/main/demos/superglue/wsc.ipynb) on the
Winograd Schema Challenge, I found that [this paper](https://arxiv.org/abs/1806.02847)
is very similar:

> Trinh, Trieu H., and Quoc V. Le. "A simple method for commonsense reasoning." arXiv
> preprint arXiv:1806.02847 (2018).

[PET with multiple masks](https://arxiv.org/abs/2009.07118) also aggregates token
probabilities to do prompt-completion classification, but these probabilities are
assumed to come from masked language models like BERT.

> Schick, Timo, and Hinrich Schütze. "It's not just size that matters: Small language
> models are also few-shot learners." arXiv preprint arXiv:2009.07118 (2020).


## Contributing

TODO


## Local development

### Setup

1. Create a new Python 3.8+ environment using venv. Activate it

2. Clone the repo (or fork it and clone that)

   ```
   git clone https://github.com/kddubey/cappr.git
   ```

3. cd to the repo and install this package in editable mode, along with development
   requirements (ensure your venv is activated)

   ```
   python -m pip install -e .[dev]
   ```

### VS code extensions for development

  * [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring).
  Use the numpy format.
  * [Set Python formatting to
    `black`](https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0).
  * [Rewrap](https://stkb.github.io/Rewrap/). Enable Auto Wrap.

### Testing

```
pytest
```

Note that a few small, dummy models will be downloaded to your computer if you don't
have them already.

### Docs

To locally build docs (I'm on Windows lol), run

```
cd docs

make.bat html
```

To preview these docs, open `docs/build/html/index.html`.

Docs are automatically built and published when code is merged to main.

### Release

[Bump the
version](https://github.com/kddubey/cappr/commit/d1f7dd51fa702c123bdfb0bcb97535995641c224),
and then create a new release on GitHub. A new version of the package will then be
automatically published on PyPI.


## Todo

(**) = I'm currently working on this or will work on it really soon. Expect it in the
next release or two. Hopefully the next one is a Llama2-battle-tested CAPPr 1.0.0!

<details>
<summary>Code</summary>

- [x] Small CPU speed-ups
  - [x] For constant-completions input, vectorize `cappr.utils.classify.agg_log_probs`
  - [x] For `examples` input, if # completions per prompt is constant, vectorize
  `cappr.utils.classify.posterior_prob`
- [ ] HuggingFace `transformers.AutoModelForCausalLM`
  - [ ] Support as many of them as possible
    - [x] GPT-2
    - [x] GPT-J
    - [x] Llama
    - [x] Llama 2
    - [x] Llama 2 chat
    - [ ] Vicuna
    - [ ] PaLM
    - [ ] T5
  - [ ] If all completions are single-tokens, just run inference once
    - [x] non `_examples` fxns
    - [ ] `_examples` fxns: need to think more about how to slice efficiently
  - [ ] Don't modify the tokenizer. Create a context manager around tokenizations (**)
  - [x] Optimize backend to enable greater scaling wrt # completions/classes
  - [x] Get it working on GPU, check that it's faster than sampling
  - [ ] May need to revisit batching
  - [ ] Add type alias `ModelForCausalLM` which is a `PreTrainedModel` (**)
  - [ ] Allow non-`' '` `end_of_prompt`. I'm not sure how helpful that is.
  - [ ] Factor out repeated code b/t `classify` and `classify_no_cache`
  - [ ] Support [Inference
    Endpoints](https://huggingface.co/docs/inference-endpoints/index)?
  - [ ] Support TensorFlow models?
  - [ ] Support priming, as in: cache it. See
    [backprompt](https://github.com/kddubey/backprompt)
- [ ] User conveniences (**)
  - [ ] Make progress bars optional, since inference often isn't batched
  - [ ] Accept string input and return string instead of list
- [ ] Support discount feature for `_examples` functions
- [ ] Factor out input checks (on prompts and completions)
- [x] (for me) Auto-enforced code formatting b/c it's getting time-consuming
- [ ] Allow for multi-label classification
  - [ ] Pass `normalize` as an argument to predict_proba functions
  - [ ] For `huggingface`, add note that you'll get faster results by passing all
  labels at once (assuming prompt is identical for each label)
- [ ] Fill in missing or non-numpy docstrings
- [ ] Testing
  - [ ] Test `cappr.huggingface.classify_no_cache` by comparing to results w/o batching!
  - [ ] For heavily quantized models, only test that pred probs are w/in 1e-2 atol
  - [ ] Increase test cases
  - [ ] Test input checks
  - [ ] Test `cappr.openai.api`
- [ ] Fix or hide warning (**)
  ```
  /usr/local/lib/python3.10/dist-packages/cappr/utils/classify.py:63: VisibleDeprecationWarning: Creating an ndarray from ragged nested sequences (which is a list-or-tuple of lists-or-tuples-or ndarrays with different lengths or shapes) is deprecated. If you meant to do this, you must specify 'dtype=object' when creating the ndarray.
  np.array(  # raises jagged/inhomogeneous ValueError if non-constant # tokens
  ```
- [ ] Rebrand docs to be more SWE friendly, no ML knowledge needed (**)
</details>

<details>
<summary>Research</summary>

Evaluate on more datasets, and understand its relative advantages and disadvantages vs
other classification methods.

- [ ] (Llama2 + CAPPr) (Llama2 + CVS) vs (Llama2 chat + CAPPr) vs (Llama2 chat + CVS)
  (**)
- [ ] RAFT benchmark
  - [x] Zero-shot training scores
  - [ ] Submit zero-shot test predictions
  - [ ] Few-shot (priming) training scores
  - [ ] Submit few-shot test predictions
- [ ] Create a user guide, build a table of results comparing competing approaches on
statistical performance, cost, and computation
- [ ] Evaluate a CoT/SbS prompt -> CAPPr to pull out the answer
- [ ] Make a computational comparison to sampling
  - [x] Assume I have full freedom to decide how inference works. Demo w/ GPT-2. Process
  inputs in batches.
  - [ ] Process inputs 1-by-1
- [ ] More SuperGLUE tasks?
- [ ] Calibration
  - [ ] Is the prior actually effective? Downsample and see
  - [ ] curves
- [ ] Finetune smaller, cheaper model and compare against zero-shot w/ davinci
  - [ ] e.g., GPT-2 from huggingface, `text-ada-001`
  - [ ] Again, compare against sampling
- [ ] Evaluate a bigger model like GPT-J
</details>
