from flask import Flask, Response, render_template

app = Flask(__name__)

class RealtimeString:
    def __init__(self):
        self.counter = 0
        self.realtime_string = "MARDTA"
    
    def generate_string(self):
        self.realtime_string += "Real-time string\n"
        self.counter += 1
        if self.counter >= 10:
            self.realtime_string = ""
            self.counter = 0
        return self.realtime_string

realtime_string = RealtimeString()

@app.route('/realtime')
def realtime():
    return Response(
        realtime_string.generate_string(),
        mimetype='text/plain'
    )

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)