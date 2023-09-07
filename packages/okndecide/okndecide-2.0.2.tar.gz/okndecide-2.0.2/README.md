# OKN DECIDE PYTHON PACKAGE LIBRARY MANUAL
## Description
This program will read the given signal csv and extract the information about max chain length, unchained okn total and whether there is okn or not.

## Installation requirements and guide
### Anaconda
To install this program, `Anaconda python distributing program` and `Anaconda Powershell Prompt` are needed.  
If you do not have `Anaconda`, please use the following links to download and install:  
Download link: https://www.anaconda.com/products/distribution  
Installation guide link: https://docs.anaconda.com/anaconda/install/  
### PIP install
To install `okndecide`, you have to use `Anaconda Powershell Prompt`.  
After that, you can use the `okndecide` from any command prompt.  
In `Anaconda Powershell Prompt`:
```
pip install okndecide
```  
## Usage guide
### Example usage
```
okndecide -i (input file) -c (config file) -v
```
`-v` is optional.  
If `-v` is not mentioned, it will only generate only json string.  
If `-v` is mentioned, it will generate all info as comments and result json string.
 
If you want to test this program, you can clone this repository, install `okndecide`, open any command prompt or terminal.  
In the terminal, go to `../okndecide/development` then run the following command:
```
okndecide -i signal.csv -c decide.info.json -v > out_with_v.json
```
out_with_v.json will be created with all information(as comments) and result json string.
If you do not want to see all other information, then run the same command without `v`:
```
okndecide -i signal.csv -c decide.info.json > out_without_v.json
```
out_without_v.json will be created with just result json string.


### To upgrade version  
In `Anaconda Powershell Prompt`,
```
pip install -U okndecide
```
or
```
pip install --upgrade okndecide
```

