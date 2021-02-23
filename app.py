### Import Modules ###
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

import plotly
import plotly.graph_objs as go

import pandas as pd
import json
import sqlalchemy as db
import joblib


# importing Data Frame that has been preprocessed
df_preprocessed = pd.read_csv('property_sales_canberra_preprocessed.csv')
print(df_preprocessed.head(10))  # checking purpose

sqlengine = db.create_engine('mysql+pymysql://root:12345@localhost:3306/property_sales_canberra_preprocessed100')
dbConnection = sqlengine.connect()
engine = sqlengine.raw_connection()
cursor = engine.cursor()

# Currently, this project uses data from csv file, uncomment syntax below to use data from the sql database
# df_preprocessed = pd.read_sql("SELECT * FROM property_sales_canberra_preprocessed100.mytable", dbConnection)


app = Flask(__name__)  # initialize flask object


###  Diagrams  ###
def scatter_plot(cat_x, cat_y, hue):

    data = []

    for val in df_preprocessed[hue].unique():
        scatt = go.Scatter(
            x=df_preprocessed[df_preprocessed[hue] == val][cat_x],
            y=df_preprocessed[df_preprocessed[hue] == val][cat_y],
            mode='markers',
            name=str(val)
        )
        data.append(scatt)

    layout = go.Layout(
        title='Scatter',
        title_x=0.5,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y)
    )

    result = {"data": data, "layout": layout}
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/scatter', methods=['POST', 'GET'])
def scatter():

    cat_x = request.args.get('x_value_html')
    cat_y = request.args.get('y_value_html')
    hue = request.args.get('hue_value_html')
    plot = scatter_plot(cat_x, cat_y, hue)

    return render_template(
        'scatter_result.html',
        plot=plot,
        title='Scatter'
    )


def histogram_plot(cat_x, cat_est, hue):

    data = []

    for val in df_preprocessed[hue].unique():
        hist = go.Histogram(
            x=df_preprocessed[df_preprocessed[hue] == val][cat_x],
            y=df_preprocessed[df_preprocessed[hue] == val]["price"],
            histfunc=cat_est,
            name=str(val)
        )
        data.append(hist)

    layout = go.Layout(
        title='Histogram',
        xaxis=dict(title=cat_x),
        yaxis=dict(title='unit'),
        boxmode='group'
    )

    result = {'data': data, 'layout': layout}
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/histogram', methods=['POST', 'GET'])
def histogram():

    cat_x = request.args.get('x_value_html')
    cat_est = request.args.get('estimator_value_html')
    hue = request.args.get('hue_value_html')
    plot = histogram_plot(cat_x, cat_est, hue)

    return render_template(
        'histogram_result.html',
        plot=plot,
        title='Histogram'
    )


###  Basic Navigation  ###
@app.route('/')
@app.route('/home', methods=['POST', 'GET'])
def home():
    return render_template('predict.html')


@app.route('/scatter_site', methods=['POST', 'GET'])
def scatter_site():
    return render_template('scatter_result.html', title='Scatter')


@app.route('/histogram_site', methods=['POST', 'GET'])
def histogram_site():
    return render_template('histogram_result.html', title='Histogram')


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html', title='Login')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About')

@app.route('/conclusion', methods=['GET'])
def conclusion():
    return render_template('conclusion.html', title='Conclusion')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    return render_template('predict.html', title='Predict')


@app.route('/result', methods=['POST', 'GET'])
def result():

    if request.method == 'POST':
        input_form = request.form

        df = pd.DataFrame({
            'parking': [input_form['parking']],
            'bathrooms': [input_form['bathrooms']],
            'bedrooms': [input_form['bedrooms']],
            'suburb': [input_form['suburb']],
            'propertyType': [input_form['propertyType']]
        })

        price = round(model.predict(df)[0], 3)
        price = '{:,}'.format(price)
        return render_template('result.html', title='Result', data=input_form, prediction=price)


@app.route('/data', methods=['POST', 'GET'])
def data():

    sqlengine = db.create_engine('mysql+pymysql://root:12345@localhost:3306/property_sales_canberra_preprocessed100')
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    cursor.execute('SET @r = 0;')
    cursor.execute(
        'SELECT * FROM (SELECT *, (@r := @r + 1) AS r_id FROM property_sales_canberra_preprocessed100.mytable) AS tmp ORDER BY r_id DESC LIMIT 10;')
    data = cursor.fetchall()
    return render_template('table_updated.html', data=data, title='Data')


@app.route('/update', methods=['POST', 'GET'])
def update():

    if request.method == 'POST':

        sqlengine = db.create_engine('mysql+pymysql://root:12345@localhost:3306/property_sales_canberra_preprocessed100')
        engine = sqlengine.raw_connection()
        cursor = engine.cursor()

        input_form = request.form

        parking_ = input_form['parking']
        bathrooms_ = input_form['bathrooms']
        bedrooms_ = input_form['bedrooms']
        suburb_ = input_form['suburb']
        propertyType_ = input_form['propertyType']
        price_ = input_form['price']

        monthsold_ = int(input_form['monthsold'])

        if (monthsold_ >= 1) & (monthsold_ <= 3):
            quarters_ = 'q1'
        elif (monthsold_ >= 4) & (monthsold_ <= 6):
            quarters_ = 'q2'
        elif (monthsold_ >= 7) & (monthsold_ <= 9):
            quarters_ = 'q3'
        else:
            quarters_ = 'q4'

        if (monthsold_ >= 3) & (monthsold_ <= 5):
            seasons_ = 'spring'
        elif (monthsold_ >= 6) & (monthsold_ <= 8):
            seasons_ = 'summer'
        elif (monthsold_ >= 9) & (monthsold_ <= 11):
            seasons_ = 'fall'
        else:
            seasons_ = 'winter'

        data = { "price" : [price_], "parking" : [parking_], "bathrooms" : [bathrooms_], "bedrooms" : [bedrooms_], "suburb" : [suburb_], 
                 "propertyType" : [propertyType_], "quarters" : [quarters_], "seasons" : [seasons_]
               }

        new_df = pd.DataFrame.from_dict(data)
        new_df.to_sql('mytable', con=dbConnection, if_exists='append', index=False)

        cursor.execute('SET @r = 0;')
        cursor.execute('SELECT * FROM (SELECT *, (@r := @r + 1) AS r_id FROM property_sales_canberra_preprocessed100.mytable) AS tmp ORDER BY r_id DESC LIMIT 10;')
        data = cursor.fetchall()

        return render_template('table_updated.html', title="Updated Table", data=data)


if __name__ == '__main__':

    model = joblib.load('gbr_twlo_final')
    app.run(debug=True, port=1500)
