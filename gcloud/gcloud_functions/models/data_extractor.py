import requests
import os
import gzip
import shutil


class DataExtractor:
    def __init__(self) -> None:
        # self.API = "alzf0zinvzwsfji"  # for aleksandra.matacz93@gmail.com
        self.API = "m4qq9k87r0vtnld"  # for a.matacz@o2.pl
        self.BASE_URL_LIST = "https://downloads.elexonportal.co.uk/p114/list"
        self.BASE_URL_DOWNLOAD = "https://downloads.elexonportal.co.uk/p114/download"

    def get_availability_data(self, date):
        """
        Get actuals data from URL
        """
        url = f"{self.BASE_URL_LIST}?key={self.API}&date={date}&filter=s0142"
        return self.get_data_from_url(url)

    def download_files_from_availability_data_and_save_it_locally(self, destination_folder):
        "Download data to given folder."

        availability_data = self.get_availability_data()  # Get availability data
        print("DOWNLOADING....")

        if not os.path.exists(destination_folder):  # If not exists - make folder for download data
            os.makedirs(destination_folder)

        # loop through availability data
        for data in availability_data:
            # set url for downloading data
            url = f"{self.BASE_URL_DOWNLOAD}?key={self.API}&filename={data}"

            # create file_name and file path for downloading data
            file_name = url.split("filename=")[-1]
            file_path = os.path.join(destination_folder, file_name)

            # Download data and save it to
            r = requests.get(url, stream=True)
            if r.ok:
                with open(file_path, 'wb') as f:  # open file from path in binary mode
                    for chunk in r.iter_content(chunk_size=1024 * 8):  # split data for small chunkes
                        if chunk:  # assure if chunk of data is not empty
                            f.write(chunk)  # write chunk of data to file
                            f.flush()  # clear binary buffer
                            os.fsync(f.fileno())  # making sure that file is written down
            else:  # HTTP status code 4XX/5XX
                print("Download failed: status code {}\n{}".format(
                    r.status_code,
                    r.text))

    def download_files_from_availability_data(self, filename):

        url = f"{self.BASE_URL_DOWNLOAD}?key={self.API}&filename={filename}"

        # Download the file content
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download file from Elexon portal.")

        return response.content

    def decompress_downloaded_data(self,
                                   download_destination_folder: str,
                                   decompress_destination_folder: str) -> None:
        """
        Decompress dowloaded data to given folder.
        Returns list of decompressed files paths.
        """

        print("EXTRACTING....")

        # Creating separate folder for decompressed files if not exists
        if not os.path.exists(decompress_destination_folder):
            os.makedirs(decompress_destination_folder)

        # Creating list of downloaded file paths
        files_list = [x.path for x in os.scandir(os.path.join(os.getcwd(), download_destination_folder))]

        # Changing working directory to folder for decompressed files
        os.chdir(os.path.join(os.getcwd(), decompress_destination_folder))

        # Loop through list of downloaded file paths and decompress
        for file in files_list:
            # Create name for decompressed file -> extract file name from path and correct extension
            file_name = file.split("\\")[-1].replace(".gz", ".csv")
            # Open compressed file in binary mode
            with gzip.open(file, 'rb') as f_in:
                # Opened destination file in binary mode
                with open(file_name, 'wb') as f_out:
                    # Copy content of compressed file to destination file
                    shutil.copyfileobj(f_in, f_out)

        decompressed_files_list = [x.path for x in os.scandir()]
        return decompressed_files_list

    def get_data_from_url(self, url: str):
        """
        Asserts response from url call.
        Return empty dict if fetching error occurs.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from URL: {url}. Error: {e}.")
            return {}  # or raise the exception or return some default value

# x = DataExtractor()
# x.download_files_from_availability_data("downloaded_files")
# x.decompress_downloaded_data("decompressed_files")
