import os


def read_txt(infile, delimeter=None, maxsplit=-1, remove_newline=True, cols=None, line_limit=None):
    """读txt文件
    Args:
        infile: input file path
        delimiter
        maxsplit
        remove_newline
        cols: list of index
        num: number of lines that returned
    """

    if cols is not None and type(cols) != list and type(cols) != int:
        raise RuntimeError('cols must be a list or integer')
    if not os.path.exists(infile):
        raise RuntimeError('file not existed: {}'.format(infile))

    content = []
    for l in open(infile, 'r', encoding='utf8'):
        if line_limit is not None and len(content) >= line_limit:
            break
        if remove_newline:
            l = l.rstrip('\n')
        if delimeter is not None:
            l = l.split(delimeter, maxsplit=maxsplit)
            if cols is not None:
                if type(cols) == list:
                    l = [l[index] for index in cols]
                else:  # integer
                    l = l[cols]
        content.append(l)
    return content


def read_jsonl(infile, cols=None, line_limit=None):
    """读jsonl文件

    args:
        cols: 字段, 类型是str或者list of string
    """
    
    if cols is not None and type(cols) != list and type(cols) != str:
        raise RuntimeError('cols must be string or list of string')
    if not os.path.exists(infile):
        raise RuntimeError('file not existed: {}'.format(infile))
    
    content = []
    for l in open(infile, 'r', encoding='utf8'):
        if line_limit is not None and len(content) >= line_limit:
            break
        lj = json.loads(l.rstrip('\n'))
        if cols is not None:
            if type(cols) == list:
                lj = {c: lj.get(c) for c in cols}
            else:  # string
                lj = {c: lj.get(c)}
        content.append(lj)
    return content


def load_txt(infile, delimeter='\t', maxsplit=-1, batch_size=10000, remove_newline=True, cols=None):
    """load text file
    """

    if cols is not None and type(cols) != list and type(cols) != int:
        raise RuntimeError('cols must be a list or integer')
    if not os.path.exists(infile):
        raise RuntimeError('file not existed: {}'.format(infile))
        
    chunk = []
    for l in open(infile, 'r', encoding='utf8'):
        if remove_newline:
            l = l.rstrip('\n')
        if delimeter is not None:
            l = l.split(delimeter, maxsplit=maxsplit)
            if cols is not None:
                if type(cols) == list:
                    l = [l[index] for index in cols]
                else:  # integer
                    l = l[cols]
        chunk.append(l)
        if len(chunk) >= batch_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
