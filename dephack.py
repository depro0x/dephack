#!/usr/bin/env python3
import sys
import argparse
import subprocess
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Dephack - Automation tool for bug bounty hunters",
        epilog="For more information, visit https://github.com/depro0x/dephack"
    )

    parser.add_argument(
        "-l", "--list",
        type=argparse.FileType('r'),
        metavar="file.txt",
        help="Input file containing a list of items to process.",
        required=False
    )

    parser.add_argument(
        "-d", "--domain",
        type=str,
        metavar="domain.com",
        help="Specify the target domain.",
        required=False
    )

    parser.add_argument(
        "-w", "--wordlist",
        type=argparse.FileType('r'),
        metavar="wordlist.txt",
        help="Input wordlist.",
        required=False
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="output.txt",
        help="Output file to store the results.",
        required=False
    )

    parser.add_argument(
        "-r", "--resolver",
        type=argparse.FileType('r'),
        metavar="resolvers.txt",
        help="File with a list of resolvers for subdomain resolution.",
        required=False
    )

    parser.add_argument(
        "-wr", "--workingresolver",
        action="store_true",
        help="Identify resolvers that are functioning correctly",
        required=False
    )

    parser.add_argument(
        "-ps", "--passivesubdomain",
        action="store_true",
        help="Find subdomains using passive methods.",
        required=False
    )

    parser.add_argument(
        "-as", "--activesubdomain",
        action="store_true",
        help="Find subdomains using active resolution.",
        required=False
    )

    return parser.parse_args()

def test_resolver(resolver):
    try:
        test_resolver = dns.resolver.Resolver(configure=False)
        test_resolver.nameservers = [resolver]
        test_resolver.resolve("google.com", "A", lifetime=3)
        return resolver
    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.exception.DNSException):
        return None

def working_resolver(resolvers, max_workers=50):
    working = []
    print(f"Total resolvers to test: {len(resolvers)}")
    print("Identifying functional resolvers...")

    with ThreadPoolExecutor(max_workers) as executor:
        future_to_resolver = {executor.submit(test_resolver, resolver): resolver for resolver in resolvers}
        for idx, future in enumerate(as_completed(future_to_resolver), start=1):
            result = future.result()
            if result:
                working.append(result)
            if idx % 1000 == 0 or idx == len(resolvers):
                print(f"Checked {idx}/{len(resolvers)} resolvers. Working so far: {len(working)}")

    return working


def passive_subdomains(domain):
    try:
        result = subprocess.check_output(
            ["subfinder", "-d", domain, "-silent"], stderr=subprocess.STDOUT
        )
        subdomains = result.decode("utf-8").splitlines()
        return subdomains
    except subprocess.CalledProcessError as e:
        print(f"Error occured while running subfinder: {e.output.decode()}")
        sys.exit(1)


def resolve_subdomain(subdomain, resolvers):
    for resolver in resolvers:
        try:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = [resolver]
            dns.resolver.resolve(subdomain, 'A')
            return subdomain
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            continue
    return None

def resolve_subdomains(subdomains, resolvers):
    resolved_subdomains = []
    total_subdomains = len(subdomains)
    successful_resolved = 0
    
    print(f"Total subdomains to resolve: {total_subdomains}")
    print("Resolving subdomains.....")
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(resolve_subdomain, subdomain, resolvers): subdomain for subdomain in subdomains}
        
        for idx, future in enumerate(as_completed(futures), start=1):
            result = future.result()
            if result:
                resolved_subdomains.append(result)
                successful_resolved += 1

            if idx % 1000 == 0 or idx == total_subdomains:
                print(f"Progress: {idx}/{total_subdomains} subdomains resolved, Successful: {successful_resolved}")
    
    print(f"Total successfully resolved subdomains: {successful_resolved}")
    return resolved_subdomains


def generate_wordlist_from_subdomains(subdomains, domain):
    wordlist = []
    for sub in subdomains:
        if sub.endswith(f".{domain}"):
            stripped = sub.replace(f".{domain}", "")
            words = stripped.split(".")
            wordlist.extend(words)
    
    wordlist = list(set(wordlist))
    return wordlist

def generate_subdomain_permutations(wordlist, domain, iterations=2):
    permutations = []
    
    for word in wordlist:
        subdomain = f"{word}.{domain}"
        permutations.append(subdomain)
    
    for _ in range(iterations - 1):
        new_permutations = []
        for word in wordlist:
            for perm in permutations:
                subdomain = f"{word}.{perm}"
                new_permutations.append(subdomain)
        permutations.extend(new_permutations)

    return permutations



if __name__ == "__main__":
    args = parse_arguments()

    if args.passivesubdomain:
        if args.domain:
            if args.output:
                print(f"Discovering subdomains for: {args.domain}")
                output = passive_subdomains(args.domain)
                print(f"Found {len(output)} subdomains passively")
                with open(args.output, 'w') as f:
                        f.write("\n".join(output))
                print(f"Subdomains saved to {args.output}")
                if not output:
                    print("No subdomains found.")
                sys.exit(1)
            else:
                print("Please specify an output file.")
        else:
            print("Please provide a domain.")

    elif args.activesubdomain:
        if args.domain:
            if args.output:
                if args.list:
                    with open(args.list.name, 'r') as file:
                        subdomains = [line.strip() for line in file.readlines() if line.strip()]
                    wordlist = generate_wordlist_from_subdomains(subdomains, args.domain)
                    print(f"Generated {len(wordlist)} words from subdomains.")
                elif args.wordlist:
                    with open(args.wordlist.name, 'r') as file:
                        wordlist = [line.strip() for line in file.readlines() if line.strip()]
                permutated_subdomains = generate_subdomain_permutations(wordlist, args.domain)
                print(f"Generated {len(permutated_subdomains)} permutations.")
                
                if args.resolver:
                    with open(args.resolver.name, 'r') as file:
                        resolvers = [line.strip() for line in file.readlines() if line.strip()]
                else:
                    resolvers = ['8.8.8.8', '1.1.1.1']
                
                resolved_subdomains = resolve_subdomains(permutated_subdomains, resolvers)
                print(f"Resolved: {len(resolved_subdomains)} subdomains.")
                
                if resolved_subdomains:
                    output_data = []
                    for subdomain in resolved_subdomains:
                        output_data.append(subdomain)
                    with open(args.output, 'w') as f:
                        f.write("\n".join(output_data))
                    print(f"Resolved Subdomains saved to {args.output}")                     
                else:
                    print("No subdomains could be resolved")
            else:
                print("Please specify an output file.")
        else:
            print("A domain is required.")

    elif args.workingresolver:
        if args.list:
            with open(args.list.name, 'r') as file:           
                if args.output:
                    raw_resolvers = [line.strip() for line in file.readlines() if line.strip()]
                    working_resolvers = working_resolver(raw_resolvers)
                    with open(args.output, 'w') as f:
                        f.write("\n".join(working_resolvers))
                    print(f"Working resolvers saved to {args.output}")
                else:
                    print("Please specify an output file")
        