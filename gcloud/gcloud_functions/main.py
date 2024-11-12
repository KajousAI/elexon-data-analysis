import functions_framework
import json
import os
from shared.gcloud_integrator import GCloudIntegrator
from models.data_extractor import DataExtractor
from shared.utils import DataConfigurator
# from models.kafka import kafka


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

    # Create timeframe object
    DataConfiguratorObject = DataConfigurator()


    # Create GCloudIntegrator Object
    GCloudIntegratorObject = GCloudIntegrator(
        project_id="elexon-data-project",
        data_configurator=DataConfiguratorObject
    )


    list_of_files = DataExtractorObject.get_list_of_files_to_download()

    if not list_of_files:
        return "Issue with fetching elexon data. There is no data from given date."

    else:
        # for file in get_availability_data upload file to bucket
        for file_name in list_of_files:
            try:
                filename_endpoint = DataExtractorObject.get_filename_endpoint(filename=file_name)
                GCloudIntegratorObject.download_file_to_gcs(
                    bucket_name="elexon-project-data-bucket", 
                    blob_name='elexon-data', 
                    filename_endpoint=filename_endpoint
                )
            except Exception as e:
                continue
    
        return "Data fetched successfully."

        # try:
        #     # Save availability data filenames in bytes
        #     availability_data_filenames_in_bytes = json.dumps(list(availability_data.keys()), indent=2).encode('utf-8')

        #     # Send filenames to kafka
        #     kafka.main(f"{yesterday_date}_filenames", availability_data_filenames_in_bytes)
        #     return list(availability_data.keys())
        # except Exception as e:
        #     print(f"Issue with sending data to kafka {e}.")
        #     return []
