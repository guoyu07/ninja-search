from flask import Flask, request, render_template
from search import Search
from util import gen_pages, pretty_date
from time import time
import json

app = Flask(__name__)
app.debug = False

@app.route("/", methods=['GET'])
def index():
    
    _from = request.args.get('from')
    if not _from:
        _from = 0

    _from = int(_from)
    q = unicode(request.args.get('q', ''))
    s = request.args.get('s','')
    raw = bool(request.args.get('raw', ''))
    
    if len(q) == 0:
        return render_template("index.html")

    search = Search(index='v2', doc_type='topic')
    search['q'] = "content:%s OR title:%s" % (q, q)
    search['from_'] = _from
    search['sort'] = '_score'

    if s in ["replies", "created"]:
        search['sort'] = "%s:desc"%s
        search.params['body']['min_score'] = 0.2
        
    if s == 'sumup':
        search.params['body']['sort'] = {
            "_script" : {
                "script" : "(doc['created'].value-1272124800000) * log10(doc['replies'].value+1)* log10(doc.score)",
                "type" : "number",
                "params" : {
                    "factor" : 0
                },
                "order" : "desc"
            }
        }

    time0 = time()
    result = search.exe()
    time1 = time()

    if raw:
        return json.dumps(result, indent=True)

    total = result['hits']['total'] 
    current = _from / 10
    max_page = total / 10
    pages = gen_pages(current, max_page)
    return render_template('result.html', res=result, pages=pages, \
        current=current, q=q, s=s, cost=time1-time0, pretty_date=pretty_date, \
        enumerate=enumerate, int=int)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
