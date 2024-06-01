from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta


class UploadApiView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            credentials = Credentials.from_service_account_file(
                "resources\\synchronize-schedule-calendar-c2cbf92e626b.json",
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            service = build("calendar", "v3", credentials=credentials)
        except Exception as e:
            print(e)
            service = None

        self.service = service
    
    
    def post(self, request, *args, **kwargs):
        error_count = 0

        def handle_batch_response(request_id, response, exception):
            if exception is not None:
                print(f"Error adding event for request {request_id}: {exception}")
                error_count += 1
            else:
                print(f"Event added successfully: {request_id}")

        try:
            events = request.data.get('events')
            gmail = request.data.get('gmail')
            calendar_start_day = request.data.get('calendar_start_day')
            calendar_end_day = request.data.get('calendar_end_day')
            
            subject_name_list = set([event["summary"] for event in events])

            # remove duplicate events if possible
            self.delete_event_list_google_calendar(
                gmail, self.get_event_list_google_calendar(
                    gmail, list(subject_name_list), calendar_start_day, calendar_end_day
                )
            )
            batch = self.service.new_batch_http_request()
            for event in events:
                batch.add(
                    self.service.events().insert(calendarId=gmail, body=event),
                    callback=lambda request_id, response, exception: handle_batch_response(
                        request_id, response, exception
                    ),
                )

            batch.execute()

            if error_count == 0:
                response_data = {
                    "message": "Cập nhật thành công lên Google Calendar",
                    "status": 201
                }
                return Response(response_data)
            else:
                response_data = {
                    "error": f"Cập nhật thất bại, {len(events)-error_count}/{len(events)} sự kiện thành công", 
                    "status": 400
                }
                return Response(response_data)

        except Exception as e:
            print("Error creating events:", e)
            response_data = {"error": "Lỗi server", "status": 500}
            return Response(response_data)
    
    
    def delete_event_list_google_calendar(self, gmail, event_ids):
        def handle_batch_response(request_id, response, exception):
            if exception is not None:
                print(f"Error delete events for request {request_id}: {exception}")
            else:
                print(f"Delete event {request_id}")

        batch = self.service.new_batch_http_request()
        for id in event_ids:
            batch.add(
                self.service.events().delete(calendarId=gmail, eventId=id),
                callback=lambda request_id, response, exception: handle_batch_response(
                    request_id, response, exception
                ),
            )

        batch.execute()   
    
    
    def get_event_list_google_calendar(self, gmail, subject_name_list, start, end):
        def handle_batch_response(request_id, response, exception):
            if exception is not None:
                print(f"Error retrieving events for request {request_id}: {exception}")
            else:
                for item in response.get("items", []):
                    event_ids.append(item["id"])

        start_date = datetime.strptime(start, '%d/%m/%Y').isoformat() + "Z"
        end_date = datetime.strptime(end, '%d/%m/%Y').isoformat() + "Z"
        event_ids = []

        batch = self.service.new_batch_http_request()
        for subject_name in subject_name_list:
            batch.add(
                self.service.events().list(
                    calendarId=gmail,
                    timeMin=start_date,
                    timeMax=end_date,
                    singleEvents=True,
                    q=subject_name,
                ),
                callback=lambda request_id, response, exception: handle_batch_response(
                    request_id, response, exception
                ),
            )

        batch.execute()
        return event_ids
    
    
    
class VerifyGmailApiView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        try:
            credentials = Credentials.from_service_account_file(
                "resources\\synchronize-schedule-calendar-c2cbf92e626b.json",
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            service = build("calendar", "v3", credentials=credentials)
        except Exception as e:
            print(e)
            service = None

        self.service = service
        
        
    def post(self, request, *args, **kwargs):
        try:
            gmail = request.data.get('gmail')
            if gmail is None:
                raise Exception("Gmail address is not provided")
            
            if self.service is None:
                raise Exception("Error creating serivce account")
            
            # test to create event:
            test_id = datetime.now().strftime("test%d%m%Y%H%M%S%f")
            start_time = datetime.now() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            timezone = "Asia/Ho_Chi_Minh"
            event = {
                "id": test_id,
                "summary": "Test Event",
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone,
                },
            }
            
            try:
                self.service.events().insert(calendarId=gmail, body=event).execute()
                self.service.events().delete(calendarId=gmail, eventId=test_id).execute()
                
                response_data = {"message": "Calendar đã được chia sẻ", "status": 200}
                return Response(response_data)
            
            except Exception as e:
                print("Error sharing calendar", e)
                response_data = {
                    "error": "Bạn chưa chia sẻ calendar với service gmail của chúng tôi",
                    "status": 400
                }
                return Response(response_data)  

        except Exception as e:
            print(e)
            response_data = {"error": "Lỗi server", "status": 500}
            return Response(response_data)
