from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests


class VerifyAccountApiView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            url = "https://qldt.ptit.edu.vn/api/auth/login"
            payload = f"username={username}&password={password}&grant_type=password"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            access_token = data.get("access_token")

            if access_token is None:
                response_data = {"error": "Thông tin đăng nhập không đúng", "status": 400}
                return Response(response_data)
            else:
                response_data = {"access_token": access_token, "status": 200}
                return Response(response_data)

        except Exception as e:
            print(e)
            response_data = {"error": "Lỗi server", "status": 500}
            return Response(response_data)
