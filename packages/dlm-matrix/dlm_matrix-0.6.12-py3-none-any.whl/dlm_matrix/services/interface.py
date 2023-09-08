from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Generic
from dlm_matrix.models import ChainTree, ChainMap
from pydantic import BaseModel, Field, PrivateAttr, create_model
from typing import Optional, Any, Dict, List, Type
from pydantic.generics import GenericModel, TypeVar

T = TypeVar("T")


# Define a base message processing class
class BaseMessageProcessing(ABC):
    @abstractmethod
    def __init__(self, message_data: List[ChainMap]):
        self.message_data = message_data

    @abstractmethod
    def filter_messages_by_condition(
        self, condition_func: Callable[[ChainMap], bool]
    ) -> List[ChainMap]:
        pass


class IMessageExtractor(BaseMessageProcessing):
    @abstractmethod
    def retrieve_all_conversation_messages(self) -> List[ChainMap]:
        pass


class IMessageSearcher(BaseMessageProcessing):
    @abstractmethod
    def find_messages_by_author(self, author: str) -> List[ChainMap]:
        pass

    @abstractmethod
    def find_similar(self, message_id: str, top_k: int = 5) -> List[ChainMap]:
        pass


class IMessageAnalyzer(BaseMessageProcessing):
    @abstractmethod
    def count_messages_by_author(self) -> Dict[str, int]:
        pass


class AbstractMessageFilter(ABC):
    @abstractmethod
    def filter(self, messages: List[ChainMap], *args, **kwargs) -> List[int]:
        pass
