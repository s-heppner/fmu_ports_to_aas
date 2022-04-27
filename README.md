# FMU Ports to AASX 

This simple Python script generates an `.aasx` file with the ports from an `.fmu` file to in order to make creating a
correct `SimulationModel` submodel easier. 


## Installation

- Requires Python 3.9
  (Probably works with 3.7+ but is not tested. 3.6 will probably not work)
- Pull or download this directory
- In a terminal:
  - Navigate to the downloaded directory
  - Windows:
    - `pip install -r requirements.txt`
  - Linux:
    - `pip3 install -r requirements.txt`
- Install the script as a package `pip install -e .`

## How to use

Option 1: Call the functions you want in the script, by adding to the end of it

Option 2: Via the command line:

```bash
python fmu_to_aasx.py <aas_id_short> <path/to/.fmu> <path/to/output_file> 
```

Hereby the arguments are:

- `<aas_id_short>`: The idShort of the AAS to be created
- `<path/to/.fmu>`: The path to the `.fmu` file
- `<path/to/output_file>`: The path to the output `.aasx` file
