#/usr/bin/python3
"""
@author Donaldson Tan
@python >= 3
@since 6 March 2016
"""
import time
import json
import subprocess
import os

def splitJSONL(json1, size=10000):
    """
    This method splits the given JSONL into chunks of 10000 JSON blocks, then
    returns the filenames of the JSON chunks. The JSON chunks are stored in /tmp
    """
    files = []
    fileid = 1
    id = 1
    f = open(json1)
    while True:
        files.append("json_"+str(fileid))
        g = open("/tmp/json_"+str(fileid), "w")
        while id % size > 0:
            try:
                line = next(f)[:-1]
            except StopIteration:
                f.close()
                g.close()
                return files
            else:
                meta = {"index": {"_index": "cidb", "_type": "company", "_id": str(id)}}
                print(json.dumps(meta), file=g)
                print(line, file=g)
                id += 1
        meta = {"index": {"_index": "cidb", "_type": "company", "_id": str(id)}}
        print(json.dumps(meta), file=g)
        print(line, file=g)
        id += 1
        g.close()
        fileid += 1
    f.close()
    return files

def indexing(json1, server="http://localhost:9200", size=10000):
    """
    This method indexs data into the Elasticsearch server via the Bulk API
    """
    os.chdir("/tmp")
    devnull = open(os.devnull, "w")
    for fname in splitJSONL(json1, size):
        subprocess.call(["curl", "-s", server+"/_bulk", "--data-binary", "@"+fname], stdout=devnull)

def main(jsonl, server="http://localhost:9200"):
    devnull = open(os.devnull, "w")
    # jsonl must contain the absolute address of the original contractor JSONL file
    jsonl = os.path.abspath(jsonl)
    # reset the elasticsearch database first by deleting the original indexs
    subprocess.call(["curl", "-XDELETE", server+"/cidb"], stdout=devnull)
    print("\ncidb index deleted. begin indexing")
    indexing(jsonl)
    print("cidb data added")

if __name__ == "__main__":
    main("contractors_20150923.jsonl", "http://172.17.0.11:9200")
