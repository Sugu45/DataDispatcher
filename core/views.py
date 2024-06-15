import json
import sys
import traceback

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Account, Destination
from .response_serlizer.serializers import AccountSerializer,DestinationSerializer
import requests


@api_view(['GET','POST'])

def account_crud(request):
    try:
        data =json.loads(request.body)
        action = data.get('action')
        jsondata = data.get('data')
        if (action == 'CREATE'):
            if not jsondata.get('id') is None:
                id=jsondata.pop('id', None)
                Account.objects.filter(id=id).update(**jsondata)
                account_u = Account.objects.get(id=id)
                serializer = AccountSerializer(account_u)
                serializer_data = {"data": serializer.data}
            else:
                account_c = Account.objects.create(**jsondata)
                serializer = AccountSerializer(account_c)
                serializer_data = {"data": serializer.data}
            response = HttpResponse(json.dumps(serializer_data), content_type='application/json')
            return response
        elif action == 'FETCH':
            page_number = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            condtion = Q()
            if jsondata.get('account_id') is not None and jsondata.get('account_id') != '':
                condtion &= Q(account_id=jsondata.get('account_id'))
            if jsondata.get('email') is not None and jsondata.get('email') != '':
                condtion &= Q(email=jsondata.get('email'))
            if jsondata.get('email') is not None and jsondata.get('email') != '':
                condtion &= Q(email=jsondata.get('email'))
            if jsondata.get('app_secret_token') is not None and jsondata.get('app_secret_token') != '':
                condtion &= Q(app_secret_token=jsondata.get('app_secret_token'))
            if jsondata.get('account_name') is not None and jsondata.get('account_name') != '':
                condtion &= Q(account_name=jsondata.get('account_name'))

            profiles = Account.objects.filter(condtion)
            paginator = Paginator(profiles, page_size)
            page_obj = paginator.page(page_number)
            serialized_profiles = AccountSerializer(page_obj.object_list, many=True).data
            data = {
                'data': serialized_profiles,
                'page_number': page_number,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count
            }
            return HttpResponse(json.dumps(data))
        elif action == 'DELETE':
            profile_d = Account.objects.filter(id=jsondata.get('id')).delete()
            return HttpResponse(json.dumps({'message': 'Account deleted'}))
    except Exception as excep:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        traceback.print_exc()
        error_obj = {}
        error_obj['status'] = "Falied"
        error_obj['message'] = (str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
            ', exception_type : {c} '.format(c=type(excep).__name__)))
        return HttpResponse(json.dumps(error_obj, indent=4), content_type='application/json')

@api_view(['GET','POST'])
def destination_crud(request):
    try:
        data =json.loads(request.body)
        action = data.get('action')
        jsondata = data.get('data')
        if (action == 'CREATE'):
            if not jsondata.get('id') is None:
                id=jsondata.pop('key', None)
                profile_u = Destination.objects.get(id=id).update(**jsondata)
                serializer = DestinationSerializer(profile_u)
                serializer_data = {"data": serializer.data}
            else:
                profile_c = Destination.objects.create(**jsondata)
                serializer = DestinationSerializer(profile_c)
                serializer_data = {"data": serializer.data}
            response = HttpResponse(json.dumps(serializer_data), content_type='application/json')
            return response
        elif action == 'FETCH':
            page_number = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            condtion = Q()
            if jsondata.get('account') is not None and jsondata.get('account') != '':
                condtion &= Q(account=jsondata.get('account'))
            if jsondata.get('url') is not None and jsondata.get('url') != '':
                condtion &= Q(url=jsondata.get('url'))
            if jsondata.get('http_method') is not None and jsondata.get('http_method') != '':
                condtion &= Q(http_method=jsondata.get('http_method'))
            if jsondata.get('account_id') is not None and jsondata.get('account_id') != '':
                condtion &= Q(account_id=jsondata.get('account_id'))

            profiles = Destination.objects.filter(condtion)
            paginator = Paginator(profiles, page_size)
            page_obj = paginator.page(page_number)
            serialized_profiles = DestinationSerializer(page_obj.object_list, many=True).data
            data = {
                'data': serialized_profiles,
                'page_number': page_number,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count
            }
            return HttpResponse(json.dumps(data))
        elif action == 'DELETE':
            profile_d = Destination.objects.filter(id=jsondata.get('id')).delete()
            return HttpResponse(json.dumps({'Destination': 'Account deleted'}))
    except Exception as excep:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        traceback.print_exc()
        error_obj = {}
        error_obj['status'] = "Falied"
        error_obj['message'] = (str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
            ', exception_type : {c} '.format(c=type(excep).__name__)))
        return HttpResponse(json.dumps(error_obj, indent=4), content_type='application/json')
@api_view(['GET'])
def get_destinations(request, account_id):
    try:
        destinations = Destination.objects.filter(account__account_id=account_id)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DestinationSerializer(destinations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def incoming_data(request):
    try:
        secret_token = request.headers.get('CL-X-TOKEN')
        if not secret_token:
            return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            account = Account.objects.get(app_secret_token=secret_token)
        except Account.DoesNotExist:
            return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

        for destination in account.destinations.all():
            headers = destination.headers
            if destination.http_method.upper() == 'GET':
                response = requests.get(destination.url, params=request.data, headers=headers)
            elif destination.http_method.upper() == 'POST':
                response = requests.post(destination.url, json=request.data, headers=headers)
            elif destination.http_method.upper() == 'PUT':
                response = requests.put(destination.url, json=request.data, headers=headers)

        return Response({'message': 'Data sent to destinations'}, status=status.HTTP_200_OK)
    except Exception as excep:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        traceback.print_exc()
        error_obj = {}
        error_obj['status'] = "Falied"
        error_obj['message'] = (str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
            ', exception_type : {c} '.format(c=type(excep).__name__)))
        return HttpResponse(json.dumps(error_obj, indent=4), content_type='application/json')