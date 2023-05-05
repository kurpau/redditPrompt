import praw
import json

# Set up your Reddit API credentials
client_id = "RRQ6eWPHJ0yy6O2ReiZ60w"
client_secret = "eSh7br4E_Edl7ode9pfQRK8_ECqPpw"
user_agent = "Python:praw (by /u/kurpau)"

# Initialize Reddit instance
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)

# Function to fetch comments recursively
def fetch_comments(comments_list, item, upvote_threshold):
    comments = []
    for comment in comments_list:
        if isinstance(comment, praw.models.MoreComments):
            continue

        if comment.ups < upvote_threshold:
            continue

        comment_data = {
            "author": str(comment.author),
            "date": str(comment.created_utc),
            "content": comment.body,
            "upvotes": comment.ups,
            "replies": []
        }

        if len(comment.replies) > 0:
            comment_data["replies"] = fetch_comments(comment.replies, item, upvote_threshold)

        comments.append(comment_data)

    # Sort comments by upvotes in descending order
    comments.sort(key=lambda x: x["upvotes"], reverse=True)

    return comments

# Function to fetch the Reddit thread data
def fetch_reddit_data(submission_id, upvote_threshold):
    submission = reddit.submission(id=submission_id)

    # Fetch original post data
    original_post = {
        "title": submission.title,
        "author": str(submission.author),
        "date": str(submission.created_utc),
        "content": submission.selftext
    }

    # Fetch comments and their replies
    submission.comments.replace_more(limit=None)
    comments = fetch_comments(submission.comments, submission, upvote_threshold)

    reddit_data = {
        "original_post": original_post,
        "comments": comments
    }

    return reddit_data

# Replace "SUBMISSION_ID" with the actual submission ID
upvote_threshold = 20
post_id = "137xmm0"
reddit_data = fetch_reddit_data(post_id, upvote_threshold)

# Save the Reddit data as a JSON file
with open("reddit_data.json", "w") as outfile:
    json.dump(reddit_data, outfile, indent=2)
