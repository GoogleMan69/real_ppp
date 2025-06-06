from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.db import connection
from datetime import datetime
from django.urls import reverse

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

            # Check if the account is locked
            if lockuser == "Y":
                return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Your account is locked"})

            # Successful login
            cursor.execute("UPDATE sys_user SET errcnt = 0, lasttm = %s WHERE usermail = %s", [datetime.now(), usermail])
            request.session["userid"] = userid  # <-- Set session BEFORE returning
            return render(request, "default.html")

    else:
        return render(request, "index.html", {"errtitle": "Login failed", "errmsg": "Unsupported HTTP method"})

def logout(request: HttpRequest):
    # Clear the session and redirect to the login page
    if "userid" in request.session:
        del request.session["userid"]
    return redirect("../")

def users(request: HttpRequest):
    msg = errmsg = None
    if request.method == "POST":
        # Delete user
        delete_userid = request.POST.get("delete_userid")
        if delete_userid:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sys_user WHERE userid = %s", [delete_userid])
            msg = "User deleted successfully."
        # Edit user
        elif request.POST.get("edit_userid"):
            edit_userid = request.POST.get("edit_userid")
            edit_usermail = request.POST.get("edit_usermail")
            edit_userpwd = request.POST.get("edit_userpwd")
            edit_errcnt = request.POST.get("edit_errcnt")
            edit_lasttm = request.POST.get("edit_lasttm")
            edit_datest = request.POST.get("edit_datest")
            edit_dateed = request.POST.get("edit_dateed")
            edit_lockuser = request.POST.get("edit_lockuser")
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE sys_user SET usermail=%s, userpwd=%s, errcnt=%s, lasttm=%s, datest=%s, dateed=%s, lockuser=%s
                    WHERE userid=%s
                """, [edit_usermail, edit_userpwd, edit_errcnt, edit_lasttm, edit_datest, edit_dateed, edit_lockuser, edit_userid])
            msg = "User updated successfully."
        # Add user (should not be used if using user_ins page, but kept for completeness)
        else:
            usermail = request.POST.get("usermail")
            userpwd = request.POST.get("userpwd")
            if not usermail or not userpwd:
                errmsg = "Email and password are required."
            else:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM sys_user WHERE usermail = %s", [usermail])
                    if cursor.fetchone()[0] > 0:
                        errmsg = "User already exists."
                    else:
                        cursor.execute(
                            "INSERT INTO sys_user (usermail, userpwd, errcnt, lasttm, datest, dateed, lockuser) VALUES (%s, %s, 0, NULL, NULL, NULL, 'N')",
                            [usermail, userpwd]
                        )
                        msg = "User added successfully."
    with connection.cursor() as cursor:
        cursor.execute("SELECT userid, usermail, userpwd, errcnt, lasttm, datest, dateed, lockuser FROM sys_user")
        users = cursor.fetchall()
    return render(request, "users.html", {"users": users, "errmsg": errmsg, "msg": msg})

def user_ins(request: HttpRequest):
    # Only allow access if logged in
    if not request.session.get("userid"):
        return redirect("homec")  # or use your login page name

    msg = errmsg = None
    if request.method == "POST":
        # why do i have to declare all of them one by one?
        # i should be able to use a loop to get all the values
        # but i don't want to use a loop because it will be less readable
        # is coding style more important than readability?
        # i don't think so
        # is django dying?
        # i don't think so
        usermail = request.POST.get("usermail")
        userpwd = request.POST.get("userpwd")
        errcnt = request.POST.get("errcnt") or 0
        lasttm = request.POST.get("lasttm") or None
        datest = request.POST.get("datest") or None
        dateed = request.POST.get("dateed") or None
        lockuser = request.POST.get("lockuser") or "N"
        if not usermail or not userpwd:
            errmsg = "Email and password are required."
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM sys_user WHERE usermail = %s", [usermail])
                if cursor.fetchone()[0] > 0:
                    errmsg = "User already exists."
                else:
                    cursor.execute(
                        "INSERT INTO sys_user (usermail, userpwd, errcnt, lasttm, datest, dateed, lockuser) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        [usermail, userpwd, errcnt, lasttm, datest, dateed, lockuser]
                    )
                    msg = "User added successfully."
    return render(request, "user_ins.html", {"errmsg": errmsg, "msg": msg})

def user_edit(request: HttpRequest):
    if request.method == "GET":
        userid = request.GET.get("userid")
        if not userid:
            return redirect("users")

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sys_user WHERE userid = %s", [userid])
            user = cursor.fetchone()
            if not user:
                return redirect("users")
        
        return render(request, "edit_user.html", {"user": user})

    elif request.method == "POST":
        userid = request.POST.get("userid")
        if request.POST.get("delete_user"):
            # Delete user and redirect
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sys_user WHERE userid = %s", [userid])
            return redirect("users")
        else:
            # Update user
            usermail = request.POST.get("usermail")
            userpwd = request.POST.get("userpwd")
            errcnt = request.POST.get("errcnt", 0)
            lasttm = request.POST.get("lasttm") # Consider updating this to current time on edit, or remove if not editable
            datest = request.POST.get("datest")
            dateed = request.POST.get("dateed")
            lockuser = request.POST.get("lockuser", "N")

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE sys_user SET 
                        usermail = %s,
                        userpwd = %s,
                        errcnt = %s,
                        lasttm = %s,
                        datest = %s,
                        dateed = %s,
                        lockuser = %s
                    WHERE userid = %s
                """, [usermail, userpwd, errcnt, lasttm, datest, dateed, lockuser, userid])
            
            return redirect("users")

 