from IPython import display
from ensure import ensure_annotations
import urllib.request
from PYRJrenderer.custom_exception import InvalidURLException
from PYRJrenderer.logger import logger

""" 
    this method is used to check the url is valid or not if validation fails return false
    or url is valid return true 
    here getcode is used to get the code as response_status is getcode==200 then log else raise asseret error.
    and raise exception
"""


@ensure_annotations
def is_valid(URL: str) -> bool:
    try:
        response_status = urllib.request.urlopen(URL).getcode()
        assert response_status == 200
        logger.debug(f"response_status: {response_status}")
        return True
    except Exception as e:
        logger.exception(e)
        return False


"""
    this method is a main method to render the response site 
    and also use the is_valid method to check if the url is valid or not.
    if the url is valid then display using IFrame and return success 
    else rise an invalid response url eception.
"""


@ensure_annotations
def render_site(URL: str, width: str = "100%", height: str = "600") -> str:
    try:
        if is_valid(URL):
            response = display.IFrame(src=URL, width=width, height=height)
            display.display(response)
            return "success"
        else:
            raise InvalidURLException
    except Exception as e:
        raise e
