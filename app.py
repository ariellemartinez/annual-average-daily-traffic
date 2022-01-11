import unicodedata
import re
import requests
import pandas as pd

def slugify(value, allow_unicode=False):
	# Taken from https://github.com/django/django/blob/master/django/utils/text.py
	value = str(value)
	if allow_unicode:
		value = unicodedata.normalize("NFKC", value)
	else:
		value = unicodedata.normalize("NFKD", value).encode(
			"ascii", "ignore").decode("ascii")
	value = re.sub(r"[^\w\s-]", "", value.lower())
	return re.sub(r"[-\s]+", "-", value).strip("-_")

# We are defining the Socrata dataset we want to scrape here.
dataset = {
	"identifier": "6amx-2pbv",
	# "title": "Annual Average Daily Traffic (AADT): Beginning 1977",
	# "dataset_link": "https://data.ny.gov/Transportation/Annual-Average-Daily-Traffic-AADT-Beginning-1977/6amx-2pbv/data",
	# "api_documentation_link": "https://dev.socrata.com/foundry/data.ny.gov/6amx-2pbv",
	"description": "Annual average daily traffic",
	"where_query_string": "$where=county='Nassau' OR county='Suffolk'"
}

try:
	# We are creating an empty list called "results".
	results = []
	url = "https://data.ny.gov/resource/" + dataset["identifier"] + ".json"
	# The limit can be up to 50000.
	limit = 1000
	count_payload = "$select=count(*)&" + dataset["where_query_string"]
	# "requests" documentation page is here: https://docs.python-requests.org/en/master/user/quickstart/
	count_request = requests.get(url, params=count_payload)
	# As we go through each page of the dataset, we are going to scrape that page of the dataset.
	count = int(count_request.json()[0]["count_1"])
	i = 0
	while i < count / limit:
		offset = i * limit
		loop_payload = "$limit=" + str(limit) + "&$offset=" + str(offset) + "&" + dataset["where_query_string"]
		loop_request = requests.get(url, params=loop_payload)
		for result in loop_request.json():
			results.append(result)
		i += 1
	# "pandas" documentation page is here: https://pandas.pydata.org/docs/index.html
	df = pd.DataFrame(results)
	file_name = slugify(dataset["description"])
	df.to_csv("csv/" + file_name + ".csv", index=False)
except:
	pass