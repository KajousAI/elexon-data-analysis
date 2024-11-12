import datetime
import re


class DataConfigurator:

    
    def extract_date_from_filename(self, filename):
        """
        Extracts the date from a filename in the format "S0142_20240924_R1_20241112100408.gz".

        Args:
            filename: The filename to extract the date from.

        Returns:
            The extracted date as a string in "yyyy-mm-dd" format.
        """
        # Use regular expression to find the date part
        match = re.search(r'\d{8}', filename)
        if match:
            date_str = match.group(0)
            # Parse the date string into a datetime object
            date = datetime.datetime.strptime(date_str, "%Y%m%d")
            # Format the date as "yyyy-mm-dd"
            return date.strftime("%Y-%m-%d")
        else:
            return None  # Or raise an error if no date is found
