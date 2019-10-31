
def convert_to_json(filename):
    """
    Input:
        filename: a string which is the commented text file to be turned into a json file
    Returns:
        a json file

    Strips the commented text file from comments. For a comment to be stripped from the text
    file, the user must use '#' to begin the comment at the very beginning of the line.
    Stripping inline comments is not supported, i.e. the comment must be contained within
    one line. See Inputs/test.txt for an example.
    """
    file_base = filename.replace('.txt','')
    json_filename = file_base + '.json'
    commented_file_reader = open(filename, 'r')
    json_file_writer = open(json_filename, 'w+')

    lines_to_review = commented_file_reader.readlines()
    for line in lines_to_review:
        if not line[0] == '#':
            json_file_writer.write(line)

    commented_file_reader.close()
    json_file_writer.close()
    return json_filename

