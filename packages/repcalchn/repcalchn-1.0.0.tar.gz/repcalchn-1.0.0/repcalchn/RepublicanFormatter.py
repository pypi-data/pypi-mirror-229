""""
This file is partially borrowed from https://github.com/dekadans/repcal
"""

class RepublicanFormatter:
    def __init__(self, rdate=None, dtime=None):
        """
        :param rdate: RepublicanDate
        :param dtime: DecimalTime
        """
        self.rdate = rdate
        self.dtime = dtime

    def format(self, fstring: str):
        fstring = self._clean(fstring)
        return fstring.format(**self._data())

    def _clean(self, fstring: str):
        if self.rdate is not None and self.rdate.is_sansculottides():
            fstring = fstring.replace('{%d}', '').replace('{%B}', '')
            fstring = ' '.join(fstring.split())

        return fstring

    def _data(self):
        time_data = date_data = {}

        if self.rdate is not None:
            date_data = {
                '%Y': self.rdate.get_year_roman(),
                '%y': self.rdate.get_year_arabic(),
                '%B': self.rdate.get_month().lower() if self.rdate.get_month() is not None else '',
                '%b': self.rdate.get_month_chn() if self.rdate.get_month_chn() is not None else '',
                '%W': self.rdate.get_week_number() or '',
                '%d': self.rdate.get_day() or '',
                '%A': self.rdate.get_weekday().lower() if self.rdate.get_weekday() is not None else '',
                '%a': self.rdate.get_weekday_chn() if self.rdate.get_weekday_chn() is not None else '',
                '%x': self.rdate.get_unique_chn(),
                '%X': self.rdate.get_full_unique_chn(),
            }

        if self.dtime is not None:
            time_data = {
                '%H': self.dtime.hour,
                '%M': self.dtime.minute,
                '%S': self.dtime.second
            }

        return {**time_data, **date_data}
