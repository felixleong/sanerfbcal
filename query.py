from datetime import datetime
import requests
import icalendar


UPCOMING_ENDPOINT = 'https://www.facebook.com/ical/u.php'
BIRTHDAY_ENDPOINT = 'https://www.facebook.com/ical/b.php'


def birthday(uid, key):
    resp = requests.get(BIRTHDAY_ENDPOINT, {'uid': uid, 'key': key})
    calendar = icalendar.Calendar.from_ical(resp.content)
    for event in calendar.subcomponents:
        start_date = datetime.strptime(event['DTSTART'].to_ical(), '%Y%m%d')
        event.add('dtstart', start_date.date())

    return calendar.to_ical()


def upcoming(
        uid, key, show_accepted=True, show_tentative=False,
        show_need_action=False):
    status = []
    if show_accepted:
        status.append('ACCEPTED')
    if show_tentative:
        status.append('TENTATIVE')
    if show_need_action:
        status.append('NEEDS-ACTION')

    resp = requests.get(UPCOMING_ENDPOINT, {'uid': uid, 'key': key})
    calendar = icalendar.Calendar.from_ical(resp.content)

    calendar.subcomponents = [
        event
        for event in calendar.subcomponents
        if event['PARTSTAT'] in status]
    return calendar.to_ical()
