from duckduckgo_search import DDGS

def search_web(query):
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
    return results

# هنا يمكنك إضافة نظام Vector Search لاحقاً لربط مشاريعك
