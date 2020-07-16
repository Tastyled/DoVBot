#! /usr/bin/env python3

# Main running script for DoV Bot

# Imports
import threading
import praw, prawcore
import sqlite3
import string
from time import sleep

# Keys and Config
from keys import keys
from config import config

# Submission Vote
from submission_voting import voting_session

# Database Connection and Table Creation
sql_config = sqlite3.connect('submissions.db')
sql_cursor = sql_config.cursor()
sql_cursor.execute(
    "CREATE TABLE IF NOT EXISTS 'submissions' (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id TEXT, bot_comment_id TEXT, bot_comment_time INTEGER, closed INTEGER DEFAULT 0)")

# Reddit API Connection
reddit = praw.Reddit(client_id=keys['client_id'],
                     client_secret=keys['client_secret'],
                     user_agent=keys['user_agent'],
                     username=keys['username'],
                     password=keys['password'])
print("Logged in")

# Arrays for storing submissions and open voting sessions
synced_posts = []
open_sessions = []


# Get list of banned words
banned_words = []
for line in open("banned_words.txt", 'r'):
    banned_words.append(line.strip())


def get_db():
    # Database Connection and Table Creation
    sql_config = sqlite3.connect('submissions.db')
    sql_cursor = sql_config.cursor()
    sql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS 'submissions' (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id TEXT, bot_comment_id TEXT, bot_comment_time INTEGER, closed INTEGER DEFAULT 0)")
    return sql_config, sql_cursor


def load_db_data( sql_cursor ):
    # Sync previously read posts
    for result in sql_cursor.execute(
            "SELECT submission_id FROM submissions"):
        print(f"\tAdding previous submission to memory - id: '{result[0]}'")
        synced_posts.append(result[0])

    # Check for previously active sections
    for result in sql_cursor.execute(
            "SELECT submission_id, bot_comment_id, bot_comment_time FROM submissions WHERE closed IS 0"):
        submission          = reddit.submission(id=result[0])
        bot_comment         = reddit.comment(id=result[1])
        bot_comment_time    = int(result[2])
        print(f"\tAdding open session to memory - id: '{bot_comment.id}'")
        open_sessions.append(voting_session(submission, bot_comment, bot_comment_time))

def send_message(user, subject, message):
    if len(message) > 10000:
        message = message[0:9900]
        message = message + "...\n\n(Message cut because it is too long)"
    reddit.redditor(user).message(subject, message)

def submission_watch( subreddit ):
    # Submission waiting thread
    sql_config, sql_cursor = get_db()
    print("Starting Submission Thread")

    while True:
        try:
            for submission in subreddit.stream.submissions():
                if submission is not None:  # Check if a post is found
                    if submission.id not in synced_posts:  # Check if submission wasn't synced yet
                        print(f"New post from user: '{submission.author}' id: '{submission.id}'")
                        send_message("Tastyled", f'New Post in r/{submission.subreddit.display_name}', f'{submission.permalink}')
                        # Create new voting session
                        new_session = voting_session( submission )
                        print("\tSession created")
                        # Record new session
                        open_sessions.append( new_session )
                        print("\tAdded to memory")
                        
                        # Add to database
                        sql_cursor.execute(
                            "INSERT INTO submissions (submission_id, bot_comment_id, bot_comment_time) VALUES (?,?,?)",
                            (submission.id, new_session.bot_comment.id, int(new_session.session_start_time)))
                        print("\tAdded to database")
                        sql_config.commit()  # commit database changes
                        print("\tChanges committed")

                        # Add to synced posts
                        synced_posts.append(submission.id)
                        print("\tAdded to synced posts")

                    else:
                        # print(f"Skipping previously read post")
                        pass
        except prawcore.exceptions.ServerError as e:
            print(f"\n\n{e}")
            print("Server Error, thread waiting 30 seconds for retry")
            sleep(30)
            print("Restarting Submission Thread")

    raise ValueError("SUBMISSION THREAD EXITING")


def session_watch():
    # Voting session waiting thread
    sql_config, sql_cursor = get_db()
    print("Starting Voting Session Thread")

    while True:
        try:
            for session in open_sessions:
                # Check active voting session timers

                # Refresh Submission
                submission_id = session.submission.id
                session.submission = reddit.submission(id=submission_id)

                # Check the session
                session.check_session()

                # Closed voting sessions
                if not session.is_open:
                    # Mark session as closed in database
                    sql_cursor.execute(
                        f"UPDATE submissions SET closed = 1 WHERE submission_id = '{session.submission.id}'"
                    )
                    print("\tUpdating database")
                    sql_config.commit()  # commit database changes
                    print("\tChanges committed")

                    # Remove closed session from memory
                    open_sessions.remove(session)
                    del session
                    print("\tRemoved from memory")

        except prawcore.exceptions.ServerError as e:
            print(f"\n\n{e}")
            print("Server Error, thread waiting 30 seconds for retry")
            sleep(30)
            print("Restarting Session Thread")

    raise ValueError("SESSION THREAD EXITING")


def comment_watch( subreddit ):
    # Comment Watch Thread
    print("Starting Comment Checking Thread")
    vote_words = config['dead_words'] + config['vegg_words'] + config['none_words']

    while True:
        try:
            for comment in subreddit.stream.comments(skip_existing=True):
                if comment is not None:
                    body = comment.body.lower()
                    body = body.translate(str.maketrans('', '', string.punctuation))
                    body = body.split()

                    # Check comment for any banned words
                    if any(word in body for word in banned_words):
                        send_message("Tastyled", "Potential Hate Speach Detected",
                        "Potential Hate Speach Detected\n\n" +
                        f"User: /u/{comment.author}  \n" +
                        f"Comment: '{comment.body}'\n\n" +
                        f"{comment.permalink}")

                    # Check comment for vote word
                    if comment.parent_id == comment.link_id:                            # Check only top level comments
                        if len(body) == 1 and any(word in body for word in vote_words): # Check if comment is one word vote reply

                            print("Removing spam comment")
                            comment.mod.remove(spam=False, mod_note="Voting outside of voting thread")

                            print("Sending Message to user")
                            send_message(comment.author.name, "Notice of Comment Removal",
                            f"Thank you for you participating in /r/DeadorVegetable!\n\n" +
                            "Unfortunately your comment has been removed because we are trying to keep top level comments reserved for discussion. " +
                            "If you are trying to vote on the post's classification please reply to /u/DOVBOT's comment, not the post itself. " +
                            "Keep in mind, if the post is more than 24 hours old, you can no longer vote.\n\n" +
                            "If you think this was done in error, please respond to this message and your comment will be reexamined by the mods.\n\n" 
                            f"Comment: \"{comment.body}\"  \n"
                            f"Link: {comment.permalink}"                          
                            )
                            
                            # send_message("Tastyled", "Comment Removed",
                            # f"Comment Removed\n\nuser: /u/{comment.author.name}  \nlink: {comment.permalink}  \ncomment: \"{comment.body}\"")

                            print("Done")

        except prawcore.exceptions.ServerError as e:
            print(f"\n\n{e}")
            print("Server Error, thread waiting 30 seconds for retry")
            sleep(30)
            print("Restarting Comment Thread")

    raise ValueError("COMMENT THREAD EXITING")


def inbox_watch():
    # Inbox Checking Thread
    print("Starting Inbox Check Thread")
    
    while True:
        try:
            for m in reddit.inbox.unread():
                if m is not None:
                    print("Message Received - Forwarding")
                    send_message("Tastyled", 
                        f"Message received from user: /u/{m.author}",
                        f"/u/{m.author}  \n" +
                        f"Subject: {m.subject}\n\n" +
                        f"{m.body}" )
                    m.mark_read()
                
        except prawcore.exceptions.ServerError as e:
            print(f"\n\n{e}")
            print("Server Error, thread waiting 30 seconds for retry")
            sleep(30)
            print("Restarting Inbox Thread")

    raise ValueError("INBOX THREAD EXITING")


# Subreddit Work
def main():
    # Initialize memory from database
    print("Loading database")
    sql_config, sql_cursor = get_db()
    load_db_data(sql_cursor)

    subreddit = reddit.subreddit(config['subreddit'])

    print("Ready.")

    try:
        submission_thread   = threading.Thread(target=submission_watch, args=(subreddit,))
        session_thread      = threading.Thread(target=session_watch)
        comment_thread      = threading.Thread(target=comment_watch, args=(subreddit,))
        inbox_thread        = threading.Thread(target=inbox_watch)

        submission_thread.setDaemon(True)
        session_thread.setDaemon(True)
        comment_thread.setDaemon(True)
        inbox_thread.setDaemon(True)

        submission_thread.start()
        session_thread.start()
        comment_thread.start()
        inbox_thread.start()

        while True: sleep(100)

    except (KeyboardInterrupt, SystemExit):
        print("Received Keyboard Interrupt")
        exit()

main()
