# Dephack - Automation Tool for Bug Bounty Hunters

Dephack is an automation tool designed to assist bug bounty hunters with subdomain enumeration, resolver testing, and active/passive subdomain discovery. It supports multi-threaded resolution, working resolver identification, and wordlist generation based on discovered subdomains.

## Features

- **Passive Subdomain Discovery**: Find subdomains using passive techniques.
- **Active Subdomain Resolution**: Resolve subdomains using DNS resolvers.
- **Working Resolver Testing**: Identify functional DNS resolvers from a provided list.
- **Subdomain Permutation**: Generate subdomain permutations based on a wordlist.
- **Custom Output**: Save results to a specified output file.
- **Multithreading**: Speed up operations by resolving multiple subdomains in parallel.

## Installation

```bash
git clone https://github.com/username/dephack.git
cd dephack
pip3 install -r requirements.txt
```

## Usage
```bash
usage: dephack.py [-h] [-l file.txt] [-d domain.com] [-w wordlist.txt] [-o output.txt] [-r resolvers.txt] [-wr] [-ps] [-as]

Dephack - Automation tool for bug bounty hunters

optional arguments:
  -h, --help            show this help message and exit
  -l file.txt, --list file.txt
                        Input file containing a list of items to process.
  -d domain.com, --domain domain.com
                        Specify the target domain.
  -w wordlist.txt, --wordlist wordlist.txt
                        Input wordlist.
  -o output.txt, --output output.txt
                        Output file to store the results.
  -r resolvers.txt, --resolver resolvers.txt
                        File with a list of resolvers for subdomain resolution.
  -wr, --workingresolver
                        Identify resolvers that are functioning correctly
  -ps, --passivesubdomain
                        Find subdomains using passive methods.
  -as, --activesubdomain
                        Find subdomains using active resolution.
```

## Examples

### Passive Subdomain Discovery
Discover subdomains for a domain using passive methods:

```bash
python3 dephack.py -ps -d example.com -o subdomains.txt
```
### Active Subdomain Discovery from wordlist
Resolve subdomains from a wordlist and check which are live:

```bash
python3 dephack.py -as -d example.com -w wordlist.txt -o resolved_subdomains.txt
```
### Active Subdomain Discovery from subdomains
Resolve subdomains from a wordlist and check which are live:

```bash
python3 dephack.py -as -d example.com -l subdomains.txt -o resolved_subdomains.txt
```

### Working Resolver Identification
Test a list of resolvers and identify which are functional:

```bash
python3 dephack.py -wr -l resolvers.txt -o working_resolvers.txt
```

## Contributing
Contributions are welcome! Feel free to fork the repository, open issues, or submit pull requests.

## Author
Dephack is developed by depro0x.

## Acknowledgments
- Subfinder for passive subdomain enumeration.
- dns.resolver for DNS resolution.
