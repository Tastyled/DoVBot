from helpers import urlify

wiki_url                = "https://www.reddit.com/r/DeadorVegetable/wiki/dovbot"

config = dict(
    # subreddit               = "Tastyled_Bot_Testing",                                                    # Subreddit
    subreddit               = "DeadorVegetable",                                                        # Subreddit
    welcome_comment_text    = "Dead or Vegetable?\n\nReply to **this comment** with your opinion.\n***\n" +    # Welcome text the bot should comment
                            #   "Good post? **Upvote** this comment. Bad post? **Downvote**.\n***\n" +
                              f"^^More ^^Info ^^[Here]({wiki_url})",                         
    edit_comment_text       = "Voting period has closed. Subject has been deemed: **%s**\n***\n" +         # Comment after the voting period has ended
                              "##Votes\n" +
                              "| Dead | Veggie | Neither |\n" +
                              "| --- | --- | --- |\n"
                              "| %d | %d | %d |\n***\n" +
                              f"^^More ^^Info ^^[Here]({wiki_url})",
    self_comment_text       = "Thank you for your submission to r/DeadorVegetable!\n\n" +             # Comment posted to a self-post
                              "Your submission has been temporarily removed because text-posts require mod approval. If you have not already been approved, please click the link below and hit send.\n\n" +
                              
                              "[Message the Mods](https://www.reddit.com/message/compose?to=" +
                              "%%2Fr%%2f%s&subject=" +
                              urlify("Please Approve my Text Post") + "&message=" +
                              urlify("Hello mod team!\n\nI have not read the rules so I did not get permission to post a text-post before actually doing so. Could you pleeaase approve my post so that I may give my two cents about the community?\n\nThank you!\n\nSincerely,  \n") +
                              "%s" +
                              urlify("\n\nTitle: \"") +
                              "%s" +
                              urlify("\"  \nLink: www.reddit.com") +
                              "%s) ",

    minutes                 = 1440,                                                                      # Duration of voting period
    dead_words              = ["dead", "ded", "rip", "dwad"],
    vegg_words              = ["vegetable", "veggie", "veggies", "veg"],
    none_words              = ["neither", "none"],
)
