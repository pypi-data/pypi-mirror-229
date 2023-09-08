#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List

import awswrangler as wr
import pandas as pd

from .. import constants

###############################################################################
DATA_VERSION_v20220720 = "v20220720"
DATA_VERSION_v20230601 = "v20230601"

ATHENA_DATABASE = "numina_data_lake_{data_version}_prod"
ATHENA_WORKGROUP = "data-science"


def query_athena(
    query: str,
    database: str = ATHENA_DATABASE.format(data_version=DATA_VERSION_v20230601),
    workgroup: str = ATHENA_WORKGROUP,
):
    return wr.athena.read_sql_query(sql=query, database=database, workgroup=workgroup)


def query_tracks(
    feed_id: str,
    start_datetime: datetime,
    end_datetime: datetime,
    obj_classes: List[str] = constants.ALL_OBJECT_CLASSES,
    query_raw_tracks=True,
    data_version: str = DATA_VERSION_v20230601,
) -> pd.DataFrame:
    """
    Query for all tracks from a single feed and between two datetimes.

    Parameters
    ----------
    feed_id: str
        The feed id to query for. This is specifically tied to a device.
    start_datetime: datetime
        The datetime to query from.
    end_datetime: datetime
        The datetime to query to.
    obj_classes: List[str]
        Which objects to retrieve track data for.
        Default: All numina standard objects.
    query_raw_tracks: bool
        Set to True to query raw tracks (pre-track connections), or False to query clean tracks
        Default: True (query raw tracks) # TODO change defaults once it's stable

    Returns
    -------
    tracks: pd.DataFrame
        The selected tracks for that feed between the provided datetimes.
    """
    # Convert obj class to tuple for string addition
    # If there is only one object class selected, the query will fail due
    # to text formatting of tuples (the trailing comma)
    if len(obj_classes) == 1:
        obj_classes = f"('{obj_classes[0]}')"
    else:
        obj_classes = tuple(obj_classes)

    track_db_name = "clean_tracks"
    if query_raw_tracks:
        track_db_name = "raw_tracks"

    athena_db = ATHENA_DATABASE.format(data_version=data_version)

    # Create basic query
    QUERY = f"""
    SELECT * FROM "{athena_db}"."{track_db_name}"
    WHERE feedid = '{feed_id}'
    AND class in {obj_classes}
    """

    # Add between datetimes
    if start_datetime is not None and end_datetime is not None:
        # Create iso_start_datetime and iso_end_datetime for ATHENA TIMESTAMP casts
        iso_start_datetime = start_datetime.isoformat(" ")
        iso_end_datetime = end_datetime.isoformat(" ")

        # Append to query
        QUERY += f"""
        AND (time
            BETWEEN CAST('{iso_start_datetime}' AS TIMESTAMP)
            AND CAST('{iso_end_datetime}' AS TIMESTAMP)
        )
        """

    # Finish the SQL formatting
    QUERY += ";"

    # Fetch and return
    return query_athena(QUERY, athena_db)


def query_dwell_tracks(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x3: int,
    y3: int,
    x4: int,
    y4: int,
    x5: int,
    y5: int,
    x6: int,
    y6: int,
    x7: int,
    y7: int,
    x8: int,
    y8: int,
    feed_id: str,
    start_datetime: datetime,
    end_datetime: datetime,
    obj_classes: List[str] = constants.ALL_OBJECT_CLASSES,
    use_clean_tracks_db=False,
    data_version: str = DATA_VERSION_v20230601,
) -> pd.DataFrame:
    """
    Query for all tracks from a single feed and between two datetimes.

    Parameters
    ----------
    feed_id: str
        The feed id to query for. This is specifically tied to a device.
    start_datetime: datetime
        The datetime to query from.
    end_datetime: datetime
        The datetime to query to.
    obj_classes: List[str]
        Which objects to retrieve track data for.
        Default: All numina standard objects.

    Returns
    -------
    tracks: pd.DataFrame
        The selected tracks for that feed between the provided datetimes.
    """
    # Convert obj class to tuple for string addition
    # If there is only one object class selected, the query will fail due
    # to text formatting of tuples (the trailing comma)
    if len(obj_classes) == 1:
        obj_classes = f"('{obj_classes[0]}')"
    else:
        obj_classes = tuple(obj_classes)

    iso_start_datetime = start_datetime.isoformat(" ")
    iso_end_datetime = end_datetime.isoformat(" ")

    athena_db = ATHENA_DATABASE.format(data_version=data_version)
    track_db_name = "raw_tracks"
    if use_clean_tracks_db:
        track_db_name = "clean_tracks"

    # Create basic query
    QUERY = f"""
    -- Query Raw or Clean Tracks
    WITH {track_db_name} as (
            SELECT 
            trackid, 
            time, 
            class, 
            bottom_center,
            bottom_center[1] as sx,
            bottom_center[2] as sy
        FROM "{athena_db}"."{track_db_name}"
        WHERE feedid = '{feed_id}'
            AND (time
                    BETWEEN CAST('{iso_start_datetime}' AS TIMESTAMP)
                    AND CAST('{iso_end_datetime}' AS TIMESTAMP)
                ) -- Filter by time
            AND class IN ({", ".join( [ f"'{i}'" for i in obj_classes] )}) -- Filter by object class
            AND ST_WITHIN( ST_POINT(bottom_center[1],bottom_center[2]), ST_GeometryFromText('POLYGON(({x1} {y1}, {x2} {y2}, {x3} {y3}, {x4} {y4}, {x5} {y5}, {x6} {y6}, {x7} {y7}, {x8} {y8}, {x1} {y1}))'))
        ORDER BY trackid, time
    ),
    -- Convert to segments
    segments AS (
            -- Calculate rolling average to normalize jitter.
            SELECT 
                trackid,class,
                sx,sy,ex,ey,vx,vy,
                -- Rolling average of vx and vy
                ABS(AVG(vx) OVER (PARTITION BY trackid ORDER BY time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)) AS fx,
                ABS(AVG(vy) OVER (PARTITION BY trackid ORDER BY time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)) AS fy,
                dt_seconds,time,etime
            FROM(
            -- Calculate Vectors
            SELECT 
                trackid,
                class,
                sx,sy,
                ex,ey,
                (ex-sx) AS vx,
                (ey-sy) AS vy,
                date_diff('millisecond', time, etime) as dt_seconds,
                time, etime
            FROM (
                    -- Get Segments info by shifting with partitions. 
                    -- Last row of the partitions gets a null value assigned
                    SELECT 
                        trackid,
                        sx,sy,
                        time,
                        lead(sx, 1) over (partition by trackid order by time) AS ex,
                        lead(sy, 1) over (partition by trackid order by time) AS ey,
                        lead(time, 1) over (partition by trackid order by time) AS etime,
                        class
                    FROM {track_db_name}
                    ORDER BY trackid,time
                )
            -- Remove last row of each trackid. This gets rolled out by the lead function.
            -- this might not be very necessary
            WHERE ex IS NOT NULL
            ORDER BY trackid, time
        )
    ), dwell_segments AS (
        SELECT 
            trackid, time, class, sx, sy, vx, vy, fx, fy, dt_seconds as dt_ms
        FROM segments
        WHERE fx <= 1 AND fy <= 1 -- Filter by Dampened vector amplitude
    ), dwell_tracks AS (
        -- Groupby trackid and sum dt_ms and average sx and sy is sql
        SELECT trackid, min(time) as min_time, class,SUM(dt_ms) as dt_ms, AVG(sx) as sx, AVG(sy) as sy FROM dwell_segments GROUP BY trackid, class
    )

    SELECT * 
    FROM dwell_tracks
    WHERE dt_ms >= 5000;
    """

    # Fetch and return
    return query_athena(QUERY, athena_db)


def query_screenline_tracks(
    sample_count: int,
    feed_id: str,
    iso_start_datetime: str,
    iso_end_datetime: str,
    obj_classes: List[str] = constants.ALL_OBJECT_CLASSES,
    x1: int = 0,
    y1: int = 0,
    x2: int = 0,
    y2: int = 0,
    use_clean_tracks_db=False,
    data_version: str = DATA_VERSION_v20230601,
) -> pd.DataFrame:
    """
    Query for all tracks from a single feed between two datetimes that cross a screenline.
    """
    athena_db = ATHENA_DATABASE.format(data_version=data_version)
    track_db_name = "raw_tracks"
    if use_clean_tracks_db:
        track_db_name = "clean_tracks"

    QUERY = f"""
    -- Query Raw Tracks
    WITH {track_db_name} as (
            SELECT * FROM (
                SELECT 
                    trackid,
                    class,
                    time,
                    sx,sy,
                    lead(sx, 1) over (partition by trackid order by time) AS ex,
                    lead(sy, 1) over (partition by trackid order by time) AS ey 
                FROM(
                    SELECT 
                        trackid, 
                        time, 
                        class, 
                        -- bottom_center,
                        bottom_center[1] as sx,
                        bottom_center[2] as sy
                    FROM "{athena_db}"."{track_db_name}"
                    WHERE feedid = '{feed_id}'
                        AND (time
                                BETWEEN CAST('{iso_start_datetime}' AS TIMESTAMP)
                                AND CAST('{iso_end_datetime}' AS TIMESTAMP)
                            ) -- Filter by time
                        AND class IN ({", ".join( [ f"'{i}'" for i in obj_classes] )}) -- Filter by object class
                    ORDER BY trackid, time
                )
            ) WHERE ex IS NOT NULL

    ),
    -- Get trackids intersecting with the screenline
    long_trackids AS (
            -- Count unique trackids
            SELECT 
                trackid
            FROM (
                SELECT * 
                FROM {track_db_name}
                WHERE ST_INTERSECTS( 
                    ST_LineFromText( CONCAT('linestring(',cast(sx as varchar),' ', cast(sy as varchar),',', cast(ex as varchar) ,' ', cast(ey as varchar),')') ),
                    ST_LineFromText( CONCAT('linestring(',cast({x1} as varchar),' ', cast({y1} as varchar),',', cast({x2} as varchar) ,' ', cast({y2} as varchar),')') ) 
                )
            )
        ORDER BY RANDOM()
        LIMIT {sample_count}
    ),
    -- Use long tracks ids to get tracks with more than 1 points
    sample_tracks AS (
        SELECT *
        FROM {track_db_name}
        WHERE trackid IN (SELECT trackid FROM long_trackids)
    )
    
    SELECT 
        trackid,
        time,
        class,
        sx,sy,ex,ey
    FROM sample_tracks
    """
    # Fetch and return
    return query_athena(QUERY, athena_db)


def query_matrices(
    feed_id: str,
    start_datetime: datetime,
    end_datetime: datetime,
    obj_classes: List[str] = constants.ALL_OBJECT_CLASSES,
    data_version: str = DATA_VERSION_v20230601,
) -> pd.DataFrame:
    """
    Query for all tracks matrices from a single feed and between two datetimes.

    Parameters
    ----------
    feed_id: str
        The feed id to query for. This is specifically tied to a device.
    start_datetime: datetime
        The datetime to query from.
    end_datetime: datetime
        The datetime to query to.
    obj_classes: List[str]
        Which objects to retrieve track data for.
        Default: All numina standard objects.

    Returns
    -------
    tracks: pd.DataFrame
        The selected track matrices for that feed between the provided datetimes.
    """
    # Convert obj class to tuple for string addition
    # If there is only one object class selected, the query will fail due
    # to text formatting of tuples (the trailing comma)
    if len(obj_classes) == 1:
        obj_classes = f"('{obj_classes[0]}')"
    else:
        obj_classes = tuple(obj_classes)

    athena_db = ATHENA_DATABASE.format(data_version=data_version)

    # Create basic query
    QUERY = f"""
    SELECT * FROM "{athena_db}"."track_matrices"
    WHERE feedid = '{feed_id}'
    AND class in {obj_classes}
    """

    # Add between datetimes
    if start_datetime is not None and end_datetime is not None:
        # Create iso_start_datetime and iso_end_datetime for ATHENA TIMESTAMP casts
        iso_start_datetime = start_datetime.isoformat(" ")
        iso_end_datetime = end_datetime.isoformat(" ")

        # Append to query
        QUERY += f"""
        AND (track_date
            BETWEEN CAST('{iso_start_datetime}' AS TIMESTAMP)
            AND CAST('{iso_end_datetime}' AS TIMESTAMP)
        )
        """

    # Finish the SQL formatting
    QUERY += ";"
    return query_athena(QUERY, athena_db)
