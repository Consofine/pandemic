# Pandemic

## Installation

### First Set Up

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies 

```bash
source venv/bin/activate
pip install -r requirements.txt
```


## Running 
```bash
export FLASK_APP=main.py; export FLASK_ENV=development; flask run
# Can define port and host like this: 
# export FLASK_APP=main.py; export FLASK_ENV=development; flask run --port=5004 --host=0.0.0.0
```