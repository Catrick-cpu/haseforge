from flask import Flask, request, render_template_string, redirect, url_for, session
from functools import wraps
import math as m
import time
from colorama import Fore
from pyfiglet import Figlet

f = Figlet(font="slant")


def create_server(core):

    app = Flask(__name__)
    app.secret_key = "§=/AFoasfu8738"

    PASSWORD = "roboterarm"

    log_buffer = []

    def log(msg):
        print(msg)
        log_buffer.append(msg)
        if len(log_buffer) > 100:
            log_buffer.pop(0)

    # ================= LOGIN =================
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function

    # ================= INIT LOG =================
    log(Fore.RED + f.renderText("Roboterarm Server"))

    # ================= HOME HTML =================
    HTML = """<!DOCTYPE html>
    <html lang="de">
    <head>
    <meta charset="UTF-8">
    <title>Roboterarm Steuerung</title>
    <style>
    body {font-family: Arial; background:#f0f0f0; display:flex; flex-direction:column; align-items:center; padding:30px;}
    nav a {margin:0 10px; color:#4CAF50; text-decoration:none;}
    form {background:#fff; padding:20px; border-radius:10px;}
    pre {background:#222; color:#0f0; padding:10px;}
    table {border-collapse:collapse;}
    td, th {border:1px solid #333; padding:5px;}
    </style>
    </head>
    <body>

    <h2>Roboterarm Steuerung</h2>

    <nav>
        <a href="/">Home</a>
        <a href="/status">Status</a>
        <a href="/metrics">Metrics</a>
        <a href="/config">Config</a>
        <a href="/debug">Debug</a>
        <a href="/logout">Logout</a>
        <a href="/manual">Manual</a>
    </nav>

    <form method="post">
    <label>Start X <input name="sx" value="100"></label>
    <label>Start Z <input name="sz" value="300"></label>
    <label>Start Y <input name="sy" value="0"></label>

    <label>End X <input name="ex" value="400"></label>
    <label>End Z <input name="ez" value="600"></label>
    <label>End Y <input name="ey" value="90"></label>

    <label>Time <input name="time" value="5"></label>

    <input type="submit">
    </form>

    <h3>Daten</h3>
    {% if received %}
    <table>
    {% for k,v in received.items() %}
    <tr><td>{{k}}</td><td>{{v}}</td></tr>
    {% endfor %}
    </table>
    {% endif %}

    <pre>{{ output }}</pre>

    </body>
    </html>
    """

    # ================= EASING =================
    def ease_in_out(t):
        return 0.5 - 0.5 * m.cos(m.pi * t)

    # ================= ROUTES =================

    @app.route("/login", methods=["GET", "POST"])
    def login():
        msg = ""
        if request.method == "POST":
            if request.form.get("password") == PASSWORD:
                session["logged_in"] = True
                return redirect("/")
            msg = "Falsches Passwort"

        return f"""
        <h2>Login</h2>
        <form method="post">
        Passwort <input name="password">
        <button>Login</button>
        </form>
        <p style='color:red'>{msg}</p>
        """

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    # ================= MAIN CONTROL =================
    @app.route("/", methods=["GET", "POST"])
    @login_required
    def index():

        output = ""
        received = {}

        if request.method == "POST":
            try:
                sx = float(request.form["sx"])
                sz = float(request.form["sz"])
                sy = float(request.form["sy"])
                ex = float(request.form["ex"])
                ez = float(request.form["ez"])
                ey = float(request.form["ey"])
                total_time = float(request.form["time"])

                received = request.form.to_dict()

                steps_count = 50

                prev_theta1, prev_theta2 = core.calc_angles(sx, sz)
                prev_rot = sy

                total_delta_rot = ey - sy
                total_delta_theta1 = 0
                total_delta_theta2 = 0

                for i in range(1, steps_count + 1):
                    t = ease_in_out(i / steps_count)

                    xi = sx + t * (ex - sx)
                    zi = sz + t * (ez - sz)

                    theta1_i, theta2_i = core.calc_angles(xi, zi)

                    total_delta_theta1 += theta1_i - prev_theta1
                    total_delta_theta2 += theta2_i - prev_theta2

                    prev_theta1, prev_theta2 = theta1_i, theta2_i

                steps_m1 = int(abs(total_delta_rot) / 360 * core.STEPS_PER_ROUND)
                steps_m2 = int(abs(total_delta_theta1) / 360 * core.STEPS_PER_ROUND)
                steps_m3 = int(abs(total_delta_theta2) / 360 * core.STEPS_PER_ROUND)

                dir_m1 = total_delta_rot >= 0
                dir_m2 = total_delta_theta1 >= 0
                dir_m3 = total_delta_theta2 >= 0

                max_steps = max(steps_m1, steps_m2, steps_m3, 1)

                c1 = c2 = c3 = 0
                a1 = a2 = a3 = 0

                for s in range(max_steps):

                    a1 += steps_m1
                    if a1 >= max_steps:
                        core.step(core.M1_STEP, core.M1_DIR, dir_m1)
                        c1 += 1
                        a1 -= max_steps

                    a2 += steps_m2
                    if a2 >= max_steps:
                        core.step(core.M2_STEP, core.M2_DIR, dir_m2)
                        c2 += 1
                        a2 -= max_steps

                    a3 += steps_m3
                    if a3 >= max_steps:
                        core.step(core.M3_STEP, core.M3_DIR, dir_m3)
                        c3 += 1
                        a3 -= max_steps

                    output += f"M1={c1} M2={c2} M3={c3}\n"
                    time.sleep(total_time / max_steps)

                core.status["theta1"] = prev_theta1
                core.status["theta2"] = prev_theta2
                core.status["rot"] = prev_rot

                core.status["counter_m1"] = c1
                core.status["counter_m2"] = c2
                core.status["counter_m3"] = c3

            except Exception as e:
                output = str(e)

        return render_template_string(HTML, output=output, received=received)

    # ================= OTHER ROUTES =================

    @app.route("/status")
    @login_required
    def status():
        return core.status

    @app.route("/metrics")
    @login_required
    def metrics():
        return core.status

    @app.route("/config", methods=["GET", "POST"])
    @login_required
    def config():
        if request.method == "POST":
            core.L1 = float(request.form["L1"])
            core.L2 = float(request.form["L2"])
            core.STEPS_PER_ROUND = int(request.form["STEPS_PER_ROUND"])

        return f"""
        <form method='post'>
        L1 <input name='L1' value='{core.L1}'><br>
        L2 <input name='L2' value='{core.L2}'><br>
        Steps <input name='STEPS_PER_ROUND' value='{core.STEPS_PER_ROUND}'><br>
        <button>Save</button>
        </form>
        """

    @app.route("/debug")
    @login_required
    def debug():
        return "<br>".join(log_buffer)

    # ================= RETURN APP =================
    return app