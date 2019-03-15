import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader


class FoodLabel(object):

    _normovane = ["n_lipid",
                  "n_saturated",
                  "n_sacharides",
                  "n_sugar",
                  "n_proteins",
                  "n_salt"]

    _product_attributes = \
        ['lipid',
         'saturated',
         'sacharides',
         'sugar',
         'protein',
         'salt']

    name_sk = ["Tuk", 
               "Nenásytené mastné kyseliny", 
               "Sacharidy", 
               "Cukry",
               "Bielkoviny", 
               "Soľ"]

    def __init__(self, hundred_grams=100,
                 xlsx_filename='list.xlsx',
                 sheet_name='corn_bageta',
                 product_sheet_name='products',
                 template_dir='templates',
                 html_file='main.html',
                 product_file='product.tpl',
                 product_name='<Produkt>'):

        self.hundred_grams = hundred_grams
        self.xlsx_filename = xlsx_filename
        self.sheet_name = sheet_name
        self.product_sheet_name = product_sheet_name
        self.template_dir = template_dir
        self.html_file = html_file
        self.product_file = product_file
        self.product_name = product_name

        self.jenv = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.jenv.get_template('main.tpl')
        # self.product = self.jenv.get_template(self.product_file)

    def load_products_from_file(self, _file_name=None, _sheet_name=None):
        _file_name = _file_name or self.xlsx_filename
        _sheet_name = _sheet_name or self.sheet_name
        xl = pd.ExcelFile(_file_name)
        _data_frame = xl.parse(_sheet_name)
        return _data_frame

    def get_products_from_file(self):
        description = self.load_products_from_file(self.xlsx_filename, self.sheet_name)
        data_frame = self.load_products_from_file(self.xlsx_filename, self.sheet_name)
        product_list = self.load_products_from_file(self.xlsx_filename,
                                                          self.product_sheet_name)
        '''
        calculating sum [g] (weight) of the product e.g 'bageta' 
        this function returns three data frames:
            - _desc   - this will be removed shortly
            - df
            - look_for_desc
        doesn't do much - it only calls method 3x: load_products_from_file
        '''
        return data_frame, description, product_list

    def calculate(self):
        """
        working_frame = data_frame
        product_description = description
        product_list_data = product_list
        :return:
        """
        format_calculus = lambda x: '{0:.1f}'.format(round(float(x), 1))
        format_repace = lambda x: str(x).replace('.', ',')
        working_frame, product_description, product_list_data = \
            self.get_products_from_file()

        _sum_of_attributes = []
        _x_hundred_grams = []

        for _n, _a in zip(FoodLabel._normovane,
                          FoodLabel._product_attributes):
            working_frame[_n] = \
                working_frame[_a].astype(float) * \
                working_frame['weight'].astype(float) / float(self.hundred_grams)

        _compare = pd.DataFrame()
        _compare = pd.merge(working_frame, 
                            product_list_data, 
                            left_on='_products', 
                            right_on='id_product')
        _dict_compare = dict(zip(_compare['id_product'], _compare['id_product_description']))

        # assign_description = lambda x: _dict_compare[x] if x in _dict_compare else 'No_match'
        #assign_description = working_frame['desc']
        working_frame['desc_from_library'] = 0

        # working_frame['desc_from_library'] = working_frame['_products'].map(assign_description)
        working_frame['desc_from_library'] = working_frame['desc']
        product_weight = working_frame['weight'].sum()
        working_frame['percentage'] = ((working_frame['weight'] / product_weight) * 100).map(format_calculus)
        working_frame['percentage'] = working_frame['percentage'].map(format_repace)

        for _nr in FoodLabel._normovane:
            _soa = working_frame[_nr].sum()
            _sum_of_attributes.append(round(_soa, 1))
            
            _tmp_hundred_g = \
                self.hundred_grams * working_frame[_nr].sum() / product_weight
            _x_hundred_grams.append(_tmp_hundred_g)


        calculated_product_values = pd.DataFrame()
        calculated_product_values['name'] = \
            pd.Series(FoodLabel._product_attributes)
        calculated_product_values['sums of attributes'] = pd.Series(
            _sum_of_attributes)

        calculated_product_values['per 100g'] = pd.Series(_x_hundred_grams)
        # format_calculus = lambda x: '{0:.1f}'.format(round(float(x), 1))
        calculated_product_values['per 100g'] = \
            calculated_product_values['per 100g'].map(format_calculus)

        calculated_product_values['name_sk'] = pd.Series(FoodLabel.name_sk)
        '''
                creating temporary pandas data-frame: temp
                and setting index to 'name' column so it will
                be easier to locate and calculate:
                    - lipid
                    - sacharides
                    - protein

                '''
        # calculated_product_values['percentage'] = (working_frame['weight'] / product_weight) * 100
        temp_var = calculated_product_values
        temp_var = temp_var.set_index("name")

        lipid = float(temp_var.loc['lipid', 'per 100g'])
        sacharid = float(temp_var.loc['sacharides', 'per 100g'])
        protein = float(temp_var.loc['protein', 'per 100g'])

        kj = int((17 * protein) + (37 * lipid) + (17 * sacharid))
        kcal = int((4 * protein) + (9 * lipid) + (4 * sacharid))
        kj = str(kj).replace('.', ',')
        kcal = str(kcal).replace('.', ',')


        calculated_product_values['per 100g'] = \
            calculated_product_values['per 100g'].map(format_repace)

        en_value_dict = \
            dict(zip(calculated_product_values['name_sk'],
                     calculated_product_values['per 100g']))

        print(product_weight)
        # print(((working_frame['weight'] / product_weight) * 100).sum())
        # print(((working_frame['weight'] / product_weight) * 100))
        # print(working_frame)
        return dict(items=working_frame,
                    en_value=en_value_dict,
                    kj=kj,
                    kcal=kcal,
                    total_product_weight=product_weight - 10,
                    product_name=self.product_name)

    def render_with_jinja(self):
        content = self.calculate()
        _output = self.template.render(**content)
        with(open(self.html_file, encoding='utf8', mode='w')) as f:
            f.write(_output)
        return self.html_file, _output

'''
Code is starting over here :P)

'''
