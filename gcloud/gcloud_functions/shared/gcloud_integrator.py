from google.cloud import secretmanager_v1
from google.cloud import storage
import json
import requests
import os 
import datetime

class GCloudIntegrator:

    def __init__(self, project_id, data_configurator) -> None:
        self.cloud_key = None
        self.project_id = project_id
        self.DataConfiguratorObject = data_configurator

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


    
    def download_file_to_gcs(self, bucket_name, blob_name, filename_endpoint):
        """
        Downloads a file from the Elexon portal and saves it directly to a Google Cloud Storage bucket.
        Organizes files into subfolders based on their names (e.g., 'S0142_20241107_II_20241112062517.gz' 
        goes into a folder named 's0142').
        """
        try:
            response = requests.get(filename_endpoint, stream=True)
            response.raise_for_status()

            # Extract filename from the endpoint URL
            filename = filename_endpoint.split('filename=')[-1]
            publish_date = filename.split('_')[-1]
            

            timestamp = self.DataConfiguratorObject.extract_date_from_filename(publish_date)

            # Extract folder name from filename 
            folder_name = filename.split('_')[0]

            if folder_name.lower() == 's0142':
                blob_name = os.path.join(folder_name, timestamp, filename)  # Path in the bucket: 'S0142/2024-11-12/S0142_20241107_II_20241112062517.gz'

                bucket = self._get_google_cloud_client().bucket(bucket_name) 
                blob = bucket.blob(blob_name)

                # Extract file extension
                file_extension = os.path.splitext(filename)[1]

                # Set the content type to indicate gzip compression
                if file_extension == '.gz': 
                    blob.content_type = 'application/gzip'

                with blob.open('wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Downloaded from {filename_endpoint} to gs://{bucket_name}/{blob_name}")

        except requests.RequestException as e:
            print(f"Error downloading file: {filename_endpoint}. Error: {e}")
        except Exception as e:
            print(f"Error uploading to GCS: {filename_endpoint}. Error: {e}")

