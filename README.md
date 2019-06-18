An example using the [`questionnaire`](https://github.com/kylebebak/questionnaire) module to collect gene symbols (and organisms) from the user (via command line) and then using NCBI's [eutils](https://www.ncbi.nlm.nih.gov/books/NBK25497/) to convert them to gene IDs.  More examples of how to use `questionnaire` can be found on the GitHub page under `examples`.

# Installing
Set up a virtual environment and install requirments.
```
virtualenv -p python3 questionnaire_env
. questionnaire_env/bin/activate
python3 -m pip install -r requirements.txt
```

# Running
```
python3 ./example_ncbi.py
```

# Testing
```
python3 -m unittest test.py
```

# Screenshots
