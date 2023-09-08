from contextlib import contextmanager
from csv import Error, Sniffer
from os import R_OK, access
from pathlib import Path
from typing import Dict, List, Optional, Union

from pyspark.sql import SparkSession
from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.functions import col


@contextmanager
def open_spark_session(spark_remote_url: str):
    spark_session = SparkSession.builder \
                               .remote(spark_remote_url) \
                               .getOrCreate()
    try:
        yield spark_session
    finally:
        spark_session.stop()


class AppMain():
    def __init__(self, spark_remote_url) -> None:
        self.__spark_session: SparkSession
        self.__spark_remote_url = spark_remote_url

    def __enter__(self) -> SparkSession:
        self.__spark_session = SparkSession.builder \
                               .remote(self.__spark_remote_url) \
                               .getOrCreate()
        return self.__spark_session

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.__spark_session.stop()


class DataFrameManipulation:
    def __init__(self) -> None:
        self.__clients: DataFrame
        self.__finDetails: DataFrame

    @property
    def clients(self) -> DataFrame:
        return self.__clients

    @clients.setter
    def clients(self, df: DataFrame) -> None:
        if isinstance(df, DataFrame):
            self.__clients = df

    @property
    def finDetails(self):
        return self.__finDetails

    @finDetails.setter
    def finDetails(self, df: DataFrame) -> None:
        if isinstance(df, DataFrame):
            self.__finDetails = df

    def filter_rows(self,
                    filterConditions: Dict[str,
                                           Union[str,
                                                 List[str]]]) -> None:
        for col_name, col_value in filterConditions.items():
            self.clients = self.clients \
                               .filter(self.clients[col_name].isin(col_value))

    def select_columns(self,
                       colsList: List[str],
                       colsMap: Optional[Dict[str, str]] = None) -> None:
        self.clients = self.clients.join(self.finDetails, ["id"])
        if colsMap:
            self.rename_columns(colsMap=colsMap)
            colsList.extend(colsMap.values())
        self.clients = self.clients.select([c for c in self.clients.columns if c in colsList])

    def rename_columns(self,
                       colsMap: Dict[str, str]) -> None:
        self.clients = self.clients.select([col(c).alias(colsMap.get(c, c)) for c in self.clients.columns])

    def save_output(self, outputPath: str):
        self.clients.write \
                    .mode("overwrite") \
                    .option("header", True) \
                    .csv(outputPath)


def file_validation(filePath: str) -> bool:
    __return_value: bool = False
    p = Path(filePath)
    if p.exists() and p.is_file():
        if access(filePath, R_OK):
            try:
                with open(filePath, newline='') as csvfile:
                    start = csvfile.read(1024)
                    Sniffer().sniff(start)
                    if Sniffer().has_header(start):
                        __return_value = True
            except Error as e:
                pass
    return __return_value
