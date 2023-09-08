# Zenodo Search

Perform zenodo searches with python.

## Installation

```bash
pip install zenodo_search
```

## Dependencies

- requests

## Usage

```python
import zenodo_search as zsearch

search_string = 'resource_type.type:other AND creators.name:("Probst, Matthias")'
records = zsearch.search(search_string)
```
[![Open Quickstart Notebook](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/matthiasprobst/zenodo_search/blob/main/examples/example.ipynb)

More examples can be found in the [examples](examples/example.ipynb) folder.
