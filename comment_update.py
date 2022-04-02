from PIL import Image
from PIL import ImageFont 
from PIL import ImageDraw
from authentication import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import random
from better_profanity import profanity
from string import ascii_letters
import textwrap
import datetime

# main function to update title and thumbnail
def update_video(): 
    # set up YouTube API object
    credentials = get_credentials()
    youtube = build('youtube', 'v3', credentials=credentials, cache_discovery=False)
    
    # choose random comment
    comment_id, author, comment = get_random_comment(youtube)

    # create new thumbnail
    create_thumbnail(author, comment)
    
    # change video thumbnail
    update_video_thumbnail(youtube, "VIDEO_ID", "/tmp/edited.png")
    
    # leave reply to let person know thumbnail has changed
    leave_reply(youtube, comment_id, author)
    
# return random comment
def get_random_comment(youtube):
    comments = get_video_comments_list(youtube, "VIDEO_ID")
    choice = random.choice(comments)
    while profanity.contains_profanity(choice[1]) or profanity.contains_profanity(choice[2]):
        choice = random.choice(comments)
    return choice

def leave_reply(youtube, comment_id, author):
    if should_leave_reply(youtube, comment_id):
        request = youtube.comments().insert(
            part="snippet,id",
            body={
              "snippet": {
                "parentId": comment_id,
                "textOriginal": make_comment(author)
              }
            }
        )
        request.execute()
  

# make a random comment reply so that they are not all identical
def make_comment(author):
    greetings = ["Hey", "Hi", "Hello"]
    thanks = ["Thank you for the comment", "Thanks for commenting", "I appreciate the comment"]
    return f"{random.choice(greetings)} {author}! {random.choice(thanks)}! Your comment was featured on this video's thumbnail at {datetime.datetime.utcnow().strftime('%b %d, %Y %H:%M')} UTC."
        
def should_leave_reply(youtube, comment_id):
    # leave reply if I have not yet commented about this comment being featured (using word featured)
    request = youtube.comments().list(
        part = "snippet",
        parentId = comment_id
    )
    response = request.execute()
    for i in range(len(response['items'])):
        
        # if there is a reply written by me
        if response['items'][i]['snippet']['authorChannelId']['value'] == 'CHANNEL_ID':
            
            # and contains the word featured
            if "featured" in response['items'][i]['snippet']['textDisplay']:
                return False
    return True
   
# function that saves the thumbnail
def create_thumbnail(comment_author, comment): 
    # load background image
    img = Image.open("thumbnail.png")
    
    # load font
    font = ImageFont.truetype("OpenSans-Bold.ttf", 120)
    
    # set up drawing and font
    draw = ImageDraw.Draw(img)    
    
    # Calculate the average length of a single character of our font.
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    
    # Translate this average length into a character count
    max_char_count = int(img.size[0] * 0.7 / avg_char_width)
    
    # Calculate how many lines at this size can be fit
    max_lines = int(((2/3*img.size[1]) / max(font.getsize(char)[0] for char in ascii_letters)))
    
    # trimming comment to fit within image
    comment = comment[:max_lines * max_char_count]
    
    # Create a wrapped text object using scaled character count
    text = textwrap.fill(text=comment, width=max_char_count)
    text_list = text.split("\n")
    
    # cut off extra lines
    text_list = text_list[:max_lines]
    
    # calculate starting point
    current_h = 225 + 50 * (max_lines - len(text_list))
    
    # draw line by line (will be centered)
    for line in text_list:
        w, h = draw.textsize(line, font=font)
        draw.text((img.size[0] / 2, current_h), line, font=font, anchor='mm')
        current_h += h
    
    # trim comment author to fit
    if len(comment_author) > 17:
        comment_author = comment_author[:17] + "..."
    draw.text(xy=(img.size[0] / 2, 25), text=f"{comment_author} says:", font=font, fill='#00ffff', anchor='mt', spacing=5)
    
    # save new thumbnail
    img.save("/tmp/edited.png")
    
def update_video_thumbnail(youtube, video_id, thumbnail_path):
    request = youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path)
    )
    request.execute()
    
def get_video_comments_list(youtube, video_id):
    # empty list for storing (commentId, author, reply)
    comments = []

    # retrieve youtube video results
    video_response=youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    ).execute()

    # iterate video response
    while video_response:
        # extracting required info
        # from each result object 
        for item in video_response['items']:

            # Extracting comments
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append((item['id'], author, comment))
        
        # Again repeat
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                    part = 'snippet',
                    videoId = video_id,
                    pageToken=video_response['nextPageToken'],
                    maxResults=100,
                    textFormat="plainText"
                ).execute()
        else:
            break
    return comments
