from nylas import Client
from nylas.resources import calendars

nylas = Client(
    api_key="nyk_v0_H9buavt1RZH2fQbVrPLjxcDxOKxLzZgbwvBjezO1Cn3I8VwD0LuLp1z5D9LfYsAt",
    api_uri="https://api-staging.us.nylas.com",
)

# res = nylas.calendars.create("mostafa.r@nylas.com", {"name": "test calendar"})

calendars
