from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests


class ScheduleApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            access_token = request.data.get('access_token')
            hoc_ky, semester_start_day, semester_end_day = self.get_semester_data(access_token)
            
            if hoc_ky is None or semester_start_day is None or semester_end_day is None:
                raise Exception("Can't find semester data")
            
            url = "https://qldt.ptit.edu.vn/api/sch/w-locdstkbhockytheodoituong"
            payload = {
                "hoc_ky": hoc_ky, 
                "loai_doi_tuong": 1, 
                "id_du_lieu": None
            }
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()["data"]["ds_nhom_to"]
            
            schedules = []
            for schedule_data in data:
                schedule = {}
                tkb = schedule_data["tkb"].split()
                schedule["subject_id"] = schedule_data["ma_mon"]
                schedule["subject_name"] = schedule_data["ten_mon"]
                schedule["group_id"] = schedule_data["nhom_to"]
                schedule["room_id"] = schedule_data["phong"]
                schedule["lecturer_name"] = schedule_data["gv"]
                schedule["start_time"] = schedule_data["tu_gio"]
                schedule["end_time"] = schedule_data["den_gio"]
                schedule["start_day"] = tkb[0]
                schedule["end_day"] = tkb[2]
                schedule["day_in_week"] = schedule_data["thu"]
                schedules.append(schedule)
                
            if len(schedules) > 0:
                response_data = {
                    "status": 200,
                    "schedules": schedules, 
                    "semester_start_day": semester_start_day,
                    "semester_end_day": semester_end_day
                }
                return Response(response_data)
            else:
                response_data = {"error": "Không tìm thấy thời khóa biểu", "status": 400}
                return Response(response_data)

        except Exception as e:
            print(e)
            response_data = {"error": "Lỗi server", "status": 500}
            return Response(response_data)
        
    
    def get_semester_data(self, access_token):
        try:
            url = "https://qldt.ptit.edu.vn/api/sch/w-locdshockytkbuser"
            payload = {
                "filter": {
                    "is_tieng_anh": None
                },
                "additional": {
                    "paging": {
                        "limit": 100,
                        "page": 1
                    },
                    "ordering": [
                        {
                            "name": "hoc_ky",
                            "order_type": 1
                        }
                    ]
                }
            }
            headers = {
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()['data']['ds_hoc_ky']
            hocky = data[0]['hoc_ky']
            semester_start_day = data[0]['ngay_bat_dau_hk']
            semester_end_day = data[0]['ngay_ket_thuc_hk']
            return (hocky, semester_start_day, semester_end_day)
            
        except Exception as e:
            print(e)
        