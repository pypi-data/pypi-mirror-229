
import sys
import os
sys.path.append(sys.path.append(os.getcwd()))
from dotenv import load_dotenv
load_dotenv()
from profile_local.src.generic_profile_insert import generic_profile_insert
from logger_local.Logger import Logger
from circles_importer import importer
import json
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from profile_reddit_restapi_imp_python_package.constants import PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID, PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME
from profile_reddit_restapi_imp_python_package.search_reddit import Reddit
from our_url.src.index import UrlCirclez
from our_url.src.component_name_enum import ComponentName
from our_url.src.entity_name_enum import EntityName
from our_url.src.action_name_enum import ActionName
from entity_type.entity_enum import EntityEnum

BRAND_NAME = os.environ.get('BRAND_NAME')
ENVIRONMENT_NAME = os.environ.get('ENVIRONMENT_NAME')
UNKNOWN_LOCATION=0

PERSONAL_PROFILE_ENTITY_TYPE_ID = 6
REDDIT_DATA_SOURCE_ID = 20

object_to_insert = {
    'component_id': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'yoav.e@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

if BRAND_NAME != 'Circlez':
    logger.exception("please add BRAND_NAME to be Circlez to .env")
    raise

if ENVIRONMENT_NAME is None:
    logger.exception("please add ENVIRONMENT_NAME to .env")
    raise

class RedditImporter:
    def __init__(self):
        pass

    def process_reddit_user(self, reddit_user: dict)->dict:
        
        comments = reddit_user['comments']
        submissions = reddit_user['submissions']

        comments_processed = []
        submissions_processed = []
        
        for comment in comments.new(limit=None):
            comments_processed.append(comment.body)
        
        
        for submission in submissions.new(limit=None):
            submissions_processed.append(submission.title)
        
        reddit_user['comments'] = comments_processed
        reddit_user['submissions'] = submissions_processed

        return reddit_user

    def handle(self, event:dict=None)->None:
        """
        purpose:
            collect data on reddit users for a certain subreddit
        args:
            event: None for manual input(terminal),
            or a json formatted as such:
            {
                    "subreddit_name": "subreddit_name",
                    "user_count": "user_count"
            }

        example:
            main({"subreddit_name": "python", "user_count": 10})
            saves 10 users that commented on the python subreddit
            to the database

            main(None) asks for user input for subreddit name and user count
        """

        HANDLE_METHOD_NAME = "handle()"
        logger.start(HANDLE_METHOD_NAME, object={"event": event})

        # collect the subreddit name and user count
        reddit = Reddit()
        subreddit_name, user_count = reddit.get_subreddit_and_query(event)
        subreddit = reddit.reddit.subreddit(subreddit_name)

        ##########################################################################
        # Here we need to add the subreddit to the groups table in the database,
        # so we can later add the users to the users table with the group name
        # as a foreign key
        ##########################################################################

        reddit_users = reddit.get_users_from_subreddit(subreddit, user_count)


        ## add a new group with the name of the subreddit, if DNE

        # try to fetch the group by name from the DB
        # if DNE, create a new group with the name of the subreddit
        # and send a event to insert it, else, do nothing

        # group_id = get_group_by_name(subreddit_name) // pseudo code
        if reddit_users:
            for reddit_user in reddit_users:

                ##this step is getting the data ready for the generic insert
                processed_user = self.process_reddit_user(reddit_user)

                #this step is inserting the user to the database
                # this needs to return the profile_id for us to be able to use the importer
                profile_id = generic_profile_insert(profle_json=json.dumps(processed_user))

                ## insert to group profile the profile-id and the group-id
                # insert_to_group_profile(profile_id, group_id) // pseudo code

                ## register in importer
                logger
                importer.insert(#data_source_id = DataSourceEnum.Reddit.value,
                                data_source_id = REDDIT_DATA_SOURCE_ID,
                                location_id = UNKNOWN_LOCATION,
                                entity_type_id = EntityEnum.PersonalProfile.value,
                                entity_id = profile_id,
                                url = f"https://www.reddit.com/r/{subreddit_name}",
                                user_id = profile_id
                )

        else:
            logger.error("error no Reddit users found")

        logger.end(HANDLE_METHOD_NAME)