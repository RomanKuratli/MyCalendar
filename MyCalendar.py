from flask import Flask, render_template, redirect, url_for
import os
from icalendar import Calendar as ICalendar
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
from collections import defaultdict


def format_time(dt):
    return dt.strftime("%H:%M")


app = Flask(__name__)
app.jinja_env.filters["time"] = format_time
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CALENDAR_PATH = os.path.join(APP_ROOT, "static", "calendar_data")
ALL_EVENTS = []
CURRENT_DATE = datetime.now()
MONTH_DELTA = relativedelta(months=1)


def event_to_dict(event):
    return {
        "summary": str(event["SUMMARY"]),
        "desc": str(event["DESCRIPTION"]),
        "start": event["DTSTART"].dt,
        "end": event["DTEND"].dt
    }


def event_sort_key(event):
    return event["start"]


@app.route('/')
def index():
    global ALL_EVENTS, CURRENT_DATE
    year, month = CURRENT_DATE.year, CURRENT_DATE.month
    events = sorted(
        [e for e in ALL_EVENTS if e["start"].month == month and e["start"].year == year],
        key=event_sort_key
    )
    grouped_events = defaultdict(list)
    for event in events:
        grouped_events[event["start"].day].append(event)

    return render_template(
        "index.html",
        year=year,
        month_name=calendar.month_name[month],
        events=grouped_events,
        day_names=calendar.day_name[:5],  # no school on weekends
        month=calendar.monthcalendar(year, month)
    )


@app.route("/next_month")
def next_month():
    global CURRENT_DATE, MONTH_DELTA
    CURRENT_DATE += MONTH_DELTA
    return redirect(url_for("index"))


@app.route("/previous_month")
def previous_month():
    global CURRENT_DATE, MONTH_DELTA
    CURRENT_DATE -= MONTH_DELTA
    return redirect(url_for("index"))


def load_calendars():
    global ALL_EVENTS
    # load all .ics files
    for ics_name in os.listdir(CALENDAR_PATH):
        if ics_name.endswith(".ics"):
            ics_path = os.path.join(CALENDAR_PATH, ics_name)
            with open(ics_path) as ics_file:
                c = ICalendar.from_ical(ics_file.read())
                ALL_EVENTS += [event_to_dict(e) for e in c.walk("VEVENT")]


if __name__ == '__main__':
    load_calendars()
    app.run()

