import ezdxf
import cloudconvert
import math
import os
import datetime
# from ezdxf.addons.drawing import matplotlib
# from ezdxf import recover
from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
cors = CORS(app)

minX = 1000000
maxX = -1000000
minY = 1000000
maxY = -1000000
radius = 0


app.config['CORS_HEADERS'] = 'Content-Type'

app.config['IMAGE_UPLOADS'] = "/var/www/html/cuttingPy/uploads"


@app.route("/dxf", methods=["POST", "GET"])
@cross_origin()
def hello_world():
    global minX, maxX, minY, maxY, radius
    image = request.files["photo"]
    imageextension = os.path.splitext(image.filename)
    current_time = datetime.datetime.now()
    current_time = str(current_time)
    current_time = current_time.replace(" ", "")
    image.filename = image.filename.replace(" ", "")
    imageFilename = imageextension[0].replace(" ", "")
    image.save(os.path.join(
        app.config['IMAGE_UPLOADS'], current_time + image.filename))
    
    link = f"https://thecuttingcenter.com/cuttingPy/uploads/{current_time+image.filename}"
    
    # # Exception handling left out for compactness:
    # doc, auditor = recover.readfile(
    #     app.config['IMAGE_UPLOADS']+"/" + current_time + image.filename)
    # if not auditor.has_errors:
    #     matplotlib.qsave(doc.modelspace(), current_time + image.filename+'.png')

    if imageextension[1] == ".dwg":
        cloudconvert.configure(api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMGJjZTEwZDYzMzYxZDMwZGQxM2ZlMDk0ZjE3YTRjMmMyZTY3NTE3NWMyYTg0ZjE5Y2NjNmU4NTdkYzM4NGI4NTU4NjQ1MWNjMTEzMDE2MGYiLCJpYXQiOjE2OTk2MDY1NjkuMDM2MzE1LCJuYmYiOjE2OTk2MDY1NjkuMDM2MzE2LCJleHAiOjQ4NTUyODAxNjkuMDMxODMsInN1YiI6IjY0NjIxMTg5Iiwic2NvcGVzIjpbInVzZXIucmVhZCIsInVzZXIud3JpdGUiLCJ0YXNrLnJlYWQiLCJ0YXNrLndyaXRlIiwid2ViaG9vay5yZWFkIiwid2ViaG9vay53cml0ZSIsInByZXNldC5yZWFkIiwicHJlc2V0LndyaXRlIl19.eVKO60ovZK6-zxGJdrttJG0ZJl7MkXl6dh33ZMnQxac14xdIA-iwXdPpAAUUngI36l0-Hojd9aJbH_SOs0ZHptkwoIkXvAXhnwpfoBc9jX9FTfl6swjuQbWCW8o5OyOTMgkSiDiUAr5lxeKmy-ENTX1bCDIzfVdun3hPIP-OK8V3COTpksg-97snI5yrl-ngR30ggf-LqzBHABmYshmGNN3wRwXPMxdXHM4PUIIizYkLq_HUcDYPmKV_jMt4gWJYvLKdvsyJqN8A-o9W94kJE2UICNJYWuJsyonu7DYqpf1GbJ7glw0IsjY13Cb4TNLwQjPLoKJ1ZWMiMij8Fca63-66jDmW73euUlPyM8A6119ZptuzlINUZaJOmwN2auMuuc2B3aUXT4bjhYQLt_gGfnIDg4Ijek1cOFcaqjQt1tCb2ifxUpd5_POrvSTuEYT64zXq8r-C5svZ4qvP_BWypf5pcmRlYWQmCBWQ054DNcK_ssC546YjGr6iCV_x2hO9OoSrlplAt9O_kUfWXYEZ9v7SU2BSOYceUmxfSnJpZQaYoRMXGyx1CnPKVRM3HWIHFkx81DmpNV7fOOP9fKT22re77DXalasv42aD48OrepRgoHKwptkEAqZxRmxpN3zLgqWffQIrVk5IZsIBuKaL_MuJF8anLN3XRO1XCTtzEyQ', sandbox=False)
        job = cloudconvert.Job.create(payload={
            "tasks": {
                'import-my-file': {
                    'operation': 'import/url',
                    'url': link
                },
                'convert-my-file': {
                    'operation': 'convert',
                    'input': 'import-my-file',
                    'output_format': 'dxf',
                    'some_other_option': 'value'
                },
                'export-my-file': {
                    'operation': 'export/url',
                    'input': 'convert-my-file'
                }
            }
        })
        job = cloudconvert.Job.wait(id=job['id'])
        for task in job["tasks"]:
            if task.get("name") == "export-my-file" and task.get("status") == "finished":
                export_task = task
        # exported_url_task_id = job['id']
        # res = cloudconvert.Job.wait(id=job['id'])
        # print("Response: ", job)
        # res = cloudconvert.Task.wait(
        #     id=exported_url_task_id)  # Wait for job completion
        file = export_task.get("result").get("files")[0]
        print(file)
        cloudconvert.download(
            filename=file['filename'], url=file['url'])
        dxf = ezdxf.readfile(
            "/var/www/html/cuttingPy/"+current_time + imageFilename+".dxf")
    else:
        dxf = ezdxf.readfile(
            app.config['IMAGE_UPLOADS']+"/"+current_time + image.filename)
    print(app.config['IMAGE_UPLOADS']+"/"+current_time + image.filename,dxf)
    msp = dxf.modelspace()
    totaldl = process_modelspace(msp, dxf)
    print("Total DL: ",totaldl)
    length = maxX-minX
    width = maxY-minY
    print(length, width)
    if radius > length:
        length = radius
    if radius > width:
        width = radius

    minX = 1000000
    maxX = -1000000
    minY = 1000000
    maxY = -1000000
    radius = 0
    # print(maxln)
    # print(maxlines[0:10])
    data = {
        "circumference": totaldl/2,
        "height": round(width),
        "width": round(length),
        "design_link": link
    }
    return jsonify(data)


def findWidthLength(line, length):
    global minX, maxX, minY, maxY
    length = math.sqrt((line[0][0]-line[1][0])**2 + (line[0][1]-line[1][1])**2)
    if length > 10:
        if line[0][0] < minX:
            minX = line[0][0]
        if line[1][0] < minX:
            minX = line[1][0]
        if line[0][0] > maxX:
            maxX = line[0][0]
        if line[1][0] > maxX:
            maxX = line[1][0]

        if line[0][1] < minY:
            minY = line[0][1]
        if line[1][1] < minY:
            minY = line[1][1]
        if line[0][1] > maxY:
            maxY = line[0][1]
        if line[1][1] > maxY:
            maxY = line[1][1]


def process_lwpolyline(e):
    lines = []
    dl_len = []
    points = []
    dl = 0
    line_end = (0, 0)
    if e.dxftype() == 'LWPOLYLINE':
        points = e.get_points()
    if e.dxftype() == 'POLYLINE':
        points = e.points()

    for i, point in enumerate(points):
        if i == 0:
            lastpoint = point
            firstpoint=point    
            continue
        # I ignored a arc_shape line and force it to be a straight one in here
        # print(points)
        line_start = (lastpoint[0], lastpoint[1])
        line_end = (point[0], point[1]) 
        line = [ line_start, line_end]

        # print(line)
        lines.append(line)
        length = math.sqrt((line_start[0]-line_end[0])
                           ** 2 + (line_start[1]-line_end[1])**2)
        dl = dl + length
        findWidthLength(line, length)
        lastpoint = point
        
    line_start=firstpoint
    length= math.sqrt((line_start[0]-line_end[0])**2 + (line_start[1]-line_end[1])**2)
    dl = dl + length

    if hasattr(e, 'virtual_entities'):
        for e2 in e.virtual_entities():
            dtype = e2.dxftype()
            if dtype == 'LINE':
                line = [e2.dxf.start, e2.dxf.end]
                length = math.sqrt(
                    (e2.dxf.start[0]-e2.dxf.end[0])**2 + (e2.dxf.start[1]-e2.dxf.end[1])**2)
                lines.append(line)
                dl = dl + length
                line_start = (e2.dxf.start[0], e2.dxf.start[1])
                line_end = (e2.dxf.end[0], e2.dxf.end[1])
                line = [line_start, line_end]
                findWidthLength(line, length)
            elif dtype == 'LWPOLYLINE':
                dl += process_lwpolyline(e2)
    # print(dl)
    return dl


# def process_modelspace(msp, dxf):
#     global radius
#     longitud_total = 0
#     for e in msp:
#         # print(e.dxftype())
#         if e.dxftype() == 'LINE':
#             # print(e.dxf.start)
#             dl = math.sqrt((e.dxf.start[0]-e.dxf.end[0])**2 + (e.dxf.start[1] -
#                                                                e.dxf.end[1])**2)
#             longitud_total = longitud_total + dl

#             line_start = (e.dxf.start[0], e.dxf.start[1])
#             line_end = (e.dxf.end[0], e.dxf.end[1])
#             line = [line_start, line_end]
#             findWidthLength(line, dl)

#             # maxlines.append(dl)
#         elif e.dxftype() == 'CIRCLE':
#             dc = 2*math.pi*e.dxf.radius
#             longitud_total = longitud_total + dc
#             radius = e.dxf.radius
#         elif e.dxftype() == 'SPLINE':
#             print("E: ", e)
#             puntos = e.control_points
#             # print(e.dxftype())
#             for i in range(len(puntos)-1):
#                 ds = math.sqrt((puntos[i][0]-puntos[i+1][0])**2 + (puntos[i][1] -
#                                                                    puntos[i+1][1])**2)
#                 longitud_total = longitud_total + ds
#                 line_start = (puntos[i][0], puntos[i][1])
#                 line_end = (puntos[i+1][0], puntos[i+1][1])
#                 line = [line_start, line_end]
#                 findWidthLength(line, ds)
#         elif e.dxftype() == 'LWPOLYLINE':
#             longitud_total = longitud_total + process_lwpolyline(e)*0.5
#         elif e.dxftype() == 'POLYLINE':
#             longitud_total = longitud_total + process_lwpolyline(e)*0.5
#         elif e.dxftype() == 'INSERT':
#             block = dxf.blocks[e.dxf.name]
#             longitud_total = longitud_total + process_modelspace(block, dxf)
#     return longitud_total

def process_modelspace(msp, dxf):
    global radius
    longitud_total = 0
    for e in msp:
        # print(e.dxftype())
        if e.dxftype() == 'LINE':
            # print(e.dxf.start)
            dl = math.sqrt((e.dxf.start[0]-e.dxf.end[0])**2 + (e.dxf.start[1] -
                                                               e.dxf.end[1])**2)
            longitud_total = longitud_total + dl

            line_start = (e.dxf.start[0], e.dxf.start[1])
            line_end = (e.dxf.end[0], e.dxf.end[1])
            line = [line_start, line_end]
            findWidthLength(line, dl)

            # maxlines.append(dl)
        elif e.dxftype() == 'CIRCLE':
            dc = 2*math.pi*e.dxf.radius
            longitud_total = longitud_total + dc
            radius = e.dxf.radius
        elif e.dxftype() == 'SPLINE':
            puntos = e.get_control_points()
            # print(e.dxftype())
            for i in range(len(puntos)-1):
                ds = math.sqrt((puntos[i][0]-puntos[i+1][0])**2 + (puntos[i][1] -
                                                                   puntos[i+1][1])**2)
                longitud_total = longitud_total + ds
                line_start = (puntos[i][0], puntos[i][1])
                line_end = (puntos[i+1][0], puntos[i+1][1])
                line = [line_start, line_end]
                findWidthLength(line, ds)
        elif e.dxftype() == 'LWPOLYLINE':
            longitud_total = longitud_total + process_lwpolyline(e)
        elif e.dxftype() == 'POLYLINE':
            longitud_total = longitud_total + process_lwpolyline(e)
        elif e.dxftype() == 'INSERT':
            block = dxf.blocks[e.dxf.name]
            longitud_total = longitud_total + process_modelspace(block, dxf)
    return longitud_total


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=4060)
