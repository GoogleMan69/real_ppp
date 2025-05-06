from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from datetime import datetime



# name of the table sys_user
# userid	usermail	userpwd	errcnt	lasttm	datest	dateed	lockuser

def index(request: HttpRequest):
    if request.method == "GET":
        return render(request, "index.html")

    elif request.method == "POST":
        usermail = request.POST.get("usermail")
        userpwd = request.POST.get("userpwd")

        if not usermail or not userpwd:
            return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Missing email or password"})

        with connection.cursor() as cursor:
            # Search user from table with usermail
            cursor.execute("SELECT * FROM sys_user WHERE usermail = %s", [usermail])
            results = cursor.fetchall()

            # Check if user exists
            if len(results) == 0:
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "No such member found"})

            # Extract user details
            userid, usermail_db, userpwd_db, errcnt_db, lasttm, datest, dateed, lockuser = results[0]

            # Ensure errcnt is not None
            errcnt = errcnt_db or 0  # Default to 0 if errcnt is None

            # Convert datest and dateed to datetime.date if they are not None
            current_date = datetime.now().date()
            if datest:
                datest = datetime.strptime(datest, "%Y%m%d").date()
            if dateed:
                dateed = datetime.strptime(dateed, "%Y%m%d").date()

            # Check if the account has started
            if datest and current_date < datest:
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Your account is not active yet."})

            # Check if the account has ended
            if dateed and current_date > dateed:
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Your account has expired."})

            # Check if the user has exceeded the limit of incorrect password attempts
            if errcnt > 3:
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Too many incorrect password attempts"})

            # Check if the password is correct
            if userpwd != userpwd_db:
                # Increment the error count
                cursor.execute("UPDATE sys_user SET errcnt = errcnt + 1 WHERE usermail = %s", [usermail])
                # Fetch the updated error count
                cursor.execute("SELECT errcnt FROM sys_user WHERE usermail = %s", [usermail])
                errcnt = cursor.fetchone()[0]

                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Incorrect user password"})

                # CHeck if the account is locked
            if lockuser == "Y":
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Your account is locked"})
            # Successful login
            cursor.execute("UPDATE sys_user SET errcnt = 0, lasttm = %s " \
                            "WHERE usermail = %s", [datetime.now(), usermail])
            return render(request, "default.html")

    else:
        return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Unsupported HTTP method"})
    
def logout(request: HttpRequest):
    # Clear the session and redirect to the login page
    if "userid" in request.session:
        del request.session["userid"]
    return redirect("../")
