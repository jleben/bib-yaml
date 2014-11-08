import argparse
import yaml
import codecs

parser = argparse.ArgumentParser(description='Translate bibliography from YAML to BIB.')
parser.add_argument('input', nargs=1)
parser.add_argument('output', nargs='?')
a = parser.parse_args()

in_file_name = a.input[0]
out_file_name = None

if a.output != None:
  out_file_name = a.output[0]
else:
  out_file_name = in_file_name.split('.')[0] + ".bib"
  print "output = " + out_file_name

in_file = codecs.open(in_file_name, encoding='utf-8', mode='r')
out_file = codecs.open(out_file_name, encoding='utf-8', mode='w')

yaml_string = in_file.read();
data = yaml.load(yaml_string);

class ConversionException(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


def required_fields():
  return {
    "book": [["author","authors"], "title", "year", "publisher"],
    "journal": [["author","authors"], "title", "journal", "year"],
    "conference": [["author","authors"], "title", "booktitle", "year"],
    "collection": [["author","authors"], "title", "booktitle", "year", "publisher"],
    "masters thesis": [["author","authors"], "title", "school", "year"],
    "phd thesis": [["author","authors"], "title", "school", "year"],
    "tech report": [["author","authors"], "title", "year", "institution", "number"]
  }

def type_identifiers():
  return {
    "book": "@book",
    "journal": "@article",
    "conference": "@inproceedings",
    "collection": "@incollection",
    "masters thesis": "@mastersthesis",
    "phd thesis": "@phdthesis",
    "tech report": "@techreport"
  }

def check_required_fields(item):
  typ = item['type']
  try:
    req_fields = required_fields()[typ]
  except KeyError:
    req_fields = []

  for field in req_fields:
    if type(field) is list:
      ok = False
      for option in field:
        if option in item:
          ok = True
          break
      if not ok:
        msg = "Missing required field:"
        for option in field:
          msg += " '" + option + "'"
          if (option != field.last):
            msg += " or"
        raise ConversionException(msg)
    else:
      if not field in item:
        raise ConversionException("Missing required field: '" + field + "'")


def process_item(item, id_map):
  try:
    typ = item['type']
  except KeyError:
    raise ConversionException("Missing type")

  try:
    out_file.write( type_identifiers()[typ] )
  except KeyError:
    raise ConversionException("Unknown type: " + str(typ))

  out_file.write("{")

  try:
    authors = item['authors']
  except KeyError:
    try:
      authors = [item['author']]
    except KeyError:
      raise ConversionException("Missing author")

  try:
    year = item['year']
  except KeyError:
    raise ConversionException("Missing year")

  check_required_fields(item)

  id = authors[0].split(',')[0] + ":" + str(year)

  count = 0
  try:
    count = id_map[id]
    count = count + 1
  except KeyError:
    count = 0

  id_map[id] = count

  if count > 0:
    id = id + ":" + str(count)

  print "writing: " + id

  out_file.write(id + " ,\n")

  out_file.write("  author = {")
  for a in range(len(authors)):
    out_file.write(authors[a])
    if a < len(authors)-1:
      out_file.write(" and ")
  out_file.write("},\n")

  for field in ['type', 'author', 'authors']:
    try:
      del item[field]
    except KeyError:
      pass

  for key, value in item.items():
    out_file.write("  " + key + " = {")
    if isinstance(value,list):
      for v in range(len(value)):
        out_file.write(value[v])
        if v < len(value)-1:
          out_file.write(" and ")
    else:
      out_file.write(str(value))
    out_file.write("},\n")

  out_file.write("}\n\n")


id_map = {}
for item in data:
  try:
    process_item(item, id_map)
  except ConversionException as e:
    print "*** Error while processing an item: " + str(e)
