# Installation

## Dependencies
### Clone daly-bms packages
```
git clone https://github.com/dreadnought/python-daly-bms.git
cd python-daly-bms

in windows: python setup.py install
in linux: python3 setup.py install
```

back to parent directory
```
cd ..
```

change name directory ```python-daly-bms``` to ```python_daly_bms```


## Install virtual enviroment
```
python -m venv env
```


## Activate Virtual Enviroment
```
env\Scripts\activate
```


## Install Requirements
```
pip install -r requirements.txt
```


## Copy Enviroment file example
```
cp .env.example .env
```


### Create Table

#### Crete table Loggers
```
python create_table.py create --table loggers
```

#### Crete table Realtime

```
python create_table.py create --table loggers
```


## Run the Program
``` 
python main.py
```

enjoy! ☕
