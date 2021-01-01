from googleapiclient.discovery import build
import re
API_KEY = 'AIzaSyCMyjscMagziCumgZ2IOMIZgko5XDS9G-k'
# Initiliaze youtube service
youtube = build('youtube','v3',developerKey = API_KEY)


class UserResponse:
    """
    A class used to represent the input from the user to the API

    . . .

    Methods
    _ _ _ _
    get_category(self)
        Returns the category that matches in the video categories in the youtube API
    auto_correct(self,user_response)
        Returns a str that has a higher chance of success for the Api

    Exception
    _ _ _ _ _
    Raises Error:
        If the input is not supported by the youtube api as
        one of it's categories
    """
    def __init__(self):
        pass


    def auto_correct(self,user_response):
        pattern = re.compile(r'[^a-zA-z\s]')
        # Strip characters that are not letter or spaces
        # to improve the chances of matching
        user_response = pattern.sub("",user_response)
        # Since the api response use & instead of and
        # subsitute 'and' with & in the text
        # to increase the chances of success
        user_response =  re.sub(r"\band\b","&",user_response)
        return user_response

    def get_category(self):
        user_response = input("What category do u want to analyse from the youtube popular page ?")
        categories = youtube.videoCategories().list(part='snippet',regionCode="US")
        categories_response = categories.execute()
        for category in categories_response["items"]:
            # Match category title and return the title with user-response in it
            # while ignoring case
            if re.match(fr"{self.auto_correct(user_response)}",category["snippet"]["title"],re.IGNORECASE):
                # Return id associated with it
                return (category["id"],category["snippet"]["title"])
        #Raise exception if no match from api can be found
        raise Exception("Input Not Valid")


class ApiResponse:
    """
    A class that is used to represent the response
    from the API back to the user

    . . .

    Attributes
    _ _ _ _ _ _
    list_of_video_ids:list
        A list of video ids that match the category the user inputs
    category:str
        The category that the user inputs so that data from
        the API can be matched

    Methods
    _ _ _ _ _
    scrape_for_content(self,content_type):
        Returns relevant data for the type of data that we want to parse
        from the API. Example input for content_type ="snippet" or "statistics"
    scrape_for_videos(self)
        Return self to allow for method chaining for the usage
        of scrape_for_content function to allow it to scrape
        for different types of content while also appending
        videos that have the same category as user to the list
    """
    def __init__(self, category):
        self.list_of_video_ids = []
        self.category = category


    def scrape_for_content(self,content_type):
        # Obtain the csv values for the video_ids in the list
        csv_values = ",".join(self.list_of_video_ids)
        # Scrape for data based on content_type
        videos_recording = youtube.videos().list(part=content_type, id=csv_values)
        recording_response = videos_recording.execute()
        return recording_response

    def scrape_for_videos(self):
        nextPageToken = None
        # Scrape for videos until there is no more pages or there is a total result of 100 videos
        while True:
            # Obtain snippet data from youtube API
            videos = youtube.videos().list(part="snippet",chart="mostPopular",maxResults=50, pageToken=nextPageToken)
            videos_response = videos.execute()
            if len(self.list_of_video_ids) == 100:
                break
            # As the youtube API does not support videoCategoryId and return videos with
            # tags under the same category but is not considered under the same category
            # it iterates through the whole list and return videos under that category
            for videos in videos_response["items"]:
                if videos["snippet"]["categoryId"] == self.category:
                    self.list_of_video_ids.append(videos["id"])
            # Go on to the next Page
            nextPageToken = videos_response.get('nextPageToken')
            if not nextPageToken:
                break
        return self

    def scrape_for_channel_stats(self,channel_id):
        # Using channel id to obtain channel statistics
        channel = youtube.channels().list(part="statistics",id=channel_id)
        channel_response = channel.execute()
        return channel_response
