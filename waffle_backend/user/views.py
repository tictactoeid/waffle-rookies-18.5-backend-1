from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from user.serializers import UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # POST /api/v1/user/
    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        #print(last_name)
        if not username or not email or not password:
            #print('a')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        elif not first_name and not last_name: # 둘 다 없는 경우, 즉 3번의 경우
            try:
                # Django 내부에 기본으로 정의된 User에 대해서는 create가 아닌 create_user를 사용
                # password가 자동으로 암호화되어 저장됨. database를 직접 조회해도 알 수 없는 형태로 저장됨.
                user = User.objects.create_user(username, email, password)

            except IntegrityError:  # 중복된 username
                return Response(status=status.HTTP_409_CONFLICT)

        elif (first_name and not last_name) or (last_name and not first_name):  # 하나만 있는 경우
            return Response(status=status.HTTP_400_BAD_REQUEST)

        else:  # 둘 다 있는 경우
            if any(x.isdigit() for x in first_name) or any(x.isdigit() for x in last_name):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
                except IntegrityError:  # 중복된 username
                    return Response(status=status.HTTP_409_CONFLICT)


        '''elif first_name: # first_name은 있음
            if any(x.isdigit() for x in first_name): #first_name에 숫자 포함
                #print('b')
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif not last_name: #first_name은 일단 통과, last_name은 없음
                #print('c')
                #print(last_name)
                #print(type(last_name))
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif any(x.isdigit() for x in last_name): #last_name에 숫자 포함
                #print('d')
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    # Django 내부에 기본으로 정의된 User에 대해서는 create가 아닌 create_user를 사용
                    # password가 자동으로 암호화되어 저장됨. database를 직접 조회해도 알 수 없는 형태로 저장됨.
                    user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)

                except IntegrityError:  # 중복된 username
                    return Response(status=status.HTTP_409_CONFLICT)'''


        # 가입했으니 바로 로그인 시켜주기
        login(request, user)
        # login을 하면 Response의 Cookies에 csrftoken이 발급됨
        # 이후 요청을 보낼 때 이 csrftoken을 Headers의 X-CSRFToken의 값으로 사용해야 POST, PUT 등의 method 사용 가능
        return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)

    # PUT /api/v1/user/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # authenticate라는 함수는 username, password가 올바르면 해당 user를, 그렇지 않으면 None을 return
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # login을 하면 Response의 Cookies에 csrftoken이 발급됨 (반복 로그인 시 매번 값이 달라짐)
            # 이후 요청을 보낼 때 이 csrftoken을 Headers의 X-CSRFToken의 값으로 사용해야 POST, PUT 등의 method 사용 가능
            return Response(self.get_serializer(user).data)
        # 존재하지 않는 사용자이거나 비밀번호가 틀린 경우
        return Response(status=status.HTTP_403_FORBIDDEN)

    # PUT /api/v1/user/
    # 함수 이름을 changeUserData() 등 새로 정의하면 /api/v1/user/changeUserData/가 되고
    # put()을 사용하면 PUT /api/v1/user에서 사용할 수 있다.
    def put(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not first_name and not last_name:  # 둘 다 없는 경우, 즉 3번의 경우
            try:
                user = request.user
                user.username = username
                user.save()

            except IntegrityError:  # 중복된 username
                return Response(status=status.HTTP_409_CONFLICT)

        elif (first_name and not last_name) or (last_name and not first_name): # 하나만 있는 경우
            return Response(status=status.HTTP_400_BAD_REQUEST)

        else: # 둘 다 있는 경우
            if any(x.isdigit() for x in first_name) or any(x.isdigit() for x in last_name):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = request.user
                    user.username = username
                    user.last_name = last_name
                    user.first_name = first_name
                    user.save()
                except IntegrityError:  # 중복된 username
                    return Response(status=status.HTTP_409_CONFLICT)

        return Response(status=status.HTTP_200_OK)

    #GET /api/v1/user/logout/
    @action(detail=False, methods=['GET'])
    def logout(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            logout(request)
            return Response(status=status.HTTP_200_OK)

    # GET /api/v1/user/
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)