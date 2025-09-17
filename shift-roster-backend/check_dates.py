from datetime import date, timedelta

today = date.today()
start_date = (today - timedelta(days=today.weekday())).isoformat()
end_date = (today + timedelta(days=6-today.weekday())).isoformat()

print(f'Today: {today}')
print(f'Week start: {start_date}')
print(f'Week end: {end_date}')
print(f'Week range covers {(date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1} days')
print(f'Today is: {today.strftime("%A")}')
