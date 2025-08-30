# importing the modules
import gettext
import re
import requests
import json
import urllib.parse
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from requests.exceptions import RequestException
try:
	import wx  # UI fallback for error messages
except Exception:
	wx = None

# Ensure '_' exists even before gettext.install is called elsewhere
try:
	_  # type: ignore[name-defined]
except NameError:
	def _(s: str) -> str:  # noqa: N802
		return s

# Create a function to add translations to the program
# This function is used to identify the program with translations added to it by contributors

def SetLanguage(CurrentSettings):

# This dictionary is used to define program on language folder and on name of language within program settings
# The dictionary key indicates the name of the language within the program settings. For example: "English"
# The dictionary value indicates the folder that contains the language files. Example: "en"

	language = {
	"English": "en",
	"Arabic": "ar",
	"Spanish": "es",
	"French": "fr"
	}

	try:
		CurrentLanguage = language[CurrentSettings["language"]]
	except:
		_ = gettext.gettext
		return _

	try:
		ChangeLanguage = gettext.translation('WikiSearch', localedir='languages', languages=[CurrentLanguage])
		ChangeLanguage.install()
		_ = ChangeLanguage.gettext
	except:
		_ = gettext.gettext

	return _

def DisableLink(HtmlContent):
	HtmlContent = HtmlContent
	pattern =r'(href\=\".*?\")'
	result = re.sub(pattern, 'role="link" aria-disabled="false"', HtmlContent, flags=re.MULTILINE)
	return result

def GetOnlineInfo(timeout: int = 10):

	# Load and read json online file with timeout and graceful errors
	url = "https://raw.githubusercontent.com/tecwindow/WikiSearch/main/WikiSearch.json"
	try:
		# Use urllib with a UA to avoid some CDNs blocking
		req = Request(url, headers={"User-Agent": "WikiSearch/1.4 (Windows)"})
		with urlopen(req, timeout=timeout) as response:
			data = response.read()
		data_json = json.loads(data)
		# Putting information into a dictionary.
		info = {
			"name": data_json.get("name"),
			"version": data_json.get("version"),
			"What's new": data_json.get("What's new", ""),
			"url": data_json.get("url"),
		}
		return info
	except Exception:
		# Propagate a controlled failure to caller; they already handle AutoCheck UI
		raise

	# Delete The empty lines.
def remove_blank_lines(text):
    lines = text.split("\n")
    lines = list(filter(lambda x: x.strip(), lines))
    text = "\n".join(lines)
    return text

# Getting the tables of article.
def GetTables(url: str, timeout: int = 10):

	TablesText = []
	try:
		resp = requests.get(url, timeout=timeout, headers={"User-Agent": "WikiSearch/1.4 (Windows)"})
		resp.raise_for_status()
		soup = BeautifulSoup(resp.content, "html.parser")
		tables = soup.find_all("table")
		for tbl in tables:
			content = tbl.get_text()
			content = remove_blank_lines(content)
			TablesText.append(content + "\n")
		return TablesText
	except RequestException:
		# Network issue: return empty list so UI can continue without tables
		return []
	except Exception:
		# Any parsing/unexpected errors should not crash the UI
		return []

# Include List of languages in JSON format.
def LanguageJSON():
# Check existence of file before running program.
	try:
		with open('LanguageCodes.json', encoding="utf-8") as json_file:
			data = json.load(json_file)
	except FileNotFoundError:
		wx.MessageBox(_("Some required files are missing."), _("Error"), style=wx.ICON_ERROR)
		exit()

	# Create a empty  list and dictionary.
	name = []
	code = {}

	# Include json file content and add it to list.
	for w in data:
		name.append(w["name"])
		code[w["name"]] = w["code"]

	return name, code

	# Get title and language of any article from its link.
def GetTitleFromURL(url):

	url = urllib.parse.unquote(url)
	url = url.split('/')

	LanguageCode = url[2].split(".")[0]
	title = url[-1]

	code = LanguageJSON()[1]
	keys = list(code.keys())
	Values = list(code.values())
	LanguageName = keys[Values.index(LanguageCode)]

	return title, LanguageName, LanguageCode

# Analyze the text.
def count_text_items(text):
	lines = text.count('\n') + 1
	paragraphs = text.count('\n\n') + 1
	sentences = len(re.findall(r'[^.!?]+[.!?]', text))
	words = len(re.findall(r'\b\w+\b', text))
	characters = len(text) + 1
    
	information = {
	'lines': lines,
	'paragraphs': paragraphs,
	'sentences': sentences,
	'words': words,
	'characters': characters
	}

	return information
