from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests


class StartSyncApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # data
            root_url = 'http://localhost:8000/api/'
            gmail = request.data.get("gmail")
            username = request.data.get("username")
            password = request.data.get("password")
            return_schedule = request.data.get("return_schedule")
            
            # verify user account
            url = f'{root_url}user/verify-account/'
            payload = {
                "username": username,
                "password": password
            }
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data['status'] == 200:
                access_token = data['access_token']
            else:
                return Response(data)
            
            
            # verify user gmail
            url = f'{root_url}google-calendar/verify-gmail/'
            payload = {
                "gmail": gmail
            }
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data['status'] != 200:
                return Response(data)
            else:
                pass
            
            
            # get schedule
            url = f'{root_url}schedule/'
            payload = {
                "access_token": access_token,
            }
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data['status'] == 200:
                schedules = data['schedules']
                semester_start_day = data['semester_start_day']
                semester_end_day = data['semester_end_day']
                events = self.convert_schedule_to_event(schedules)
            else:
                return Response(data)

            
            # upload google calendar
            url = f'{root_url}google-calendar/upload/'
            payload = {
                "events": events,
                "calendar_start_day": semester_start_day,
                "calendar_end_day": semester_end_day,
                "gmail": gmail
            }
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data['status'] == 201:
                response_data = {"message": "Đồng bộ hoàn tất", "status": 200}
                if return_schedule:
                    response_data['schedules'] = schedules
                return Response(response_data) 
            else:
                return Response(data)       
            
        except Exception as e:
            print("Error creating events:", e)
            response_data = {"error": "Lỗi server, đồng bộ thất bại", "status": 500}
            return Response(response_data)
        

    def convert_schedule_to_event(self, schedules):
        def convert_day_in_week(day_in_week: int):
            if day_in_week == 2:
                return "MO"
            elif day_in_week == 3:
                return "TU"
            elif day_in_week == 4:
                return "WE"
            elif day_in_week == 5:
                return "TH"
            elif day_in_week == 6:
                return "FR"
            elif day_in_week == 7:
                return "SA"
            else:
                return "SU"

        events = []
        for schedule in schedules:
            event = {
                "start": {"timeZone": "Asia/Ho_Chi_Minh"},
                "end": {"timeZone": "Asia/Ho_Chi_Minh"},
            }

            start_day = datetime.strptime(schedule["start_day"], "%d/%m/%y").date()
            end_day = (
                datetime.strptime(schedule["end_day"], "%d/%m/%y") + timedelta(days=1)
            ).date()
            start_time = datetime.strptime(schedule["start_time"], "%H:%M").time()
            end_time = (
                datetime.strptime(schedule["end_time"], "%H:%M") + timedelta(hours=1)
            ).time()
            recurrence_rule = f'RRULE:FREQ=WEEKLY;BYDAY={convert_day_in_week(schedule["day_in_week"])};UNTIL={end_day.strftime("%Y%m%d")}'

            event["start"]["dateTime"] = datetime.combine(start_day, start_time).isoformat()
            event["end"]["dateTime"] = datetime.combine(start_day, end_time).isoformat()
            event["summary"] = schedule["subject_name"]
            event["description"] = "-".join(
                [schedule["subject_id"], schedule["group_id"], schedule["lecturer_name"]]
            )
            event["location"] = schedule["room_id"]
            event["recurrence"] = [recurrence_rule]
            events.append(event)

        return events
