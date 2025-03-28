from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db import connection

# Create your views here.
def index(request: HttpRequest):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM sys_user")
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    return render(request, 'index.html', {'colmset': columns,
                                           'dataset': results})