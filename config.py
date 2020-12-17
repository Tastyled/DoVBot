from helpers import urlify

wiki_url                = "https://www.reddit.com/r/DeadorVegetable/wiki/dovbot/"
mod_message_url         = "https://www.reddit.com/kd5ed5/"
spoiler_wiki_url        = "https://www.reddit.com/r/DeadorVegetable/wiki/spoilers/"
feedback_url            = "https://www.reddit.com/message/compose?to=DOVBOT&subject=Feedback"

config = dict(
    # Subreddit to monitor
    # subreddit               = "Tastyled_Bot_Testing",
    subreddit               = "DeadorVegetable",

    # Welcome text the bot should comment
    welcome_comment_text    = f"###ATTENTION EVERYBODY ON DEADORVEGETABLE\nBefore discussing the scary polls and answering them inaccurately, **[read our announcement post]({mod_message_url})**.  \nBy lying on these polls you are likely doing much more harm than good. Answer them truthfully.\n"
                              "***\nDead or Vegetable?\n\n" +
                              " * **Reply** to this comment with your opinion.\n" +
                              " * **Upvote** this comment if the post is good.\n" +
                              " * **Downvote** this comment if the post is trash.\n" +
                             f"\nPlease remember to mark news articles and other general spoilers with a [spoiler tag]({spoiler_wiki_url}).\n",

    # Welcome/Closed comment footer
    comment_footer          = f"***\n[^(How to Vote)]({wiki_url}) ^(-) [^(Latest Mod Update)]({mod_message_url}) ^(-) [^(Send Feedback)]({feedback_url})",

    # Welcome text if account is too new or has too little karma
    low_karma_comment       = "Thank you for your submission to r/DeadorVegetable!\n\n" +
                              "Your submission has been automatically removed because your account is too new OR has too little karma. Please continue to build your account to a reputable status so that you may contribute.\n\n" +
                              "Thanks!",

    # Comment after the voting period has ended
    closed_comment_header   = "Voting period has closed. Subject has been deemed: **%s**\n***\n",

    # Layout of the votes histogram
    histogram_layout        = "#####Votes\n" +
                              "| Dead | Veggie | Neither |\n" +
                              "| --- | --- | --- |\n" +
                              "| %d | %d | %d |\n",

    # Comment posted to a self-post
    self_comment_text       = "Thank you for your submission to r/DeadorVegetable!\n\n" +
                              "Your submission has been automatically removed because text-posts require mod approval. If you have not already been approved, please click the link below and hit send.\n\n" +

                              "[Message the Mods](https://www.reddit.com/message/compose?to=" +
                              "%%2Fr%%2F%s&subject=" +
                              urlify("Please Approve my Text Post") + "&message=" +
                              urlify("Hello mod team!\n\nI have not read the rules so I did not get permission to post a text-post before actually doing so. Could you pleeaase approve my post?\n\nThank you!\n\nSincerely,  \n") +
                              "%s" +
                              urlify("\n\nTitle: \"") +
                              "%s" +
                              urlify("\"  \nLink: www.reddit.com/") +
                              "%s) ",

    # Automatic Removal Report Threshold
    report_removal_thresh   = 7,

    # Message to modmail when Report Threshold is met
    automod_mail_message    = "Hello fellow moderators,\n\nI have removed a post for you. It currently has %d reports. Please take a look to see if I did good.\n\nTitle: '%s'  \nUser: /u/%s  \nLink: www.reddit.com/%s",

    # Duration of voting period in minutes
    minutes                 = 1440,
    update_interval         = 30,

    # Automatic Removal Commment Score Threshold
    downvote_removal_thresh = -100,
    downvote_report_thresh  = -10,

    # Words used for voting
    dead_words              = ["dead", "ded", "rip", "dwad"],
    vegg_words              = ["vegetable", "veggie", "veggies", "veg"],
    none_words              = ["neither", "none", "nyet"],

    # Min karma / age an account must be to submit posts
    min_karma_1             = 1500,   # scalar karma value 1
    min_karma_2             = 500,    # scalar karma value 2
    min_age_1               = 1,      # scalar age value 1 in months
    min_age_2               = 6,      # scalar age value 2 in months
    min_comment_karma       = 10,     # minimum comment karma
    min_link_karma          = 1       # minimum post karma
)
