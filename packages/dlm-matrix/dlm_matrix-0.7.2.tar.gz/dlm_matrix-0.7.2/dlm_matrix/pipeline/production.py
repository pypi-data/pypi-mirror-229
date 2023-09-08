from typing import Any, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, root_validator, validator, PrivateAttr
from math import log2
from enum import Enum
import nltk
from collections import Counter


class UpdatePolicy(str, Enum):
    """Policy for updating word count and weight."""

    INCREMENT = "increment"
    OVERWRITE = "overwrite"


class ProductionWord(BaseModel):
    """Encapsulates a single significant word derived from the content."""

    word: str = Field(..., description="The production word itself.")
    count: int = Field(1, description="The frequency count of the word.")
    weight: Optional[float] = Field(
        1.0, description="A weight value assigned to the word."
    )
    tf_idf: Optional[float] = Field(None, description="The TF-IDF value of the word.")
    _parent: Optional[Any] = PrivateAttr(default=None)

    @validator("weight")
    def weight_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Weight must be a positive value.")
        return v

    @property
    def relative_frequency(self) -> Optional[float]:
        """Relative frequency of the word within its parent collection."""
        if self._parent:
            return self.count / self._parent.total_count
        else:
            return None

    @property
    def relative_weight(self) -> Optional[float]:
        """Relative weight of the word within its parent collection."""
        if self._parent:
            return self.weight / sum(
                word.weight for word in self._parent.words.values()
            )
        else:
            return None

    @property
    def relative_tf_idf(self) -> Optional[float]:
        """Relative TF-IDF of the word within its parent collection."""
        if self._parent:
            return self.tf_idf / sum(
                word.tf_idf for word in self._parent.words.values()
            )
        else:
            return None

    def __str__(self):
        return f"ProductionWord({self.word})"


class Ngrams(BaseModel):
    """Represents a collection of n-grams."""

    ngrams: Dict[Union[str, Tuple[str, ...]], int] = Field(
        ..., description="A dictionary of n-grams and their counts."
    )
    total_count: int = Field(
        ..., description="The total count of all n-grams in this collection."
    )

    @root_validator
    def check_ngram_consistency(cls, values):
        ngrams, total_count = values.get("ngrams"), values.get("total_count")
        if not isinstance(total_count, int) or total_count < 0:
            raise ValueError("Total count must be a positive integer")
        if total_count != sum(ngrams.values()):
            raise ValueError("Total count must equal the sum of the n-gram counts")
        return values

    def update_ngrams(
        self,
        ngram: Union[str, Tuple[str, ...]],
        count: int,
        update_policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Updates the n-gram collection with a new n-gram."""
        if ngram not in self.ngrams:
            self.ngrams[ngram] = count
        else:
            if update_policy == UpdatePolicy.INCREMENT:
                self.ngrams[ngram] += count
            elif update_policy == UpdatePolicy.OVERWRITE:
                self.ngrams[ngram] = count
        self.total_count += count


class ProductionWords(BaseModel):
    """Encapsulates a collection of significant words and n-grams derived from the content."""

    words: Dict[str, ProductionWord] = Field(
        {}, description="A dictionary of words and their associated ProductionWord."
    )
    unigrams: Dict[str, Ngrams] = Field(
        {}, description="A dictionary of unigrams and their associated Ngram."
    )
    bigrams: Dict[Tuple[str, str], Ngrams] = Field(
        {}, description="A dictionary of bigrams and their associated Ngram."
    )
    trigrams: Dict[Tuple[str, str, str], Ngrams] = Field(
        {}, description="A dictionary of trigrams and their associated Ngram."
    )
    total_count: int = Field(0, description="Total word and n-gram count")

    class Config:
        validate_assignment = True  # enables validation on assignment

    @root_validator
    def check_word_ngram_consistency(cls, values):
        words, unigrams, bigrams, trigrams, total_count = values.values()
        collections = [words, unigrams, bigrams, trigrams]
        if not isinstance(total_count, int) or total_count < 0:
            raise ValueError("Total count must be a positive integer")
        total_from_collections = sum(sum(c.values()) for c in collections)
        if total_count != total_from_collections:
            raise ValueError(
                "Total count must equal the sum of the word and n-gram counts"
            )
        return values

    def update_ngrams(
        self,
        ngrams: Ngrams,
        ngram: Union[str, Tuple[str, ...]],
        count: int,
        update_policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Updates the n-gram collection with a new n-gram."""
        ngrams.update_ngrams(ngram, count, update_policy)
        self.total_count += count

    def add_word(
        self,
        word: str,
        count: int = 1,
        weight: float = 1.0,
        policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Adds a word to the collection, updating count, weight, and TF-IDF."""
        if word not in self.words:
            self.words[word] = ProductionWord(word=word, _parent=self)
        if policy == UpdatePolicy.INCREMENT:
            self.words[word].count += count
            self.words[word].weight += weight
        elif policy == UpdatePolicy.OVERWRITE:
            self.words[word].count = count
            self.words[word].weight = weight
        else:
            raise ValueError(f"Invalid update policy: {policy}")
        self.total_count += count

    def add_words(
        self,
        words: List[str],
        count: int = 1,
        weight: float = 1.0,
        policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Adds a list of words to the collection, updating count, weight, and TF-IDF."""
        for word in words:
            self.add_word(word, count, weight, policy)

    def add_words_from_text(
        self,
        text: str,
        count: int = 1,
        weight: float = 1.0,
        policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Adds words from a string to the collection, updating count, weight, and TF-IDF."""
        self.add_words(text.split(), count, weight, policy)

    def update_ngrams(
        self,
        ngrams: Ngrams,
        ngram: Union[str, Tuple[str, ...]],
        count: int,
        update_policy: UpdatePolicy = UpdatePolicy.INCREMENT,
    ):
        """Updates the n-gram collection with a new n-gram."""
        ngrams.update_ngrams(ngram, count, update_policy)
        self.total_count += count

    @classmethod
    def from_text(cls, text: str):
        """Generates a ProductionWords object from a given text."""
        words = nltk.word_tokenize(text)
        unigrams = Counter(words)

        bigrams_list = list(nltk.bigrams(words))
        bigrams = Counter(bigrams_list)

        trigrams_list = list(nltk.trigrams(words))
        trigrams = Counter(trigrams_list)

        total_count = len(words) + len(bigrams_list) + len(trigrams_list)

        # Generating ProductionWord objects for each unigram
        words_objects = {
            word: ProductionWord(word=word, count=count)
            for word, count in unigrams.items()
        }

        # Generating Ngram objects for unigrams, bigrams, trigrams
        unigrams_objects = {
            unigram: Ngrams(ngrams={unigram: count}, total_count=count)
            for unigram, count in unigrams.items()
        }
        bigrams_objects = {
            bigram: Ngrams(ngrams={bigram: count}, total_count=count)
            for bigram, count in bigrams.items()
        }
        trigrams_objects = {
            trigram: Ngrams(ngrams={trigram: count}, total_count=count)
            for trigram, count in trigrams.items()
        }

        return cls(
            words=words_objects,
            unigrams=unigrams_objects,
            bigrams=bigrams_objects,
            trigrams=trigrams_objects,
            total_count=total_count,
        )

    def __str__(self):
        return f"ProductionWords({self.words})"
