import functions_framework
import json

from shared.gcloud_integrator import GCloudIntegrator
from models.data_extractor import DataExtractor
from shared.utils import DataConfigurator
from models.kafka import kafka


@functions_framework.http
def get_elexon_data_and_send_it_to_kafka(request, context=None):

    """
    Function to get data from Elexon API,
    send filenames to Kafka topic
    and download .gz data to Google Storage Bucket.

    Return empty list if no data is fetched
    or sending message to kafka failed.
    """

    # Create DataExtractor Object
    DataExtractorObject = DataExtractor()

    # Create GCloudIntegrator Object
    GCloudIntegratorObject = GCloudIntegrator("elexon-project")

    # Create timeframe object
    DataConfiguratorObject = DataConfigurator()

    # Get project secret
    GCloudIntegratorObject.get_secret("elexon-project-service-account-secret")

    # Get yesterday's date
    yesterday_date = DataConfiguratorObject.timeframe_window()

    availability_data = DataExtractorObject.get_availability_data(date=yesterday_date)

    if not availability_data:
        print("Issue with fetching elexon data. There is no data from given date.")
        return []

    else:
        # for file in get_availability_data upload file to bucket
        for file in availability_data:
            availability_data_file = DataExtractorObject.download_files_from_availability_data(filename=file)
            GCloudIntegratorObject.upload_data_to_cloud_from_string("elexon-project-data-bucket", availability_data_file, file)

        print("Data fetched successfully.")

        # try:
        #     # Save availability data filenames in bytes
        #     availability_data_filenames_in_bytes = json.dumps(list(availability_data.keys()), indent=2).encode('utf-8')

        #     # Send filenames to kafka
        #     kafka.main(f"{yesterday_date}_filenames", availability_data_filenames_in_bytes)
        #     return list(availability_data.keys())
        # except Exception as e:
        #     print(f"Issue with sending data to kafka {e}.")
        #     return []
