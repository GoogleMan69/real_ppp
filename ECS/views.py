from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db import connection

# Create your views here.
def index(request: HttpRequest):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM sys_user")
        results = cursor.fetchall()
        htmlStr = "<html><body><table border='1'>"
        for row in results:
            htmlStr = htmlStr + "<tr>" + \
                f"<td>{row[0]}</td>" + \
                f"<td>{row[1]}</td>" + \
                f"<td>{row[2]}</td>" + \
                f"<td>{row[3]}</td>" + \
                f"<td>{row[4]}</td>" + \
                f"<td>{row[5]}</td>" + \
                f"<td>{row[6]}</td>" + \
                f"<td>{row[7]}</td>" + \
                "</tr>"
        htmlStr = htmlStr + "</table></body></html>"

    return HttpResponse(htmlStr)