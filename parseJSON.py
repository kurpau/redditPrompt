import json
import re

'''
Parse JSON output for chatGPT prompt

T: denotes the title of the original post.
C: denotes the content of the original post.
!C: denotes a top-level comment.
!R: denotes a reply to a comment.
!RR: denotes a reply to a reply.
!RRR: denotes a reply to a reply's reply.
U: denotes the upvote count for a comment or reply.

1. Identify the title and content of the original post by looking for the "T:" and "C:" prefixes.
2. Split the input string by the "!" symbol to separate comments and replies.
3. For each separated element, check the prefix to identify whether it's a comment ("C:"), reply ("R:"), reply to a reply ("RR:"), or a reply to a reply's reply ("RRR:").
4. Extract the upvote count for each comment or reply by looking for the "U:" prefix.
5. Maintain a hierarchy and nesting structure based on the prefixes identified in step 3.
6. While creating the article, use the hierarchy and upvote counts to prioritize popular and relevant comments and replies.
'''

def parse_comment(comment, compact_data, level):
    content = comment['content'].replace('\n', ' ').replace('|', '/')
    content = re.sub(' +', ' ', content).strip()
    upvotes = comment['upvotes']
    compact_data.append(f"!{'R' * level}:{content}|U:{upvotes}")

    if 'replies' in comment:
        for reply in comment['replies']:
            parse_comment(reply, compact_data, level + 1)

def json_to_compact_format(json_file):
    with open(json_file, 'r') as infile:
        reddit_data = json.load(infile)

    original_post = reddit_data['original_post']
    title = original_post['title'].replace('\n', ' ').replace('|', '/')
    title = re.sub(' +', ' ', title).strip()
    content = original_post['content'].replace('\n', ' ').replace('|', '/')
    content = re.sub(' +', ' ', content).strip()
    compact_data = [f"T:{title}|C:{content}"]

    for comment in reddit_data['comments']:
        parse_comment(comment, compact_data, 1)

    return '|'.join(compact_data)

compact_format = json_to_compact_format('reddit_data.json')

with open("reddit_data_compact.txt", "w") as outfile:
    outfile.write(compact_format)
