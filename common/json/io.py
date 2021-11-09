import json


def read(filename):
    """ Reads the file and returns a data object.

    Args:
      filename (str or Path): The file containing the json.  If the file ends
          in `.jsonl`, then will return a list.

    Returns:
      (dict or list or str): The data represented by json in the file.
    """
    if filename.endswith('.jsonl'):
        return read_jsonl(filename)
    with open(filename) as infile:
        return json.load(infile)


def _read_jsonl_as_generator(filename):
    with open(filename) as infile:
        for line in infile:
            if line.strip():
                yield json.loads(line)


def read_jsonl(filename, generator=False):
    jsonl_generator = _read_jsonl_as_generator(filename)
    return jsonl_generator if generator else list(jsonl_generator)


def write(filename, data):
    """ Write json data to filename.

    If filename ends in `jsonl`, then writes each piece of data on a newline.
    """
    if filename.endswith(".jsonl"):
        return write_jsonl(filename, data)

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


def write_jsonl(filename, data):
    """ Write json data to filename as `.jsonl`. """
    with open(filename, 'w') as outfile:
        for obj in data:
            print(json.dumps(obj), file=outfile)
