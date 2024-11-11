from google.cloud import secretmanager_v1
from google.cloud import storage
import json


class GCloudIntegrator:

    def __init__(self, project_id) -> None:
        self.cloud_key = None
        self.project_id = project_id

    def get_secret(self, secret_id, version_id="latest"):
        """
        Return a secret value from gcloud secret manager instance.
        """
        try:
            # Create Secret Manager Client
            client = secretmanager_v1.SecretManagerServiceClient()
            # Build secret name
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            # Get a response
            response = client.access_secret_version(request={"name": name})
            # Assing secret value to self.cloud_key
            self.cloud_key = json.loads(response.payload.data.decode("UTF-8"))
            
            return self.cloud_key
        except Exception as e:
            print(f"Error with getting secret {e}.")
            return None

    def _get_google_cloud_client(self):
        """
        Return a client to manage google cloud service from provided cloud key
        """
        # Try to create Storage Client
        try:
            # return storage.Client.from_service_account_info(self.cloud_key)  # return Google Cloud Storage Client
            return storage.Client()  # return Google Cloud Storage Client
        except Exception:
            return None  # if there is no cloud key provided

    def upload_data_to_cloud_from_file(self, bucket_name, data_to_upload, blob_name):
        ''' Uploads files with api data to GCP buckets. '''
        try:
            bucket = self._get_google_cloud_client().bucket(bucket_name)  # connect to bucket
            blob = bucket.blob(blob_name)  # create a blob
            with open(data_to_upload, "rb") as file:
                blob.upload_from_file(file)  # upload data to blob
        except Exception as e:
            print(f"Error when uploading data to cloud from file: {e}.")
            return None

    def upload_data_to_cloud_from_string(self, bucket_name, data_to_upload, blob_name):

        '''
        Uploads files with api data to GCP buckets.
        Returns None if error is encountered.
        '''

        try:
            bucket = self._get_google_cloud_client().bucket(bucket_name)  # connect to bucket
            blob = bucket.blob(blob_name)  # create a blob
            blob.upload_from_string(data_to_upload)  # send data to bucket

            print("File successfully uploaded to bucket")
        except Exception as e:
            print(f"Error when uploading data from string: {e}.")
            return None

# "591906381433"
# "elexon-project-service-account-secret"

# x = GCloudIntegrator("elexon-project")
# x.get_secret("elexon-project-service-account-secret")
# x.upload_data_to_cloud_from_file("elexon-project-raw-data-bucket",
#                                  "C:\\Users\\matacza\\Desktop\\Projekty\\elexon-project\\decompressed_files\\S0142_20211115_DF_20240314140804.csv",
#                                  "test_data.csv")
