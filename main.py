# Importing required functions
import os
import pandas as pd
from flask import render_template

# Root endpoint
normovane = ["n_lipid","n_saturated","n_sacharides","n_sugar","n_proteins","n_salt"]
attributes = ['lipid','saturated','sacharides','sugar','protein','salt']
name_sk = ["Tuk", "Nenásytené mastné kyseliny", "Sacharidy", "Cukry","Bielkoviny", "Soľ"]
hundred_grams = 100

def get_excel_sheets(file):
    """Returns map of respective sheet:excel_file couples."""
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    return {i:file for i in sheet_names}

def calc(file, sheet):
    """Calculates nutrition facts based on Excel file."""
    
    xl = pd.ExcelFile(file)
    df = xl.parse(sheet)
    sum_of_attributes = []
    x_hundred_grams = []

    for normed, item in zip(normovane, attributes):
        df[normed] = df[item] * df['weight'] / hundred_grams


    product_weight = df['weight'].sum()
    df['percentage'] = ((df['weight'] / product_weight) * 100)

    for i in normovane:
        sum_of_attributes.append(round(df[i].sum(), 1))
        x_hundred_grams.append(hundred_grams * df[i].sum() / product_weight)


    cdf = pd.DataFrame()
    cdf['name'] = pd.Series(attributes)
    cdf['sums of attributes'] = pd.Series(sum_of_attributes)
    cdf['per 100g'] = pd.Series(x_hundred_grams)
    cdf['name_sk'] = pd.Series(name_sk)

    temp_var = cdf
    temp_var = temp_var.set_index("name")

    lipid = float(temp_var.loc['lipid', 'per 100g'])
    sacharid = float(temp_var.loc['sacharides', 'per 100g'])
    protein = float(temp_var.loc['protein', 'per 100g'])

    kj = int((17 * protein) + (37 * lipid) + (17 * sacharid))
    kcal = int((4 * protein) + (9 * lipid) + (4 * sacharid))

    en_value_dict = dict(zip(cdf['name_sk'], cdf['per 100g']))

    return dict(items=df.to_json(),
                en_value={k:round(v, 1) for k, v in en_value_dict.items()},
                kj=int(kj),
                kcal=int(kcal),
                total_product_weight=int(product_weight - 10),
                product_weight = int(product_weight),
                product_name=sheet)


def main(request):
    """Cloud Function to process uploaded Excel files and return nutrition facts."""
    if request.method == 'GET':
        return render_template('upload-excel.html')
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        try:
            #file = request.files['file']
            # save file in local directory
            file.save(file.filename)
            data = get_excel_sheets(file)

            if os.path.exists(file.filename):
                # removing processed file
                os.remove(file.filename)
            
            res = []
            for i in data:
                res.append(calc(file, i))

            return render_template("ind.html", data=res)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
