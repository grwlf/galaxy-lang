# coding: utf-8

"""
    ICFP Contest 2020 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class TeamForProblemsScoreboardDto(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'team': 'TeamDto',
        'score': 'int',
        'solved_at': 'datetime',
        'problems': 'dict(str, ProblemDto)'
    }

    attribute_map = {
        'team': 'team',
        'score': 'score',
        'solved_at': 'solvedAt',
        'problems': 'problems'
    }

    def __init__(self, team=None, score=None, solved_at=None, problems=None, local_vars_configuration=None):  # noqa: E501
        """TeamForProblemsScoreboardDto - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._team = None
        self._score = None
        self._solved_at = None
        self._problems = None
        self.discriminator = None

        if team is not None:
            self.team = team
        if score is not None:
            self.score = score
        if solved_at is not None:
            self.solved_at = solved_at
        self.problems = problems

    @property
    def team(self):
        """Gets the team of this TeamForProblemsScoreboardDto.  # noqa: E501


        :return: The team of this TeamForProblemsScoreboardDto.  # noqa: E501
        :rtype: TeamDto
        """
        return self._team

    @team.setter
    def team(self, team):
        """Sets the team of this TeamForProblemsScoreboardDto.


        :param team: The team of this TeamForProblemsScoreboardDto.  # noqa: E501
        :type: TeamDto
        """

        self._team = team

    @property
    def score(self):
        """Gets the score of this TeamForProblemsScoreboardDto.  # noqa: E501


        :return: The score of this TeamForProblemsScoreboardDto.  # noqa: E501
        :rtype: int
        """
        return self._score

    @score.setter
    def score(self, score):
        """Sets the score of this TeamForProblemsScoreboardDto.


        :param score: The score of this TeamForProblemsScoreboardDto.  # noqa: E501
        :type: int
        """

        self._score = score

    @property
    def solved_at(self):
        """Gets the solved_at of this TeamForProblemsScoreboardDto.  # noqa: E501


        :return: The solved_at of this TeamForProblemsScoreboardDto.  # noqa: E501
        :rtype: datetime
        """
        return self._solved_at

    @solved_at.setter
    def solved_at(self, solved_at):
        """Sets the solved_at of this TeamForProblemsScoreboardDto.


        :param solved_at: The solved_at of this TeamForProblemsScoreboardDto.  # noqa: E501
        :type: datetime
        """

        self._solved_at = solved_at

    @property
    def problems(self):
        """Gets the problems of this TeamForProblemsScoreboardDto.  # noqa: E501


        :return: The problems of this TeamForProblemsScoreboardDto.  # noqa: E501
        :rtype: dict(str, ProblemDto)
        """
        return self._problems

    @problems.setter
    def problems(self, problems):
        """Sets the problems of this TeamForProblemsScoreboardDto.


        :param problems: The problems of this TeamForProblemsScoreboardDto.  # noqa: E501
        :type: dict(str, ProblemDto)
        """

        self._problems = problems

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TeamForProblemsScoreboardDto):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TeamForProblemsScoreboardDto):
            return True

        return self.to_dict() != other.to_dict()
