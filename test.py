from calendar import c
import json


def dfs(arr):
    for comment in arr:
        contexts.append(comment['context'].lower().replace('\n\n', ' '))
        dfs(comment['replies'])

with open('articles/fox/science/scientists-find-new-asteroid-crater-shed-light-dinosaurs-extinction/comments.json', 'r') as f:
    comments_json = json.load(f)

contexts = []
dfs(comments_json)

with open('tmp_train.txt', 'w') as f:
    [f.write(c + '\n') for c in contexts][20:]

with open('tmp_test.txt', 'w') as f:
    # [f.write(f'{i}\t0\t1\t{c}') for c, i in enumerate(contexts[:20])]
    [f.write(str(i) + '\t1\t0\t' + c + '\n') for i, c in enumerate(contexts[:20])]


