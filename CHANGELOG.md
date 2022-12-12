# 0.2.1
## Changed
- Sort videos/streams according to user selection order.
- Loop in playlist.
## Fixed
- Decreace excution time when there is no need for importing youtube-dl.
- Better handle exiting.

# 0.2.0
## Added
- Respect XDG base directory specification.
- Set channel videos list length via cli argument.
- Show more videos from the prompt, without restarting the tool, by typing the "x" character alone to double the videos amout, or followed with a number of videos to be showed (e.g. x2 or x13).
## Fixed
- Now the progress bar moves when fetching stream or channel videos list data, to be an indication that someting is happening.
## Deleted
- Delete multi channel support, since it conflicts with new features and it makes the code complecated.

# 0.1.0
- (First release)
