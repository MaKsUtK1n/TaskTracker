from sqlite3 import connect
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from uvicorn import run
from time import time, ctime



con = connect("db.db", isolation_level=None, check_same_thread=False)
cursor = con.cursor()
app = FastAPI()
color_schemas = {0: ('#fff','#28a745','#28a745'),
                 1: ("#00a9a5", "#0b5351", "#092327"),
                 3: ("#edf6f9", "#83c5be", "#006d77"),
                 2: ("#f8f7ff", "#b8b8ff", "#9381ff"),
                 4: ("#edf2f4", "#8d99ae", "#2b2d42")}



@app.get("/l")
async def mcheck(request: Request):
    fr = request.query_params
    cursor.execute("SELECT * FROM users WHERE login=?", (fr['login'],))
    dt = cursor.fetchone()
    if dt is None:
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?)", (None, fr['login'], fr['password'], 0, None))
        con.commit()
        res = RedirectResponse("/tasks")
        res.set_cookie("l", fr['login'])
        res.set_cookie("p", fr['password'])
    elif dt[2] != fr['password']:
        res = HTMLResponse(open("index.html", encoding="utf-8").read().replace("%ERR%", "Пароль неверный"))
    elif dt[2] == fr['password']:
        res = RedirectResponse("/tasks")
        res.set_cookie("l", fr['login'])
        res.set_cookie("p", fr['password'])
    return res
@app.get("/")
async def main(request: Request):
    if request.cookies == {} or ("l" in request.cookies and "p" in request.cookies):
        res = HTMLResponse(open("index.html", encoding="utf-8").read().replace("%ERR%", ""))
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    cursor.execute("SELECT * FROM users WHERE login=? and password=?", (request.cookies['l'], request.cookies['p']))
    dt = cursor.fetchone()
    if dt is None:
        res = HTMLResponse(open("index.html", encoding="utf-8").read().replace("%ERR%", ""))
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    else:
        return RedirectResponse("/tasks")


@app.get("/ct")
async def crdasd(request: Request):
    if request.cookies == {} or ("l" not in request.cookies and "p" not in request.cookies):
        return RedirectResponse("/")
    cursor.execute("SELECT * FROM users WHERE login=?", (request.cookies['l'],))
    dt = cursor.fetchone()
    if dt is None or dt[2] != request.cookies['p']:
        res = RedirectResponse("/")
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    fr = request.query_params
    cursor.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?)", (None, dt[0], fr['shortname'], fr['desc'], "", fr['expires_in_date'] + fr['expires_in_min'], "active", ctime(time())[11:-5]))
    con.commit()
    return RedirectResponse("/tasks")
@app.get("/CreateTask")
async def CreateTask(request: Request):
    if request.cookies == {} or ("l" not in request.cookies and "p" not in request.cookies):
        return RedirectResponse("/")
    cursor.execute("SELECT * FROM users WHERE login=?", (request.cookies['l'],))
    dt = cursor.fetchone()
    if dt is None or dt[2] != request.cookies['p']:
        res = RedirectResponse("/")
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    return HTMLResponse(open("create_task.html", encoding="utf-8").read().replace("[0]", color_schemas[dt[3]][0]).replace("[1]", color_schemas[dt[3]][1]).replace("[2]", color_schemas[dt[3]][2]))


@app.get("/tasks")
async def tasks(request: Request):
    if request.cookies == {} or ("l" not in request.cookies and "p" not in request.cookies):
        return RedirectResponse("/")
    cursor.execute("SELECT * FROM users WHERE login=?", (request.cookies['l'],))
    dt = cursor.fetchone()
    if dt is None or dt[2] != request.cookies['p']:
        res = RedirectResponse("/")
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    cursor.execute("SELECT * FROM tasks WHERE cid=? or instr(shared_users, ?)", (dt[0], dt[0]))
    st = cursor.fetchall()
    taskshtml = ''
    for task in st:
        taskshtml += f'''
        <button class="task" onclick="window.location.href = '/tasks/{task[0]}'">
                <div style="float: right; width: 95%;">
                    <b>{task[2]}</b> <br>
                    <a style="opacity: 0.5;">{task[3]}</a>
                </div>
                <div id="{task[6]}" class="status"></div>
            </button> <br> <br>'''        
    return HTMLResponse(open("tasks.html", encoding="utf-8").read().replace("%TASKS%", taskshtml).replace("[0]", color_schemas[dt[3]][0]).replace("[1]", color_schemas[dt[3]][1]).replace("[2]", color_schemas[dt[3]][2]))


@app.get("/settings")
async def settings(request: Request):
    if request.cookies == {} or ("l" not in request.cookies and "p" not in request.cookies):
        return RedirectResponse("/")
    cursor.execute("SELECT * FROM users WHERE login=?", (request.cookies['l'],))
    dt = cursor.fetchone()
    if dt is None or dt[2] != request.cookies['p']:
        res = RedirectResponse("/")
        for cookie in request.cookies:
            res.delete_cookie(cookie)
        return res
    return HTMLResponse(open("settings.html", encoding="utf-8").read().replace("[0]", color_schemas[dt[3]][0]).replace("[1]", color_schemas[dt[3]][1]).replace("[2]", color_schemas[dt[3]][2]))


run(app, host="0.0.0.0", port=443)