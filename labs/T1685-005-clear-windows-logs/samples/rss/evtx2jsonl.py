import sys, json
from evtx import PyEvtxParser

src, dst = sys.argv[1], sys.argv[2]
with open(dst, "w") as out:
    for rec in PyEvtxParser(src).records_json():
        out.write(json.dumps(json.loads(rec["data"])) + "\n")
