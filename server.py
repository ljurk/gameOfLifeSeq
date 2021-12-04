from flask import Flask, render_template, request
from datetime import datetime
import numpy as np
import random

app = Flask(__name__)
COLS = 100
ROWS = 100

def update(cur):
    nxt = np.zeros((cur.shape[0], cur.shape[1]))

    for r, c in np.ndindex(cur.shape):
        num_alive = np.sum(cur[r-1:r+2, c-1:c+2]) - cur[r, c]

        col = 0
        if (cur[r, c] == 1 and 2 <= num_alive <= 3) or (cur[r, c] == 0 and num_alive == 3):
            nxt[r, c] = 1
            col = 1

        col = col if cur[r, c] == 1 else 0

    return nxt

def getPattern(rows, columns):
    tempArray = []
    for row in range(rows):
        tempArray.append([])
        for col in range(columns):
            tempArray[row].append(random.randrange(2))
    return np.array(tempArray)

pattern = getPattern(ROWS,COLS)

def getTable(row, col):
    out = '<table >'
    for i in range(row):
        out += "<tr>"
        for j in range(col):
            out += "<td "
            if pattern[i][j]:
                out += 'bgcolor="black"'
            else:
                out += 'bgcolor="white"'
            out += "</td>"
        out += "</tr>"
    out += '</table>'
    return out


@app.route("/",methods=['GET', 'POST'])
def hello_world():
    global pattern
    pattern = update(pattern)
    if request.method == 'POST':
        if 'new' in request.form:
            pattern = getPattern(ROWS,COLS)
            pass # unknown

    return render_template("index.html", text=str(datetime.now()), table = getTable(ROWS,COLS))

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
