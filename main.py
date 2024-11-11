from gcloud.gcloud_functions.models.data_extractor import DataExtractor
from gcloud.gcloud_functions.shared.gcloud_integrator import GCloudIntegrator


def get_availability_data_decompress_and_upload_to_bucket():

    # Create GCloud Integrator Object
    GCloudIntegratorObject = GCloudIntegrator("elexon-project")

    # Crate Data Extractor Object
    DataExtractorObject = DataExtractor()

    # Get cloud key from Secrete Manager
    GCloudIntegratorObject.get_secret("elexon-project-service-account-secret")

    DataExtractorObject.download_files_from_availability_data("downloaded_files")
    final_files = DataExtractorObject.decompress_downloaded_data("downloaded_files", "decompressed_files")

    # loop through decompressed files and upload to GCStorage bucket
    for file in final_files:
        file_name = file.split("\\")[-1]  # extract decompressed file name
        print(file_name)
        # upload decompressed file to the GCStorage bucket
        GCloudIntegratorObject.upload_data_to_cloud_from_file(bucket_name="elexon-project-raw-data-bucket",
                                                        data_to_upload=file_name,
                                                        blob_name=file_name)


if __name__ == "__main__":
    get_availability_data_decompress_and_upload_to_bucket()
