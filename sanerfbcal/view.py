"""The main views."""

from datetime import datetime
import cherrypy
import icalendar
import requests


class RootView(object):

    """The root of our site."""

    @cherrypy.expose
    def index(self):
        """Display the index page."""
        return 'Hello world'


class FbCalendarView(object):

    """Proxy of the Facebook iCal endpoint."""

    _ENDPOINT = 'https://www.facebook.com/ical/{}'

    class CalendarType:
        BIRTHDAY = 'B'
        UPCOMING_EVENT = 'U'

    class UpcomingEventType:
        ACCEPTED = 'ACCEPTED'
        TENTATIVE = 'TENTATIVE'
        NEEDS_ACTION = 'NEEDS-ACTION'

        __VALID_TYPE = set([ACCEPTED, TENTATIVE, NEEDS_ACTION])

        @staticmethod
        def filter_valid(type_list):
            """
            Filter the type list for valid options.

            :param list type_list: The set of event types to be validated.
            :returns: The set of valid options from the input list.
            :rtype: set
            """
            if not isinstance(type_list, (list, tuple)):
                type_list = [type_list]

            return FbCalendarView.UpcomingEventType.__VALID_TYPE.intersection(
                type_list)

    def __init__(self, cal_type):
        """
        Constructor.

        :param FbCalendarView.CalendarType cal_type: The type of Facebook
            calendar.
        """
        self._cal_type = cal_type

    @cherrypy.expose
    @cherrypy.tools.response_headers(
        headers=[('Content-Type', 'text/calendar')])
    def index(self, uid, key, **kwargs):
        """Display the index page."""
        if self._cal_type == self.CalendarType.BIRTHDAY:
            return self._birthday(uid, key)
        elif self._cal_type == self.CalendarType.UPCOMING_EVENT:
            return self._upcoming(uid, key, **kwargs)

    def _birthday(self, uid, key):
        """
        Query the Facebook birthday iCal, cleanup and return.

        :param str uid: The UID to the Facebook iCal endpoint.
        :param str key: The key to the Facebook iCal endpoint.
        """
        resp = requests.get(
            self._ENDPOINT.format('b.php'), {'uid': uid, 'key': key})
        calendar = icalendar.Calendar.from_ical(resp.content)
        for event in calendar.subcomponents:
            start_date = datetime.strptime(
                event['DTSTART'].to_ical(), '%Y%m%d')
            event.add('dtstart', start_date.date())

        return calendar.to_ical()

    def _upcoming(
            self, uid, key, status=[UpcomingEventType.ACCEPTED]):
        """
        Query the Facebook upcoming events iCal, cleanup and return.

        :param str uid: The UID to the Facebook iCal endpoint.
        :param str key: The key to the Facebook iCal endpoint.
        """
        status_list = self.UpcomingEventType.filter_valid(status)

        resp = requests.get(
            self._ENDPOINT.format('u.php'), {'uid': uid, 'key': key})
        calendar = icalendar.Calendar.from_ical(resp.content)

        calendar.subcomponents = [
            event
            for event in calendar.subcomponents
            if event['PARTSTAT'] in status_list]
        return calendar.to_ical()
