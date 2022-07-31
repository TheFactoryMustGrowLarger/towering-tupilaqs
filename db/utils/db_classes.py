from dataclasses import dataclass


@dataclass
class QuestionPull:
    """Question Type struct"""

    id: int
    txt: str
    title: str
    expl: str
    difficulty: int
    ident: str
    votes: int


@dataclass
class QuestionInsert:
    """Question Type struct"""

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


class UserList:
    """Base class for the different lists that the User table contains"""

    def as_list(self, property_name):
        """Helper function to split the given property to a list of strings

        assumes seperation by ', ' and excludes empty items
        """
        value = getattr(self, property_name, None)
        if value is None:
            return list()

        sp = value.split(', ')
        empty_removed = filter(lambda x: x != '', sp)
        return list(empty_removed)


@dataclass
class User(UserList):
    """User Type struct"""

    id: int
    user_name: str
    password: str
    correct_answers: str
    incorrect_answers: str
    submitted_questions: str
    submitted_add_votes: str
    ident: str


@dataclass
class UserCA(UserList):
    """User correct answers Type Struct"""

    correct_answers: str


@dataclass
class UserIA(UserList):
    """User incorrect answers Type Struct"""

    incorrect_answers: str


@dataclass
class UserSQ(UserList):
    """User incorrect answers Type Struct"""

    submitted_questions: str


@dataclass
class UserSV(UserList):
    """User submitted add votes Type Struct"""

    submitted_add_votes: str
