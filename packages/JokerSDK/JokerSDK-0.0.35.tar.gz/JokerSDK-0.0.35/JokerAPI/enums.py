__context__: tuple = (
    "API.INVALID",
    "API.VALID",
    "API.RESPONSE-ENUMS",
    "API.EXCEPTIONS"
)

from typing import Any
from strenum import StrEnum
from .exceptions import *

"""
Container class holding predefined error messages for the JokerAPI.co integration.

    Attributes:
    -----------
    REQUIRED_KEY : str
        Error message indicating that an API key must be set before attempting to dial or control call flow.

    INVALID_KEY : str
        Error message indicating that the provided API key is incorrect, resulting in inability to dial or control call flow.
    
    INVALID_COUNTRY : str
        Error message indicating that the provided numbers may not be called to.
    
    INVALID_PARAM: str
        Error message indicating that the key word arguments aren't properly polluted.
"""
class ExceptionMsg:
    REQUIRED_KEY = "Please set an API key before processing to dial or control the flow of a call."
    INVALID_KEY = "The API key provided is invalid."
    INVALID_COUNTRY = "The numbers 'to' or 'from' are not white listed."
    INVALID_PARAM = "Please pollute the key word arguments correctly."

"""
Enum-like class `API` for building endpoint URLs and translating API actions into URLs for JokerAPI.co integration.

    Attributes:
    -----------
    URL : str
        The base URL template for constructing API endpoint URLs.

    Methods:
    --------
    __translator__(val: str, url: str, vars: dict) -> str:
        Translates the API action name into the corresponding endpoint URL with the provided variables.

    Parameters:
    -----------
    val : str
        The API action name, e.g., "DIAL", "PLAY", "TRANSFER", etc.

    url : str
        The base URL template.

    vars : dict
        A dictionary containing variables required for constructing the specific endpoint URL.

    Returns:
    --------
    str
        The translated endpoint URL for the given API action and variables.
"""

class API(StrEnum):
    URL = "https://api.jokerapi.co/voice/v1/{}?{}"

    """
    Translates API action name into the corresponding endpoint URL.
        
        Parameters:
        -----------
        val : str
            The API action name, e.g., "DIAL", "PLAY", "TRANSFER", etc.
        
        url : str
            The base URL template.
        
        vars : dict
            A dictionary containing variables required for constructing the specific endpoint URL.
        
        Returns:
        --------
        str
            The translated endpoint URL for the given API action and variables.
    """
    def __translator__(
            val: str, 
            url, 
            vars
            ) -> str:
        return {
            "DIAL": url.format("dial", f"apikey={vars['key']}&to={vars['to']}&from={vars['from']}&webhookurl={vars['url']}"),
            "PLAY": url.format("play", f""),
            "PLAYTEXT": url.format("playtext", f""),
            "gAUDIO": url.format("gather", f""),
            "gText": url.format("gathertext", f""),
            "TRANSFER": url.format("transfer", f""),
            "HANGUP": url.format("hangup", f"")
        }[val]


class Joker(StrEnum):
    """
    An enumeration of responses registered and received from JokerAPI, utilized within the library to manage diverse responses.
        Attributes:
        -----------
        __unknown__ : list
            A list to collect unrecognized responses.

        SUCCESS : str
            A response indicating that the operation was successful.

        INVALIDAUTH : str
            A response indicating an invalid API key, often leading to authorization failure.

        INVALIDPARAM : str
            A response indicating missing parameters in the request, leading to unsuccessful processing.

        SERVERFAILURE : str
            A response indicating a connection failure with the server.

        NO_BALANCE : str
            A response indicating insufficient balance for the requested action.

        INVALIDCOUNTRY : str
            A response indicating that the requested country is not whitelisted for the operation.

        GATHER_AUDIO : str
            A response indicating the playing of audio during the gathering phase.

        GATHER_TEXT : str
            A response indicating the playing of text during the gathering phase.

        CALL_ENDED : str
            A response indicating the termination of a call.

        PLAY_AUDIO : str
            A response indicating the playing of audio.

        PLAY_TEXT : str
            A response indicating the playing of text.

        TRANSFERING : str
            A response indicating the ongoing process of call transfer.

        Methods:
        --------
        __INVALID__(value: str) -> int
            Register an unrecognized response and return its index in the '__unknown__' list.

    """
    __unknown__ = []
    
    SUCCESS = "success"
    INVALIDAUTH = "invalid api key"
    INVALIDPARAM = "you are missing parameters"
    SERVERFAILURE = "Connection failed"
    NO_BALANCE = "you have no balance"
    INVALIDCOUNTRY = "this country is not whitelisted"
    
    GATHER_AUDIO = "playing audio while gathering"
    GATHER_TEXT = "playing text while gathering"

    CALL_ENDED = "call ended"

    PLAY_AUDIO = "playing audio"
    
    PLAY_TEXT = "playing text"
    
    TRANSFERING = "transfering call"

    """
        Register an unrecognized response and return its index in the '__unknown__' list.

        Parameters:
        -----------
        value : str
            The unrecognized response to register.

        Returns:
        --------
        int
            The index of the registered unrecognized response in the '__unknown__' list.
    """
    def __INVALID__(
            value: str
            ) -> int:
        return (_ := Joker.__unknown__.append([value])), len(Joker.__unknown__)[-1]


translator = {
    Joker.INVALIDAUTH:    [ INVALIDAPIKEY, ExceptionMsg.INVALID_KEY ],
    Joker.INVALIDCOUNTRY: [ INVALIDCOUNTRY, ExceptionMsg.INVALID_COUNTRY ],
    Joker.INVALIDPARAM:   [ INVALIDPARAM, ExceptionMsg.INVALID_PARAM ]
}