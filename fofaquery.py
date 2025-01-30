#!/usr/bin/env python3

import requests
import argparse 
import base64
import time
from gettext import gettext as _

LOGO =  """
.-:::::'   ...     .-:::::' :::.     .::::::.    ...    :::.,:::::: :::::::...-:.     ::-.
;;;'''' .;;;;;;;.  ;;;''''  ;;`;;   ,;;'```';;,  ;;     ;;;;;;;'''' ;;;;``;;;;';;.   ;;;;'
[[[,,==,[[     \\[[,[[[,,== ,[[ '[[, [[[     [[[\\[['     [[[ [[cccc   [[[,/[[['  '[[,[[['  
`$$$"``$$$,     $$$`$$$"``c$$$cc$$$c"$$c  cc$$$"$$      $$$ $$"\""\"   $$$$$$c      c$$"    
 888   "888,_ _,88P 888    888   888,"*8bo,Y88b,88    .d888 888oo,__ 888b "88bo,,8P"`     
 "MM,    "YMMMMMP"  "MM,   YMM   ""`   "*YP" "M" "YmmMMMM"" "\""\"YUMMMMMMM   "W"mM"    
"""

VERSION = "0.1"

HEADER = f" \n{LOGO}\nFOFA Query Tool v{VERSION} by alhazred\n\n"

class FOFAHelpFormatter(argparse.HelpFormatter):
    def _format_usage(self, usage, actions, groups, prefix=None):
        return HEADER + argparse.HelpFormatter._format_usage(self, usage, actions, groups, prefix)


def print_header():
	print(HEADER)
	

def parse_args():



	parser = argparse.ArgumentParser(description="FOFA Query Tool", formatter_class=FOFAHelpFormatter)
	parser.add_argument("-k", "--key", help="FOFA API key", required=True)
	parser.add_argument("-q", "--query", help="FOFA Query", required=False, default=None)
	parser.add_argument("-F", "--fields", help="Fields to return", default="host,ip,port")
	parser.add_argument("-s", "--size", help="Number of results to return", type=int, default=500)
	parser.add_argument("-d", "--delay", help="Delay between requests in seconds", type=float, default=0.5)
	parser.add_argument("-O", "--org", help="Search organisation", type=str, default=None)
	parser.add_argument("-o", "--output", help="File to write output to", type=str, default=None, required=True)
	parser.add_argument("-f", "--format", help="Output format", type=str, default="text", choices=["text", "json"])
	parsed = parser.parse_args()
	if parsed.query and (parsed.org):
		parser.error("making an explicit query with --query and using other query options are mutually exclusive")

	if parsed.org:
		parsed.query = f"org=\"{parsed.org}\"" if parsed.query is None else f"{parsed.query} && org=\"{parsed.org}\""

	return parsed


def get_results(key=None, query=None, fields="host,port,ip", size=500, delay=0.5):

	if not key:
		raise ValueError("API key is required")

	if not query:
		raise ValueError("Query is required")


	b64_query = base64.b64encode(query.encode()).decode()
	endpoint = "https://fofa.info/api/v1/search/next" 
	params = {
		"qbase64": b64_query,
		"fields": fields,
		"size": size,
		"key": key
	}
	results = []

	while True:
		resp = requests.get(endpoint, params=params)
		data = resp.json()
		results += data["results"]
		print(f"[+] got {len(data['results'])} results. total: {len(results)}")
		if data.get("next", False):
			params["next"] = data["next"]
		else:
			break

		# sleep for delay seconds

		time.sleep(delay)

	fields_ary = fields.split(",")
	results = [dict(zip(fields_ary, r)) for r in results]

	print(f"[+] finished. total results: {len(results)}")

	return results

def main():
	args = parse_args()
	results = get_results(key=args.key, query=args.query, fields=args.fields, size=args.size, delay=args.delay)
	print(f"[+] writing results to {args.output}")
	with open(args.output, "w") as f:
		if args.format == "json":
			import json
			f.write(json.dumps(results, indent=4))
		else:
			for r in results:
				f.write(" ".join([r.get(k, "") for k in args.fields.split(",")]) + "\n")
	print("[+] done")


if __name__ == "__main__":
	main()




	