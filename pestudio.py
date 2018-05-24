#!/usr/bin/python3

import argparse
from SignatureMatcher import SignatureMatcher
from PeAnalyzer import PeAnalyzer
from VirusTotalClient import VirusTotalClient
import prettytable
import re
import constants
import xml.etree.ElementTree as ET
import sys

def parseCommandLineArguments():
	parser = argparse.ArgumentParser(description='PE file analyzer. The default output is human-readable and structured in tables. If no file is specifies, the interactive mode is entered.')
	parser.add_argument("-f", "--file", help="The file to analyze", required=False, dest="file")
	parser.add_argument("-v", "--virusTotal", help="Submit the file to virus total and get their score.", action="store_true", dest="virusTotal")
	parser.add_argument("--header", help="Show information from header.", action="store_true", dest="header")
	parser.add_argument("-t", "--tlsCallbacks", help="Show addresses of TLS callbacks.", action="store_true", dest="tls")
	parser.add_argument("-i", "--imports", help="Check the imports against known malicious functions.", action="store_true", dest="imports")
	parser.add_argument("-e", "--exports", help="Show the exports of the binary", action="store_true", dest="exports")
	parser.add_argument("-r", "--resources", help="Check the resources for blacklisted values.", action="store_true", dest="resources")
	parser.add_argument("--relocations", help="Show the relocations.", action="store_true", dest="relocations")
	parser.add_argument("-s", "--signatures", help="Check for known signatures (e.g. packers).", action="store_true", dest="signatures")
	parser.add_argument("--strings", help="Check the strings in the PE file.", action="store_true", dest="strings")
	parser.add_argument("-x", "--xml", help="Format output as xml.", action="store_true", dest="xml")
	return parser.parse_args()

def interactiveMode():
	print("No file has been specified. Entering interactive mode...")
	print("Not supported yet :(")

def checkFile(args):
	if args.xml:
		root = ET.Element("Report")

	if args.virusTotal:
		vt = VirusTotalClient(args.file)
		if args.xml:
			root = vt.getXmlReport(root)
		else:
			print(vt.printReport())
	
	peAnalyzer = PeAnalyzer(args.file)
	
	if args.header:
		if args.xml:
			peAnalyzer.addHeaderInformationXml(root)
		else:
			peAnalyzer.printHeaderInformation()
	
	if args.tls:
		if args.xml:
			peAnalyzer.addTLSXml(root)
		else:
			peAnalyzer.printTLS()
	
	if args.imports:
		if args.xml:
			root = peAnalyzer.getImportXml(root)
		else:
			peAnalyzer.printImportInformation()
	
	if args.exports:
		if args.xml:
			root = peAnalyzer.addExportsXml(root)
		else:
			peAnalyzer.printExports()
	
	if args.relocations:
		if args.xml:
			root = peAnalyzer.addRelocationsXml(root)
		else:
			peAnalyzer.printRelocations()
	
	if args.resources:
		blacklistedResources = peAnalyzer.blacklistedResources()
		
		if args.xml:
			root = peAnalyzer.addResourcesXml(root)
		else:
			print("Blacklisted resources found: " + str(blacklistedResources) if len(blacklistedResources) > 0 else "No blacklisted resources found")
			# TODO: Check resource types and corresponding thresholds in thresholds.xml
			
			peAnalyzer.showAllResources()
	
	if args.strings:		
		if args.xml:
			root = peAnalyzer.addAllStringsXml(root)
		else:
			print("Strings in the PE file:")
			peAnalyzer.printAllStrings()
	
	if args.signatures:
		matcher = SignatureMatcher(args.file)
		packers = matcher.findPackers()
		
		if args.xml:
			root = matcher.addPackersXml(root)
		else:
			if len(packers):
				print(constants.RED + "The signature of the following packer was found: " + str(packers) + constants.RESET)
			else:
				print("No packer signature was found in the PE file")
	
	if args.xml:
		print(ET.tostring(root).decode('utf-8'))
	

if __name__ == "__main__":
	args = parseCommandLineArguments()
	if args.file is None:
		interactiveMode()
	else:
		checkFile(args)