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

def process_item(item, id_map):
  t = item['type']
  if t == 'conference':
    out_file.write("@inproceedings")
  elif t == 'journal':
    out_file.write("@article")

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

  try:
    title = item['title']
  except KeyError:
    raise ConversionException("Missing title")

  try:
    booktitle = item['booktitle']
  except KeyError:
    raise ConversionException("Missing book title")

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

  out_file.write("  title = {" + title + "},\n")

  out_file.write("  booktitle = {" + booktitle + "},\n")

  out_file.write("  year = {" + str(year) + "},\n")

  out_file.write("}\n\n")


id_map = {}
for item in data:
  try:
    process_item(item, id_map)
  except ConversionException as e:
    print "Error while processing an item: " + str(e)
