from helpers import urlify

wiki_url                = "https://www.reddit.com/r/DeadorVegetable/wiki/dovbot/"
mod_message_url         = "https://www.reddit.com/r/DeadorVegetable/comments/j1ib2l/major_update_reporting_rules_and_nsfl_tags/"
mod_app_url             = "https://www.reddit.com/r/DeadorVegetable/comments/jcm9pj/rdeadorvegetable_is_looking_to_expand_the_mod_team/"

config = dict(
    # Subreddit to monitor
    # subreddit               = "Tastyled_Bot_Testing",
    subreddit               = "DeadorVegetable",

    # Welcome text the bot should comment
    welcome_comment_text    = "***\nDead or Vegetable? Reply to **this comment** with your opinion." +
                              "\n\nDon't spoil the fun! Please remember to mark news articles and other general spoilers with a spoiler tag >!\>!like this!\<!<\n***\n" +
                            #   "Good post? **Upvote** this comment. Bad post? **Downvote**.\n***\n" +
                              f"^(For more info:) [^(How Voting Works)]({wiki_url}) ^(-) [^(Latest Mod Update)]({mod_message_url}) ^(-) [^(Apply to be a Mod)]({mod_app_url})",

    # Welcome text if account is too new or has too little karma
    low_karma_comment       = "Thank you for your submission to r/DeadorVegetable!\n\n" +
                              "Your submission has been automatically removed because your account is too new OR has too little karma. Please continue to build your account to a reputable status so that you may contribute.\n\n" +
                              "Thanks!",

    # Comment after the voting period has ended
    edit_comment_text       = "Voting period has closed. Subject has been deemed: **%s**\n***\n" +
                              "#####Votes\n" +
                              "| Dead | Veggie | Neither |\n" +
                              "| --- | --- | --- |\n"
                              "| %d | %d | %d |\n***\n" +
                              f"^(For more info:) [^(How Voting Works)]({wiki_url}) ^(-) [^(Latest Mod Update)]({mod_message_url}) ^(-) [^(Apply to be a Mod)]({mod_app_url})",

    # Comment posted to a self-post
    self_comment_text       = "Thank you for your submission to r/DeadorVegetable!\n\n" +
                              "Your submission has been automatically removed because text-posts require mod approval. If you have not already been approved, please click the link below and hit send.\n\n" +

                              "[Message the Mods](https://www.reddit.com/message/compose?to=" +
                              "%%2Fr%%2F%s&subject=" +
                              urlify("Please Approve my Text Post") + "&message=" +
                              urlify("Hello mod team!\n\nI have not read the rules so I did not get permission to post a text-post before actually doing so. Could you pleeaase approve my post so that I may give my two cents about the community?\n\nThank you!\n\nSincerely,  \n") +
                              "%s" +
                              urlify("\n\nTitle: \"") +
                              "%s" +
                              urlify("\"  \nLink: www.reddit.com") +
                              "%s) ",

    # Automatic Removal Report Threshold
    report_thresh           = 10,

    # Message to modmail when Report Threshold is met
    automod_mail_message    = "Hello fellow moderators,\n\nI have removed a post for you. It currently has %d reports. Please take a look to see if I did good.\n\nTitle: '%s'  \nUser: /u/%s  \nLink: www.reddit.com%s",

    # Duration of voting period in minutes
    minutes                 = 1440,

    # Words used for voting
    dead_words              = ["dead", "ded", "rip", "dwad"],
    vegg_words              = ["vegetable", "veggie", "veggies", "veg"],
    none_words              = ["neither", "none", "nyet"],

    # Min karma / age an account must be to submit posts
    min_karma_1             = 1500,   # scalar karma value 1
    min_karma_2             = 500,    # scalar karma value 2
    min_age_1               = 1,      # scalar age value 1 in months
    min_age_2               = 6,      # scalar age value 2 in months
)
