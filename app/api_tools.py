from app import database


def get_json_entity(entity_query):
    query_result_proxy = database.session.execute(entity_query)
    row_proxies = [r for r in query_result_proxy]
    if len(row_proxies) == 1:
        json_entity = {k: v for k, v in row_proxies[0].items()}
    else:
        json_entity = {}

    return json_entity