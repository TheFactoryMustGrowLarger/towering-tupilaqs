from dataclasses import dataclass


@dataclass
class Question:
    """Question Type struct"""

    id: int
    txt: str
    title: str
    expl: str
    difficulty: int
    ident: str
    votes: int


@dataclass
class Answer:
    """Answer Type struct"""

    id: int
    answer: str
    ident: str


@dataclass
class Combined:
    """**Summary**

    Combined Type struct
    For getting both question and answer from DB
    """

    id: int
    txt: str
    answer: str
    title: str
    expl: str
    difficulty: int
    votes: int
    ident: str


@dataclass
class User:
    """User Type struct"""

    id: int
    user_name: str
    correct_answers: str
    incorrect_answers: str
    ident: str


@dataclass
class UserCA:
    """User correct answers Type Struct"""

    correct_answers: str


@dataclass
class UserIA:
    """User incorrect answers Type Struct"""

    incorrect_answers: str
