import re,ast


def synthetic_literal_eval(raw):
    subthings = re.search(r"\[(.|\n)*\]",raw).group(0)

    pattern = re.compile(r'\{(.|\n)*?\}')
    records = []
    for item in re.finditer(pattern,subthings):
        print('Aaa',item.group(0))
        records.append(ast.literal_eval(item.group(0)))

    print('Got',len(records))
    return {"records" : records}
