from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
import dill as pickle
import os, datetime

app = Flask(__name__)
#
# flask page functions
@app.route('/')
def main():
    return redirect('/index')
    
@app.route('/rankings')
def rankings():
    return render_template('rankings.html')


@app.route('/index', methods=['GET', 'POST'])
def index(): 

    relpath = '/Users/dbricare/Documents/Programming/CollegeOutcomesWeb/'

    def knnestimate(df, earn, tuition, nn=5):
        # df must have column order: institution, state, tuition, 50% earnings, 75% earnings, 90% earnings
        cols = df.columns
        xtest = np.array([tuition, earn]).reshape(1,-1)
        dfs = {}
        for percent, col in zip(['50%', '25%', '10%'], cols[3:]):
            X = df[['PublicPrivate', col]]
            with open(relpath+col+'.pkl', 'rb') as f:
                knn = pickle.load(f)
            _ , idxs = knn.kneighbors(xtest, nn)
            outcols = list(cols[:3])
            outcols.append(col)
            dfres = df[outcols].iloc[idxs.flatten()].copy()
            dfres.sort_values(cols[2], inplace=True, ascending=True)
            dfres.columns = ['Institution', 'State', 'Tutition ($)', 'Earnings ($)']
            testhtml = dfres.to_html(index=False, classes='table table-condensed table-striped table-bordered')
            testhtml = testhtml.replace('border="1" ', '').replace('class="dataframe ', 'class="')
            testhtml = testhtml.replace(' style="text-align: right;"', '')
            dfs[percent] = testhtml
        return dfs

    data = pd.read_csv(relpath+'EarningsTuition.csv', sep=',')

    if request.method=='GET':
        earntarget = 60000
        tuitiontarget = 10000
        nn = 5
    else:
        earntarget = int(request.form['earnings'])
        tuitiontarget = int(request.form['tuition'])
        nn = int(request.form['viewsize'])

    # run function to get tables
    dfs = knnestimate(data, earntarget, tuitiontarget, nn)

    # modification date
    t = os.path.getmtime(relpath+'app.py')
    modt=datetime.date.fromtimestamp(t)
    updated = modt.strftime('%B %e, %Y')

    return render_template('index.html', updated=updated, dfs=dfs,
                            earnings=earntarget, tuition=tuitiontarget, viewsize=nn)

if __name__ == "__main__":
    app.run(debug=True, port=33507)
