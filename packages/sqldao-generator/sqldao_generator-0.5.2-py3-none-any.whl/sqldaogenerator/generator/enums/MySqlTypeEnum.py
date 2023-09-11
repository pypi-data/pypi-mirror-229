from enum import Enum


# from sqlalchemy import BigInteger, VARCHAR, CHAR, Text, SmallInteger, Integer, Double, DateTime


class MySqlTypeEnum(Enum):
    bigint = "BigInteger"
    varchar = "VARCHAR"
    char = "CHAR"
    text = "Text"
    tinyint = "SmallInteger"
    int = "Integer"
    double = "Double"
    datetime = "DateTime"
