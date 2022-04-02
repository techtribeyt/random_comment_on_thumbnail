# Changing YouTube Thumbnail
## Where a random comments gets featured every 15 minutes.

I wrote a program that picks a random YouTube comment from the comment section and puts it on the thumbnail automatically every 15 minutes. I made this in order to explore dynamic YouTube videos, or videos where something about the video, often the title or thumbnail, change during the videos lifetime.

**This is currently live!** You can go to my video: https://www.youtube.com/watch?v=RXN1d_UpaAY, and leave a comment. You will be automatically notified by my program when your thumbnail has been featured (just once to not be annoying). You can go straight to the channel and see what the current thumbnail says.

Here is what a thumbnail with a comment looks like:
![Thumbnail](/thumbnail_example.jpg)


The program uses the YouTube API with AWS Lambda to run this code every 15 minutes. I included all of the code I am using here except the authentication. A good authentication tutorial can be found here: https://www.youtube.com/watch?v=vQQEaSnQ_bs.
 
