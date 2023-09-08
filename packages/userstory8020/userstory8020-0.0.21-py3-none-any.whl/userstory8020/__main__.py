if __package__:
    from .app import DataFrameManipulation, file_validation, open_spark_session
else:
    from app import DataFrameManipulation, open_spark_session, file_validation

import argparse


class main():
    def run_app(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("spark_remote_url")
        parser.add_argument("clients_dataset_path")
        parser.add_argument("finDetails_dataset_path")
        parser.add_argument("countries")
        args = parser.parse_args()
        if not file_validation(filePath=args.clients_dataset_path):
            pass
        if not file_validation(filePath=args.finDetails_dataset_path):
            pass

        with open_spark_session(spark_remote_url=args.spark_remote_url) as spark:
            dfm = DataFrameManipulation()
            dfm.clients = spark.read.csv(args.clients_dataset_path,
                                         sep=',',
                                         header=True)
            dfm.finDetails = spark.read.csv(args.finDetails_dataset_path,
                                            sep=',',
                                            header=True)
            dfm.clients.show()
            dfm.finDetails.show()
            dfm.filter_rows(filterConditions={"country": ["United Kingdom",
                                                        "Netherlands"]})
            dfm.select_columns(colsList=['email', 'country'],
                               colsMap={"btc_a": "bitcoin_address",
                                        "id": "client_identifier",
                                        "cc_t": "credit_card_type"})
            dfm.clients.show()
            dfm.save_output(outputPath="client_data")


if __name__ == "__main__":
    main().run_app()
