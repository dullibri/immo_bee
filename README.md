# Immowelt Analyzer
Author: dirk.ulbricht@gmail.com

## Purpose
Scrape housing data from German housing portal Immowelt.de and retrieve as comma separted file.

## Installation

### Geckodriver 
This package depends on Geckodriver that can not be imported using pip directly. However, there is an os-independent python module [(geckodriver-autoinstaller)] available performing the install(https://pypi.org/project/geckodriver-autoinstaller/). For More information on a manual install see: 
- [Windows](https://www.browserstack.com/guide/geckodriver-selenium-python) 
- Linux it's `sudo apt install firefox-geckodriver` 
- Mac use  `npm install geckodriver`. 

### immo-bee

```bash
python -m pip install immo-bee
```

## Usage
### Commandline

```bash
 python -m immo_bee --help
 python -m immo_bee norderstedt hamburg
 ```
This will create a folder *data* on your current working directory (if it is not already there) and saves 4 json files for each location for houses, appartments, for rent and for sale respectively. Additionally it will create a comma separated file including all json files preprocessed and ready for usage.

### Import
If you prefer using immo_bee as a package use:
```python
from immo_bee import bee

list_of_locations = ["norderstedt","hamburg"]
df = bee(list_of_locations)
```