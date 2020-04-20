# Tracks the voting process for a DoV submission

# Imports
import praw
import string
from time import time, sleep

# Config
from config import config

class voting_session:

    def __init__(self, submission, bot_comment=None, session_start_time=None):
        self.submission = submission
        self.is_self_post = submission.is_self

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

            if self.is_self_post:
                print("\tPost is a self")
                self.__post_self_comment()
                submission.mod.remove()
            else:
                print("\tPost is regular")
                self.__post_welcome_comment()
        else:
            raise ValueError("voting_session - __init__() - Bot comment or session start time received without counterpart")

    def __post_welcome_comment(self):
        if self.bot_comment is None:
            # Post bot welcome comment
            self.bot_comment = self.submission.reply( config['welcome_comment_text'] )
            print(f"\tComment added - id: '{self.bot_comment.id}'")
            
            # Distinguish and sticky comment
            self.bot_comment.mod.distinguish(sticky=True)
            print("\tComment stickied")

            # Disable inbox replies
            self.bot_comment.disable_inbox_replies()
            
            self.is_open = True
            self.session_start_time = time()
        else:
            raise ValueError("__post_welcome_comment() - Tried to post more than one welcome comment")

    def __post_self_comment(self):
        if self.bot_comment is None:
            # Post bot self comment
            self.bot_comment = self.submission.reply( config['self_comment_text'] % (self.submission.permalink) )
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
            print("\t\tUser tried to vote more than once - Skipped")


    def __count_replies(self):
        # Refresh comment to load new data
        self.bot_comment.refresh()

        # Get replies to bot comment and send them to be parsed
        print("\tCounting Replies")
        for reply in self.bot_comment.replies:
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
        
        # Get flair choices to select flair ID
        flair_choices = self.submission.flair.choices()

        if   winner == "Neither":
            flair_id = next(item for item in flair_choices if item["flair_text"] == "Neither")["flair_template_id"]
            self.submission.flair.select( flair_id )
        elif winner == "Dead":
            flair_id = next(item for item in flair_choices if item["flair_text"] == "RIP")["flair_template_id"]
            self.submission.flair.select( flair_id )
        elif winner == "Fresh Veggie":
            flair_id = next(item for item in flair_choices if item["flair_text"] == "Fresh Veggie")["flair_template_id"]
            self.submission.flair.select( flair_id )
        elif winner == "Hard to Tell":
            flair_id = next(item for item in flair_choices if item["flair_text"] == "Hard to Tell")["flair_template_id"]
            self.submission.flair.select( flair_id )
        else:
            raise ValueError("__set_submission_flair() - Bad winner input")


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
            edit_comment = config["edit_comment_text"] % ( winner, self.dead_score, self.vegg_score, self.none_score )
            self.bot_comment.edit( edit_comment )

            # Set the submission flair to reflect how users voted
            self.__set_submission_flair(winner) 

        else:
            # If post was removed or deleted delete the bot comment
            self.bot_comment.delete()



        
    def check_session(self):
        # For regular posts
        if not self.is_self_post:
            # Check if post was removed
            if self.submission.author is None or self.submission.removed:
                print(f"Post removed - Closing session - '{self.bot_comment.id}'")
                self.__close_voting_period(removed=True)

            # Check if session time is up
            elif ((time() - self.session_start_time) / 60) > config["minutes"]:
                print(f"Time is up - Closing session - '{self.bot_comment.id}'")
                self.__close_voting_period() 

        # For self posts
        else:
            if self.submission.approved:
                print("Self post approved")
                self.is_open = False
                self.bot_comment.delete()
           
            # Check if session time is up
            elif ((time() - self.session_start_time) / 60) > config["minutes"]:
                print(f"Time is up - Closing session - '{self.bot_comment.id}'")
                self.is_open = False 

            elif self.submission.author is None:
                print(f"Post removed - Closing session - '{self.bot_comment.id}'")
                self.is_open = False
