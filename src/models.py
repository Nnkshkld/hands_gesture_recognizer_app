from enum import Enum


class GestureSet(str, Enum):
    # Single hand
    LIKE = "is_like"
    DISLIKE = "is_dislike"
    STOP = "is_stop"
    OKAY = "is_okay"

    # Two hands
    TWO_LIKES = "is_two_likes"
    TWO_DISLIKES = "is_two_dislike"
    TWO_STOPS = "is_two_stops"
    TWO_OKAY = "is_two_okay"
