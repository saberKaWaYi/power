from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def get_data(request):
    return Response(request.data)