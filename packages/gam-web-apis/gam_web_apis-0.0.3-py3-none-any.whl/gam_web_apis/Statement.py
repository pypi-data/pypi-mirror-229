
from sys import maxsize
from typing import Union
from inspect import *


__iterables__ = (list, tuple, set, frozenset, filter, map, reversed)
__logicalOperators__ = ["AND", "OR"]  # conjunction, disjunction
__actions__ = ["IN", "IS", "LIKE", "<", "<=", ">", ">=", "=", "!="]


def linenoMsg(message):
    caller = getframeinfo(stack()[1][0])
    return "%d - %s" % (caller.lineno, message)


class Statement():
    def __init__(self, where: Union[dict, list, tuple, str], offset: int = 0, pageSize: int = 100, limit: int = maxsize, sortOrder: str = "name ASC"):
        """
        The `where` condition can be of types `<dict>`, `<list>`, `<tuple>` or `<str>`.
        - A condition of type `<dict>` must describe an operator suh as "AND"/"OR" which must contain a `<list>` or `<tuple>` of mutiple conditions. 
        - A condition of type `<list>` or `<tuple>` must follow the structure of [`<property`, `<operator>`, `<value(s)>`]. 
        - A condition of type `<str>` is an uncommon but valid feature. It can be used occasionally to match a name (as far i practically tested).

        Example Statement `where` clauses:
        ```py
        Statement(where: <tuple> = (<property>, "LIKE", "<wildcard%match>")
        Statement(where: <list> = [<property>, "IN", <list> | <tuple> | <set> | <frozenset> | <filter> | <map> | <reversed>)
        Statement(where: <str> = "{resource_name}")
        Statement(where: <dict> = { "AND": <list conditions> }
        Statement(where: <dict> = { "OR": <list conditions> }
        # Example <dict>
        Statement(where={ "AND": [
            ("status", "IN", ["INACTIVE", "ARCHIVED"]), # or "ACTIVE"
            "{resource_particular_name}",
            { "OR": [
                ("name", "LIKE", "resource_name_matches")
                { "AND": list(more_conditions) }
            ]}
        ]})
        ```
        """
        self.__validateStatement__(where)
        self.sortOrder = sortOrder if any(order in sortOrder for order in ("ASC", "DESC")) else "name ASC"
        self.limit = int(limit)
        self.offset = int(offset)
        self.setSize = min(self.limit, pageSize)
        self.conditionStatement = self.__createCondition__(where)

    def toStatement(self):
        return f"WHERE {self.conditionStatement} ORDER BY {self.sortOrder} LIMIT {self.setSize} OFFSET {self.offset}"

    def next(self, pageSetSize: int) -> bool:
        self.offset += self.setSize
        self.limit = min(self.limit, pageSetSize)
        self.setSize = min(self.setSize, self.limit - self.offset)
        return self.offset < self.limit

    def __createCondition__(self, condition):
        if type(condition) is dict:
            logicalOperator, nextConditions = tuple(condition.items())[0]
            return f"""({f" {logicalOperator} ".join(
                [self.__createCondition__(nextCondition)
                    for nextCondition in nextConditions]
            )})"""
        elif isinstance(condition, (list, tuple)):
            prop, action, value = tuple(condition)
            value = f"""({", ".join([repr(v) for v in value])})""" if action == "IN" else f"""'{value}'"""
            return f"""{prop} {action} {value}"""
        elif type(condition) is str:
            return condition

    def __validateStatement__(self, where):
        if not isinstance(where, (dict, list, tuple, str)):
            raise Exception('The type of the argument "where" of a statement must be a dict, list, tuple or str')
        elif len(errors := self.__validateCondition__(where, [])) > 0:
            raise Exception("\n\b".join(errors))

    def __validateCondition__(self, condition, errors: list):
        if type(condition) is dict:
            if len(items := tuple(condition.items())) != 1:
                errors.append(linenoMsg("""A condition of type dict can have 1 property"""))
            else:
                logicalOperator, nextConditions = items[0]
                if logicalOperator not in __logicalOperators__:
                    errors.append(linenoMsg(f"""The logicalOperator must be one of {__logicalOperators__}"""))
                elif not isinstance(nextConditions, (list, tuple)):
                    errors.append(linenoMsg(f"""The value from the logicalOperator "{logicalOperator}" must be a list"""))
                elif len(nextConditions) == 0:
                    errors.append(linenoMsg(f"""The length of the list from the logicalOperator "{logicalOperator}" must be greater than 0"""))
                else:
                    for nextCondition in nextConditions:
                        self.__validateCondition__(nextCondition, errors)
        elif isinstance(condition, (list, tuple)):
            if len(condition) != 3:
                errors.append(linenoMsg("""The length of a condition tuple must be equal to 3"""))
            else:
                prop, action, value = tuple(condition)
                if type(prop) is not str:
                    errors.append(linenoMsg("""The type of the property of a condition must be a str"""))
                if action not in __actions__:
                    errors.append(linenoMsg(f"""The action of a condition must be one of {__actions__}"""))
                if action == "IN":
                    if not isinstance(value, __iterables__):
                        errors.append(linenoMsg(f"""The value from the action "IN" of a condition must be a list"""))
                elif type(value) is not str:
                    errors.append(linenoMsg(f"""The value from the action "{action}" of a condition must be a str"""))
        elif type(condition) is str:
            if not (condition.startswith("{") and condition.endswith("}")):
                errors.append(linenoMsg("""In the rare case the condition is a string, the string is expected be wrapped in curly brackets: {condition}"""))
        else:
            errors.append(linenoMsg("""The type of a condition must be a dict or a str"""))
        return errors
