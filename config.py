wiki_url                = "https://www.reddit.com/r/DeadorVegetable/comments/f2mrpl/dead_or_vegetable_voting_is_live/"

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
                              "Your submission has been temporarily removed because text-posts require mod approval. To get approval, please message the mods with a link to this post within 24 hours.\n\n" + 
                              "Link: www.reddit.com%s",
    minutes                 = 1440,                                                                      # Duration of voting period
    dead_words              = ["dead", "ded", "rip", "rest in peace", "dwad"],
    vegg_words              = ["vegetable", "veggie", "veggies", "veg"],
    none_words              = ["neither", "none"],
)
