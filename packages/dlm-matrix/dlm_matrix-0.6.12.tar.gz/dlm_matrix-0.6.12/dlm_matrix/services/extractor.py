from typing import List, Callable, Optional, Tuple, Union, Dict
from dlm_matrix.services.filters import ChainFilter
from dlm_matrix.models import ChainTree, ChainMap
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from dlm_matrix.services.interface import IMessageExtractor
from sklearn.metrics.pairwise import cosine_similarity
import random
import numpy as np


class MessageExtractor(IMessageExtractor):
    def __init__(self, conversation_tree: ChainTree):
        super().__init__(conversation_tree)
        self.mapping = conversation_tree.mapping
        self._search_results = self.retrieve_all_conversation_messages()

    @property
    def search_results(self) -> List[ChainMap]:
        return self._search_results

    def filter_conversation_messages(
        self, conversation_filter: ChainFilter
    ) -> List[ChainMap]:
        all_messages = self.retrieve_all_conversation_messages()
        return [msg for msg in all_messages if conversation_filter.filter(msg.message)]

    def retrieve_all_conversation_messages(self) -> List[ChainMap]:
        return list(self.mapping.values())

    def find_message_by_id(self, message_id: str) -> Optional[ChainMap]:
        return self.mapping.get(message_id)

    def find_messages_by_role(self, role: str) -> List[ChainMap]:
        return [msg for msg in self._search_results if msg.message.author.role == role]

    def get_messages_by_role(self, role: str) -> List[str]:
        messages = self.find_messages_by_role(role)
        return [msg.message.content.text for msg in messages]

    def get_user_messages(self) -> List[str]:
        return self.get_messages_by_role("user")

    def get_assistant_messages(self) -> List[str]:
        return self.get_messages_by_role("assistant")

    def filter_messages_by_word_and_role(
        self, word: str, role: str = "user"
    ) -> List[str]:
        messages = self.get_messages_by_role(role)
        return [message for message in messages if word in message]

    def create_message_matrix(self, role: str = "user") -> csr_matrix:
        vectorizer = TfidfVectorizer()
        messages = self.get_messages_by_role(role)
        return vectorizer.fit_transform(messages)

    def get_message_similarity(
        self, message_matrix: csr_matrix, message: str
    ) -> Union[float, None]:
        vectorizer = TfidfVectorizer()
        message_vector = vectorizer.transform([message])
        similarity = cosine_similarity(message_vector, message_matrix)
        return similarity[0][0]

    def get_message_similarity_by_role(
        self, message: str, role: str = "user"
    ) -> Union[float, None]:
        message_matrix = self.create_message_matrix(role)
        return self.get_message_similarity(message_matrix, message)

    def filter_messages_by_condition(
        self, condition_func: Callable[[ChainMap], bool]
    ) -> List[ChainMap]:
        all_messages = self.retrieve_all_conversation_messages()
        return [msg for msg in all_messages if condition_func(msg)]

    def get_message_pairs(self) -> List[Tuple[str, str]]:
        user_messages = self.get_user_messages()
        assistant_messages = self.get_assistant_messages()
        return list(zip(user_messages, assistant_messages))

    def get_random_message_pairs(self) -> List[Tuple[str, str]]:
        return random.sample(self.get_message_pairs(), len(self.get_message_pairs()))

    def get_random_pair(self) -> Tuple[str, str]:
        return random.choice(self.get_random_message_pairs())

    def get_random_message_by_role(self, role: str) -> str:
        return random.choice(self.get_messages_by_role(role))

    def get_random_user_message(self) -> str:
        return self.get_random_message_by_role("user")

    def get_random_assistant_message(self) -> str:
        return self.get_random_message_by_role("assistant")

    def get_first_n_messages(
        self, n: int, role: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        if role == "both":
            pairs = self.get_message_pairs()
            return pairs[:n]
        elif role in ["user", "assistant"]:
            messages = self.get_messages_by_role(role)
            return messages[:n]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant', 'both'")

    def search_messages(
        self, keyword: str, role: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        if role == "both":
            pairs = self.get_message_pairs()
            return [pair for pair in pairs if keyword in pair[0] or keyword in pair[1]]
        elif role in ["user", "assistant"]:
            messages = self.get_messages_by_role(role)
            return [message for message in messages if keyword in message]
        else:
            raise ValueError

    def get_statistics(
        self, role: str = "both"
    ) -> Union[Dict[str, float], Dict[str, Dict[str, float]]]:
        stats = [
            "mean_length",
            "median_length",
            "std_dev_length",
            "max_length",
            "min_length",
        ]
        roles = ["user", "assistant"] if role == "both" else [role]
        result = {
            r: {
                s: getattr(np, s.split("_")[0])(
                    [len(m) for m in self.get_messages_by_role(r)]
                )
                for s in stats
            }
            for r in roles
        }
        return result if role == "both" else result[role]

    def get_extreme_length_message(
        self, role: str = "both", extreme: str = "max"
    ) -> Union[str, Dict[str, str]]:
        roles = ["user", "assistant"] if role == "both" else [role]
        extreme_func = max if extreme == "max" else min
        result = {r: extreme_func(self.get_messages_by_role(r), key=len) for r in roles}
        return result if role == "both" else result[role]

    # We can now use this function to create the get_longest and get_shortest methods
    def get_longest(self, role: str = "both") -> Union[str, Dict[str, str]]:
        return self.get_extreme_length_message(role, "max")

    def get_shortest(self, role: str = "both") -> Union[str, Dict[str, str]]:
        return self.get_extreme_length_message(role, "min")
