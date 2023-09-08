from typing import List, TYPE_CHECKING


import pandas as pd

from ._tools import _get_headline_from_story
from ._urgency import Urgency

if TYPE_CHECKING:
    from pandas.core.tools.datetimes import DatetimeScalar


class NewsData(object):
    def __init__(
        self,
        title: str,
        creator: str,
        source: List[dict],
        language: List[dict],
        item_codes: List[str],
        urgency: int,
        creation_date: str,
        update_date: str,
        raw: dict,
        news_type: str,
        html: str = None,
        text: str = None,
    ) -> None:
        self.title = title
        self.creator = creator
        self.source = source
        self.language = language
        self.item_codes = item_codes
        self.urgency: Urgency = Urgency(urgency)

        if news_type == "story":
            from .story._data import NewsStoryContent

            self.content: NewsStoryContent = NewsStoryContent(html, text)
            self.headline: str = _get_headline_from_story(raw)
            self.creation_date: "DatetimeScalar" = pd.to_datetime(creation_date)
            self.update_date: "DatetimeScalar" = pd.to_datetime(update_date)

        elif news_type == "headline":
            self.first_created: "DatetimeScalar" = pd.to_datetime(creation_date)
            self.version_created: "DatetimeScalar" = pd.to_datetime(update_date)
            self.story_id: str = raw["storyId"]
