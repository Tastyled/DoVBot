#! /usr/bin/env python3

# Main running script for DoV Bot

# Imports
import threading
import praw, prawcore
import sqlite3
import string
from time import sleep
import datetime

# Keys and Config
from keys import keys
from config import config

# Submission Vote
from submission_voting import voting_session


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


def get_db():
    # Database Connection and Table Creation
    sql_config = sqlite3.connect('submissions.db')
    sql_cursor = sql_config.cursor()
    sql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS 'submissions' (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id TEXT, low_karma INT, bot_comment_id TEXT, bot_comment_time INTEGER, closed INTEGER DEFAULT 0)")
    try:
        sql_cursor.execute(
            "ALTER TABLE 'submissions' ADD COLUMN low_karma INT")
    except sqlite3.Error as err:
        # print(f"{err} - ignoring")
        pass
    return sql_config, sql_cursor


def in_whitelist( subreddit, redditor ):
    username = redditor.name.lower()

    # Get Wiki
    wl_wiki = subreddit.wiki["whitelist"]
    whitelist = (wl_wiki.content_md)

    # Parse wiki for whitelist
    for line in whitelist.splitlines():
        line = line.lower().rstrip()
        if line == username:
            print("\tUser in whitelist")
            return True
    return False


def failure_wait_retry(error, threadname):
    print(f"\n\n{error}")
    print(f"{threadname} waiting 30 seconds for retry")
    sleep(30)
    print(f"Restarting {threadname} Thread")


def load_db_data( sql_cursor ):
    # Sync previously read posts
    for result in sql_cursor.execute(
            "SELECT submission_id FROM submissions"):
        print(f"\tAdding previous submission to memory - id: '{result[0]}'")
        synced_posts.append(result[0])

    # Check for previously active sections
    for result in sql_cursor.execute(
            "SELECT submission_id, low_karma, bot_comment_id, bot_comment_time FROM submissions WHERE closed IS 0"):
        submission          = reddit.submission(id=result[0])
        low_karma_flag      = bool(result[1])
        bot_comment         = reddit.comment(id=result[2])
        bot_comment_time    = int(result[3])
        print(f"\tAdding open session to memory - id: '{bot_comment.id}'")
        open_sessions.append(voting_session(submission, low_karma_flag, bot_comment, bot_comment_time))


def send_message(user, subject, message):
    if len(message) > 10000:
        message = message[0:9900]
        message = message + "...\n\n(Message cut because it is too long)"
    reddit.redditor(user).message(subject, message)


def karma_needed(age):
    y_1 = config["min_karma_1"]
    y_2 = config["min_karma_2"]
    x_1 = config["min_age_1"]
    x_2 = config["min_age_2"]

    m = (y_2 - y_1)/(x_2 - x_1)
    b = (-1 * m * x_1) + y_1
    return (m * age) + b


def good_account( redditor ):

    total_karma = redditor.comment_karma + redditor.link_karma

    current_time = datetime.datetime.utcnow().timestamp()
    account_age = current_time - redditor.created_utc

    account_age /= 2629800 # convert to months

    if   account_age < config["min_age_1"]:
        return False
    elif total_karma < config["min_karma_2"]:
        return False
    elif total_karma < karma_needed(account_age):
        return False

    return True

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
                        if submission.is_self:
                            send_message("Tastyled", f'New self-post in r/{submission.subreddit.display_name}', f'www.reddit.com/{submission.id}')

                        # Check for low karma / account age
                        low_karma_flag = not in_whitelist( subreddit, submission.author ) and not good_account( submission.author )

                        # Create new voting session
                        new_session = voting_session( submission, low_karma_flag )
                        print("\tSession created")

                        # Record new session
                        open_sessions.append( new_session )
                        print("\tAdded to memory")

                        # Add to database
                        sql_cursor.execute(
                            "INSERT INTO submissions (submission_id, low_karma, bot_comment_id, bot_comment_time) VALUES (?,?,?,?)",
                            (submission.id, low_karma_flag, new_session.bot_comment.id, int(new_session.session_start_time)))
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
            failure_wait_retry(e, "submissions")
        except prawcore.exceptions.RequestException as e:
            failure_wait_retry(e, "submissions")
        except prawcore.exceptions.ResponseException as e:
            failure_wait_retry(e, "submissions")


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

                # Get current low karma flag
                low_karma_check = session.low_karma_flag

                # Check the session
                session.check_session()

                # If low karma flag has changed, update database
                if low_karma_check and not session.low_karma_flag:
                    sql_cursor.execute(
                        f"UPDATE submissions SET "\
                        f"low_karma = 0, "\
                        f"bot_comment_id = '{session.bot_comment.id}', "\
                        f"bot_comment_time = {int(session.session_start_time)} "\
                        f"WHERE submission_id = '{session.submission.id}'"
                    )
                    print("\tUpdating database")
                    sql_config.commit()  # commit database changes
                    print("\tChanges committed")

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
            failure_wait_retry(e, "sessions")
        except prawcore.exceptions.RequestException as e:
            failure_wait_retry(e, "sessions")
        except prawcore.exceptions.ResponseException as e:
            failure_wait_retry(e, "sessions")

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

                    # Check comment for vote word
                    if comment.parent_id == comment.link_id:                            # Check only top level comments
                        if len(body) == 1 and any(word in body for word in vote_words): # Check if comment is one word vote reply

                            print("Removing spam comment")
                            comment.mod.remove(spam=False, mod_note="Voting outside of voting thread")

                            print("Done")

        except prawcore.exceptions.ServerError as e:
            failure_wait_retry(e, "comments")
        except prawcore.exceptions.RequestException as e:
            failure_wait_retry(e, "comments")
        except prawcore.exceptions.ResponseException as e:
            failure_wait_retry(e, "comments")

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
            failure_wait_retry(e, "inbox")
        except prawcore.exceptions.RequestException as e:
            failure_wait_retry(e, "inbox")
        except prawcore.exceptions.ResponseException as e:
            failure_wait_retry(e, "inbox")

    raise ValueError("INBOX THREAD EXITING")

def queue_watch( subreddit ):
    # Mod Queue Checking Thread
    print("Starting Queue Check Thread")

    while True:
        try:
            for reported_item in subreddit.mod.reports("submissions"):
                # print(f"{reported_item.title}")

                if not reported_item.approved and len(reported_item.user_reports) >= config["report_thresh"]:
                    print("Report threshold met - removing post")
                    reported_item.mod.remove(spam=False, mod_note="Report Threshold Met - Need moderator approval")
                    Message = config['automod_mail_message'] % (len(reported_item.user_reports), reported_item.title, reported_item.author, reported_item.id)
                    Message += "  \nReports:  \n"
                    for report in reported_item.user_reports:
                        Message += f"{report}  \n"
                    subreddit.message("I Removed a Post", Message )


        except prawcore.exceptions.ServerError as e:
            failure_wait_retry(e, "queue")
        except prawcore.exceptions.RequestException as e:
            failure_wait_retry(e, "queue")
        except prawcore.exceptions.ResponseException as e:
            failure_wait_retry(e, "queue")

    raise ValueError("QUEUE THREAD EXITING")

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
        queue_thread        = threading.Thread(target=queue_watch, args = (subreddit,))

        submission_thread.setDaemon(True)
        session_thread.setDaemon(True)
        comment_thread.setDaemon(True)
        inbox_thread.setDaemon(True)
        queue_thread.setDaemon(True)

        submission_thread.start()
        session_thread.start()
        comment_thread.start()
        inbox_thread.start()
        queue_thread.start()

        while True: sleep(100)

    except (KeyboardInterrupt, SystemExit):
        print("Received Keyboard Interrupt")
        exit()

main()
