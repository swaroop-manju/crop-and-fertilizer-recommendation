from flask import Flask, render_template, request
import pickle
import math
import csv  # using Python module

# Running the flask app
app = Flask(__name__)

# load model using pickle
model = pickle.load(open('model.pkl', 'rb'))


# n,p,k,ph fetching
def fetch(vari):
    f = open('fetch (2).csv', 'r')  # use binary mode if on MS windows
    d = [i for i in csv.reader(f)]  # use list comprehension to read from file
    f.close()  # close file
    coords = [(float(d[i][0]), float(d[i][1])) for i in range(1, len(d))]
    t = (coords.index(closest_coord(coords, vari)) + 1)
    ph = d[t][2]
    n = d[t][3]
    p = d[t][4]
    k = d[t][5]
    return (list(map(float, [ph[:-5], n[:-2], p[:-2], k[:-2]])))


def closest_coord(coords, vari):
    closest = coords[0]
    for c in coords:
        if distance(c, vari) < distance(closest, vari):
            closest = c
    return closest


def distance(co1, co2):
    return math.sqrt(pow(abs(co1[0] - co2[0]), 2) + pow(abs(co1[1] - co2[1]), 2))

def fertiliser(pred, test):
    f = open('fertilizer.csv', 'r')  # use binary mode if on MS windows
    d = [i for i in csv.reader(f)]  # use list comprehension to read from file
    f.close()  # close file
    for j in range(0, len(d)):
        if d[j][1] == pred:
            h = j
    req = [d[h][i] for i in range(2, 5)]
    pres = test[:3]
    recom = measure(req, pres)
    return (req, recom)


def measure(req, pres):
    lib = {'Nitrogen': 'medium', 'Phosphorus': 'medium', 'Potassium': 'medium'}
    tlist = []
    for i in range(len(req)):
        if int(req[i]) - int(pres[i]) > 10:
            temp = 'more'
        elif int(req[i]) - int(pres[i]) <= 4:
            temp = 'not needed'
        else:
            temp = 'medium'
        tlist.append(temp)
    return (tlist)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict_crop():
    data1 = float(request.form.get('lon'))
    data2 = float(request.form.get('lat'))
    temp =  float(request.form.get('tem'))
    humid = float(request.form.get('hum'))
    mois =  float(request.form.get('moi'))
    vari = (data1, data2)
    lst = fetch(vari)
    lst.extend([temp, humid, mois])  # temp,humid,moisture
    ph = lst[0]
    test = lst[1:]
    test.insert(5, ph)
    pred = model.predict([test])

    prin = (fertiliser(pred, test))
    req = prin[0]
    recom = prin[1]
    output = (" The suitable crop is {} with present soil parameters N={},P={},K={},pH={}\n The required amount of nutrients are \n N={},P={},K={}\n Therefore, application of\n Nitrogen: {}\n Phosphorus: {}\n Potassium: {}\n".format(
            pred[0], test[0], test[1], test[2], test[5], req[0], req[1], req[2], recom[0], recom[1], recom[2]))
    return render_template('index.html',result=output)


if __name__ == '__main__':
    app.run(debug=True)