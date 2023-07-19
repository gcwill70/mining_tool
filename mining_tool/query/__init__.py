
def get_query(data: list[dict], query):
    result = []
    for entry in data:
        if (eval(query)(entry)):
            result.append(entry)
    return result