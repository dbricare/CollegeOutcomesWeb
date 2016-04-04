from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
import os, datetime

# load data
# df must have column order: institution, state, tuition, 50% earnings, 75% earnings, 90% earnings
df = pd.read_csv('EarningsTuition.csv', sep=',', encoding='utf-8')
# instantiate app
app = Flask(__name__)

# other functions
def moddate():
    t = os.path.getmtime('app.py')
    modt=datetime.date.fromtimestamp(t)
    return 'Last updated: '+modt.strftime('%B %e, %Y')

def nncalc(outcols, earn, tuition, nn):
    # sort by minimal distance between target and each column and output those indices
    X = df[outcols].copy()
    X['euclid'] = np.sqrt(np.square(X['PublicPrivate']-tuition) + np.square(X[outcols[-1]]-earn))
    X.sort_values('euclid', inplace=True, ascending=True)
    X.drop('euclid', axis=1, inplace=True)
    return X.iloc[:nn]

# flask page functions
@app.route('/')
def main():
    return redirect('/earncost')
    
@app.route('/rankings')
def rankings():
    # modification date
    updated = moddate()
    return render_template('rankings.html', updated=updated)

@app.route('/earncost', methods=['GET', 'POST'])
def earncost(): 
    if request.method=='GET':
        earntarget = 60000
        tuitiontarget = 10000
        nn = 5
    else:
        earntarget = int(request.form['earnings'])
        tuitiontarget = int(request.form['tuition'])
        nn = int(request.form['viewsize'])
    # run function to get tables
    cols = df.columns
    dfs = {}
    for percent, col in zip(['50%', '25%', '10%'], cols[3:]):
        outcols = list(cols[:3])
        outcols.append(col) # inst, state, tuition, earnings
        dfres = nncalc(outcols, earntarget, tuitiontarget, nn)
        dfres.columns = ['Institution', 'State', 'Annual Tuition', 'Reported Earnings']
        dfres.sort_values('Annual Tuition', inplace=True, ascending=True)
        with pd.option_context('max_colwidth', -1):
            testhtml = dfres.to_html(index=False, escape=False, 
            classes='table table-condensed table-striped table-bordered')
        testhtml = testhtml.replace('border="1" ', '').replace('class="dataframe ', 'class="')
        testhtml = testhtml.replace(' style="text-align: right;"', '').replace('&', '&amp;')
        dfs[percent] = testhtml

    # modification date
    updated = moddate()

    return render_template('earncost.html', updated=updated, dfs=dfs,
                            earnings=earntarget, tuition=tuitiontarget, viewsize=nn)

if __name__ == "__main__":
    app.run(debug=True, port=33507)
