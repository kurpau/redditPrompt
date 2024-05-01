import praw
import praw.models
import argparse
import json
import os
from dotenv import load_dotenv

load_dotenv()

# parse the arguments from cli
parser = argparse.ArgumentParser(description='Parse reddit thread to json with upvote threshold')
parser.add_argument('THREAD_ID', help='ID of the reddit thread')
parser.add_argument('-c', '--count', type=int, help='Comments with this many upvotes or more will be parsed')

args = parser.parse_args()

# Set up your Reddit API credentials
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = os.getenv("USER_AGENT")

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=client_id, client_secret=client_secret, user_agent=user_agent
)


# Function to fetch comments recursively
def fetch_comments(comments_list, item, upvote_threshold):
    comments = []
    for comment in comments_list:
        if isinstance(comment, praw.models.MoreComments):
            continue

        if upvote_threshold is not None and comment.ups < upvote_threshold:
            continue

        comment_data = {
            "author": str(comment.author),
            "date": str(comment.created_utc),
            "content": comment.body,
            "upvotes": comment.ups,
            "replies": [],
        }

        if len(comment.replies) > 0:
            comment_data["replies"] = fetch_comments(
                comment.replies, item, upvote_threshold
            )

        comments.append(comment_data)

    return comments


# Function to fetch the Reddit thread data
def fetch_reddit_data(submission_id, upvote_threshold):
    submission = reddit.submission(id=submission_id)

    # Fetch original post data
    original_post = {
        "title": submission.title,
        "author": str(submission.author),
        "date": str(submission.created_utc),
        "content": submission.selftext,
    }

    # Fetch comments and their replies
    submission.comments.replace_more(limit=None)
    comments = fetch_comments(submission.comments, submission, upvote_threshold)

    reddit_data = {"original_post": original_post, "comments": comments}

    return reddit_data


reddit_data = fetch_reddit_data(args.THREAD_ID, args.count)

# Save the Reddit data as a JSON file
with open("reddit_data.json", "w") as outfile:
    json.dump(reddit_data, outfile, indent=2)
