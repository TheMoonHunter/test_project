import unittest
import random
import os

from mock import MagicMock
from parser import XMLParser

class TestAssignment(unittest.TestCase):

	def setUp(self):
		""" Per Test setup."""
		restrictions = {"DateListed": "2016", "Description": "and"}
		required_fields = ["MlsId", "MlsName", "DateListed", "StreetAddress", "Price",
					  	   "Bedrooms", "Bathrooms", "Appliances", "Rooms", "Description"]
		self._initialize_xml_parser(restrictions, required_fields)

	def tearDown(self):
		""" Per Test tearDown"""
		if os.path.isfile("results.csv"):
			os.remove("results.csv")

	def _initialize_xml_parser(self, restrictions, required_fields):
		self._xml_parser = XMLParser(MagicMock(), MagicMock(),
									 restrictions, required_fields)

	def _validate_format_sub_nodes_output(self, results, field, expected):
		listing = MagicMock()
		listing.findall.return_value = results
		actual = self._xml_parser._format_sub_nodes(listing, field)
		self.assertEquals(expected, actual)

	def _get_mocked_results(self, values):
		results = []
		for value in values:
			result = MagicMock()
			result.text = value
			results.append(result)
		return results

	def test_format_sub_nodes_no_results(self):
		results = []
		expected = ""
		self._validate_format_sub_nodes_output(results, "field", expected)

	def test_format_sub_nodes_one_result(self):
		values = ["text"]
		results = self._get_mocked_results(values)
		expected = "text"
		self._validate_format_sub_nodes_output(results, "field", expected)

	def test_format_sub_nodes_multiple_results(self):
		values = ["dog", "cat", "horse", "cow"]
		results = self._get_mocked_results(values)
		expected = "dog,cat,horse,cow"
		self._validate_format_sub_nodes_output(results, "animals", expected)

	def _validate_get_bathroom_count_output(self, results, expected):
		listing = MagicMock()
		listing.find.return_value = results
		actual = self._xml_parser._get_bathroom_count(listing)
		self.assertEquals(expected, actual)

	def test_get_bathroom_count_no_values(self):
		results = []
		expected = '0'
		self._validate_get_bathroom_count_output(results, expected)

	def test_get_bathroom_count_throws_exception(self):
		results = Exception
		expected = '0'
		self._validate_get_bathroom_count_output(results, expected)

	def test_get_bathroom_count_with_values(self):
		results = MagicMock()
		results.text.return_value = '1'
		expected = '4'
		self._validate_get_bathroom_count_output(results, expected)

	def _validate_get_required_fields(self, find_results, findall_results, expected):
		listing = MagicMock()
		listing.find.return_value = find_results
		listing.findall.return_value = findall_results
		actual = self._xml_parser._get_required_fields(listing)
		self.assertEquals(expected, actual)

	def test_get_required_fields_no_fields(self):
		self._initialize_xml_parser(dict(), list())
		expected = dict()
		self._validate_get_required_fields("", list(), expected)

	def test_get_parsed_data_no_restrictions(self):
		required_fields = ["MslID", "DateListed"]
		listings = [MagicMock()] * random.randrange(1, 100)
		self._initialize_xml_parser(dict(), required_fields)
		actual = self._xml_parser._get_parsed_data(listings)
		self.assertEquals(len(listings), len(actual))

	def _validate_turn_dict_to_csv(self, parsed_data, file_exists, expected):
		self.assertEquals(os.path.isfile("results.csv"), False)
		actual = self._xml_parser._turn_dict_to_csv(parsed_data)
		self.assertEquals(os.path.isfile("results.csv"), file_exists)
		self.assertEquals(actual, expected)

	def test_turn_dict_to_csv_empty_dict(self):
		parsed_data = dict()
		file_exists = False
		expected = "Unable to create CSV file."
		self._validate_turn_dict_to_csv(parsed_data, file_exists, expected)

	def test_turn_dict_to_csv_populated_dict(self):
		parsed_data = MagicMock()
		file_exists = True
		expected = "Successfully created CSV file."
		self._validate_turn_dict_to_csv(parsed_data, file_exists, expected)


if __name__ == '__main__':
    unittest.main()
