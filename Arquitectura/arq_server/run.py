from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


quarks = [{'appName': 'up', 'charge': '+2/3'},
          {'name': 'down', 'charge': '-1/3'},
          {'name': 'charm', 'charge': '+2/3'},
          {'name': 'strange', 'charge': '-1/3'}]

apps = {
    "cleanDirectory":{"init":"clase"}
}

@app.route('/applications/<string:appName>', methods=['GET'])
def returnOne(appName):
    if appName in apps:
        return jsonify(apps[appName])

@app.route('/applications/<string:appName>', methods=['POST'])
def addOne(appName):
    new_quark = request.get_json()
    print(new_quark)
    quarks.append(new_quark)
    return jsonify({'quarks' : quarks})

if __name__ == "__main__":
    app.run(debug=True)