from datetime import timedelta, date


class DataConfigurator:

    def timeframe_window(self):
        yesterday = date.today() - timedelta(days=1)
        return yesterday
