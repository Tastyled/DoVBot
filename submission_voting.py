# Tracks the voting process for a DoV submission

# Imports
import praw
from praw.models import MoreComments
import string
from time import time, sleep

# Config
from config import config
from helpers import urlify

class voting_session:

    def __init__(self, submission, low_karma_flag, bot_comment=None, session_start_time=None):
        self.submission = submission
        self.is_self_post = submission.is_self
        self.low_karma_flag = low_karma_flag

        self.voters = []
        self.dead_score = 0
        self.vegg_score = 0
        self.none_score = 0

        self.bot_comment = None

        if bot_comment is not None and session_start_time is not None:
            self.is_open = True
            self.bot_comment = bot_comment
            self.session_start_time = session_start_time

        elif bot_comment is None and session_start_time is None:
            self.is_open = False
            self.session_start_time = 0

            if self.low_karma_flag:
                print("\tUser has too little karma")
                submission.mod.remove(spam=False, mod_note="Account too new/low karma")
                self.__post_low_karma_comment()

            elif self.is_self_post:
                print("\tPost is a self")
                submission.mod.remove(spam=False, mod_note="Text post - require mod approval")
                self.__post_self_comment()

            else:
                print("\tPost is regular")
                self.__post_welcome_comment()
        else:
            raise ValueError("voting_session - __init__() - Bot comment or session start time received without counterpart")

        self.prev_update_time = self.session_start_time

    def __reset_session(self):
        self.low_karma_flag = False
        self.voters = []
        self.dead_score = 0
        self.vegg_score = 0
        self.none_score = 0
        self.bot_comment = None
        self.is_open = False
        self.session_start_time = 0
        self.prev_update_time = 0


    def __reset_votes(self):
        self.voters = []
        self.dead_score = 0
        self.vegg_score = 0
        self.none_score = 0


    def __post_welcome_comment(self):
        if self.bot_comment is None:
            # Post bot welcome comment
            self.bot_comment = self.submission.reply( config['welcome_comment_text'] + config["comment_footer"])
            print(f"\tComment added - id: '{self.bot_comment.id}'")

            # Distinguish and sticky comment
            self.bot_comment.mod.distinguish(sticky=True)
            print("\tComment stickied")

            # Disable inbox replies
            self.bot_comment.disable_inbox_replies()

            self.is_open = True
            self.session_start_time = time()
            self.prev_update_time = self.session_start_time
        else:
            raise ValueError("__post_welcome_comment() - Tried to post more than one welcome comment")


    def __post_self_comment(self):
        if self.bot_comment is None:
            # Post bot self comment
            self.bot_comment = self.submission.reply( config['self_comment_text'] % (config['subreddit'], urlify(self.submission.author.name, False), urlify(self.submission.title, False),  urlify(self.submission.id, False)) )
            print(f"\tComment added - id: '{self.bot_comment.id}'")

            # Distinguish and sticky comment
            self.bot_comment.mod.distinguish(sticky=True)
            print("\tComment stickied")

            # Disable inbox replies
            self.bot_comment.disable_inbox_replies()

            self.is_open = True
            self.session_start_time = time()
        else:
            raise ValueError("__post_self_comment() - Tried to post more than one welcome comment")


    def __post_low_karma_comment(self):
        if self.bot_comment is None:
            # Post bot low karma comment
            self.bot_comment = self.submission.reply( config["low_karma_comment"] )
            print(f"\tComment added - id: '{self.bot_comment.id}'")

            # Distinguish and sticky comment
            self.bot_comment.mod.distinguish(sticky=True)
            print("\tComment stickied")

            # Disable inbox replies
            self.bot_comment.disable_inbox_replies()

            self.is_open = True
            self.session_start_time = time()
        else:
            raise ValueError("__post_low_karma_comment() - Tried to post more than one welcome comment")


    def __parse_tally(self, reply):
        voter = reply.author
        dead_flag = 0
        vegg_flag = 0

        reply_body = reply.body.lower()
        reply_body = reply_body.translate(str.maketrans('', '', string.punctuation))
        reply_body = reply_body.split()

        # Make sure voter has not previously voted
        if voter not in self.voters:
            # Search reply for neither -
            if any(word in reply_body for word in config['none_words']):
                self.none_score += 1        # Skip multi flag checking in case comment reads "neither dead nor veggie" or similar phrasing
                return

            # Search reply for dead words
            if any(word in reply_body for word in config['dead_words']):
                dead_flag = 1
            # Search reply for veggie words
            if any(word in reply_body for word in config['vegg_words']):
                vegg_flag = 1

            # Add vote to the corresponding category
            if dead_flag != vegg_flag:
                if   dead_flag:
                    self.dead_score += 1
                elif vegg_flag:
                    self.vegg_score += 1
                self.voters.append(voter)
            else:
                print("\t\tUser voted for both or no options - Ignored")
        else:
            print("\t\tUser vote already counted - Skipped")


    def __count_replies(self):
        # Refresh comment to load new data
        self.bot_comment.refresh()

        # Get replies to bot comment and send them to be parsed
        print("\tCounting Replies")
        for reply in self.bot_comment.replies:
            if isinstance(reply, MoreComments):
                continue
            if not reply.removed: reply.mod.remove()
            self.__parse_tally(reply)
        print(f"\tReplies - D: {self.dead_score} - V: {self.vegg_score} - N: {self.none_score}")


    def __get_winner(self):
        ds = self.dead_score
        vs = self.vegg_score
        ns = self.none_score

        if not self.is_open:
            if   ns > ds and ns > vs:
                return "Neither"
            elif ds > vs:
                return "Dead"
            elif vs > ds:
                return "Fresh Veggie"
            else:
                return "Hard to Tell"
        else:
            raise ValueError("__get_winner() - Tried to get winner before end of voting period")


    def __set_submission_flair(self, winner):
        print("\tSetting Submission Flair")
        flair_text = ""

        if self.submission.link_flair_text == "NSFL":
            flair_text = "NSFL - "

        # Get flair choices to select flair ID
        flair_choices = self.submission.flair.choices()

        if   winner == "Neither":
            flair_text = flair_text + "Neither"

        elif winner == "Dead":
            flair_text = flair_text + "RIP"

        elif winner == "Fresh Veggie":
            flair_text = flair_text + "Fresh Veggie"

        elif winner == "Hard to Tell":
            flair_text = flair_text + "Hard to Tell"

        else:
            raise ValueError("__set_submission_flair() - Bad winner input")

        flair_id = next(item for item in flair_choices if item["flair_text"] == flair_text)["flair_template_id"]
        self.submission.flair.select( flair_id )


    def __close_voting_period(self, removed=False):
        # Close the voting period
        self.is_open = False

        # Lock the comment to prevent uncounted votes
        self.bot_comment.mod.lock()

        if not removed:
            # Check bot comment for replies
            self.__count_replies()
            winner = self.__get_winner()

            # Next edit the bot comment to display votes
            print("\tEditing Comment")
            edit_comment = config["closed_comment_header"] % ( winner ) + \
                config["histogram_layout"] % ( self.dead_score, self.vegg_score, self.none_score )
            self.bot_comment.edit( edit_comment )

            # Set the submission flair to reflect how users voted
            self.__set_submission_flair(winner)

        else:
            # If post was removed or deleted delete the bot comment
            self.bot_comment.delete()


    def update_count(self):
        edit_comment = config["welcome_comment_text"] + \
            "\n***\nHere's how the score is looking currently:\n\n" + \
            config["histogram_layout"] % (self.dead_score, self.vegg_score, self.none_score) + \
            config["comment_footer"]
        self.bot_comment.edit( edit_comment )
        print("\tCount Updated")


    def check_session(self):

        # Mark post as NSFW is NSFL is flaired
        if self.submission.link_flair_text == "NSFL":
            if not self.submission.over_18:
                self.submission.mod.nsfw()
            # if not self.submission.spoiler:
            #     self.submission.mod.spoiler()

        # Re-sticky if a comment is not stickied already
        if not self.submission.comments[0].stickied:
            self.bot_comment.mod.distinguish(sticky=True)

        # Check if post was deleted
        if self.submission.author is None:
            print(f"Post removed - Closing session - '{self.submission.id}'")

            # For self/low karma posts
            if self.is_self_post or self.low_karma_flag:
                self.is_open = False
                self.bot_comment.delete()

            # For regular posts
            else:
                self.__close_voting_period(removed=True)

        # Check if session time is up
        elif ((time() - self.session_start_time) / 60) > config["minutes"]:
            print(f"Time is up - Closing session - '{self.submission.id}'")

            # For self/low karma/removed posts
            if self.is_self_post or self.low_karma_flag or self.submission.removed:
                self.is_open = False
                self.bot_comment.delete()

            # For regular posts
            else:
                self.__close_voting_period()

            return

        # Check for update interval
        elif ((time() - self.prev_update_time) / 60) > config["update_interval"]:
            if not self.is_self_post and not self.low_karma_flag and not self.submission.removed:
                print(f"Updating count - '{self.submission.id}'")
                self.__count_replies()
                self.update_count()
                self.prev_update_time = time()

        # Check for self post approval
        if self.is_self_post and self.submission.approved:
            print("Self post approved")
            self.is_open = False
            self.bot_comment.delete()

        # Check for low karma post approval
        elif self.low_karma_flag and self.submission.approved:
            print("Low karma post approved")

            # Submission will now act as a regular post, reset all values
            self.bot_comment.delete()
            self.__reset_session()

            # Post voting welcome comment
            self.__post_welcome_comment()
