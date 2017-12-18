import urllib2
import csv
from xml.etree import ElementTree


class XMLParser(object):

	def __init__(self, url, data_field, restrictions, required_fields):
		""" Initialize """
		self._url = url
		self._data_field = data_field
		self._restrictions = restrictions
		self._required_fields = required_fields

	def _extract_xml_data(self):
		""" Extract xml data from url."""
		tree = ElementTree.parse(urllib2.urlopen(self._url))
		xml_data = tree.getroot()
		return xml_data

	def parse_xml_data(self):
		""" Start parsing through XML data."""
		xml_data = self._extract_xml_data()
		listings = xml_data.findall(self._data_field)
		parsed_data = self._get_parsed_data(listings)
		return self._turn_dict_to_csv(parsed_data)

	def _turn_dict_to_csv(self, parsed_data):
		""" Put parsed data in a CSV file."""
		try:
			keys = parsed_data[0].keys()

			# sort parsed_data by date listed.
			data = sorted(parsed_data, key=lambda k: k['DateListed'])

			with open('results.csv', 'wb') as output_file:
			    dict_writer = csv.DictWriter(output_file, keys)
			    dict_writer.writeheader()
			    dict_writer.writerows(data)
			return "Successfully created CSV file."
		except:
			return "Unable to create CSV file."

	def _get_parsed_data(self, listings):
		""" Get parsed data from XML data with given restrictions."""
		parsed_data = list()
		for listing in listings:
			selected = True

			# loop through each restriction and only select listing if
			# it passes all restrictions
			for field, value in self._restrictions.iteritems():
				attribute = listing.find(".//{}".format(field))
				if value not in attribute.text:
					selected = False
					break
			if selected:
				parsed_data.append(self._get_required_fields(listing))
		return parsed_data

	def _get_required_fields(self, listing):
		""" Get required fields into a dict."""
		# RODO: generalize this for any XML file.
		data = dict()
		for field in self._required_fields:
			if field == "Appliances" or field == "Rooms":
				data[field] = self._format_sub_nodes(listing, field)
			elif field == "Description":
				description = listing.find(".//{}".format(field)).text
				data[field] = description[:200]
			elif field == "Bathrooms":
				data[field] = self._get_bathroom_count(listing)
			else:
				data[field] = listing.find(".//{}".format(field)).text
		return data

	def _get_bathroom_count(self, listing):
		""" Get total number of bathrooms for listing."""
		bathroom_types = ["Bathrooms", "FullBathrooms", "HalfBathrooms", "ThreeQuarterBathrooms"]
		count = 0
		try:
			for br_type in bathroom_types:
				num_bathrooms = listing.find(".//{}".format(br_type)).text
				if num_bathrooms:
					count += int(num_bathrooms)
		except:
			count = 0
		return str(count)

	def _format_sub_nodes(self, listing, field):
		""" Format all sub-nodes to be comma joined."""
		sub_nodes = listing.findall(".//{}/*".format(field))
		sub_nodes_text = [sub_node.text for sub_node in sub_nodes]
		return ",".join(sub_nodes_text)


if __name__ == "__main__":
	# initialize all information needed
	url = "http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml"
	restrictions = {"DateListed": "2016", "Description": "and"}
	required_fields = ["MlsId", "MlsName", "DateListed", "StreetAddress", "Price", 
					  "Bedrooms", "Bathrooms", "Appliances", "Rooms", "Description"]
					  
	# run the parser
	parser = XMLParser(url, "Listing", restrictions, required_fields)
	output = parser.parse_xml_data()
	print output