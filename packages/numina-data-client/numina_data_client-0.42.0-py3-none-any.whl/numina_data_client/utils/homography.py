"""
This package stores homography anchor points in a dyanmoDB table.
The dynamo stable is structured with the feedId as the partition key and the
achor points as the sort key. The anchor points are a json object with the
following structure:
[
    {
        "x": 153,
        "y": 425,
        "lat": 40.6997465251,
        "lng": -73.9808547423
    },
    {
        "x": 271,
        "y": 234,
        "lat": 40.6997294065,
        "lng": -73.9806204452
    },
    {
        "x": 309,
        "y": 234,
        "lat": 40.6997115009,
        "lng": -73.9806167711
    },
    {
        "x": 435,
        "y": 442,
        "lat": 40.6996980311,
        "lng": -73.9808602689
    }
]
"""

import os
import json
from typing import List, Dict
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import boto3
from boto3.dynamodb.conditions import Attr, Key

# Define DynamoDB parameters
ACHOR_POINTS_TABLE = os.environ.get(
    "DYNAMO_HOMOGRAPHY_ANCHOR_POINTS_TABLE", "homography-anchor-points"
)


@dataclass_json
@dataclass
class AchorPoint:
    x: int
    y: int
    lat: float
    long: float


def store_achor_points(feedId: str, achor_points: List[AchorPoint]):
    """Store the homography anchor points in dyanmoDB.

    Args:
        AchorPoints: the feedId achor points
    """

    client = boto3.client("dynamodb")
    client.put_item(
        TableName=ACHOR_POINTS_TABLE,
        Item={
            "feedId": {"S": feedId},
            "anchorPoints": {
                "S": f"{AchorPoint.schema().dump(achor_points, many=True)}"
            },
        },
    )


def get_achor_points(feedId: str) -> List[AchorPoint]:
    """Retrive achor points from dyanmoDB for a given feedId.

    Args:
        feedId (str): the feedId from a sensor

    Returns:
        AchorPoints: the achor points
    """

    client = boto3.client("dynamodb")
    response = client.get_item(
        TableName=ACHOR_POINTS_TABLE, Key={"feedId": {"S": feedId}}
    )
    return AchorPoint.schema().loads(
        response["Item"]["anchorPoints"]["S"].replace("'", '"'), many=True
    )
