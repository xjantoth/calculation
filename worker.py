import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


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
                 product_name='<Produkt>'):

        self.hundred_grams = hundred_grams
        self.xlsx_filename = xlsx_filename
        self.sheet_name = sheet_name
        self.product_sheet_name = product_sheet_name
        self.template_dir = template_dir
        self.html_file = html_file
        self.product_name = product_name

        self.jenv = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.jenv.get_template('main.tpl')

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
        format_calculus = lambda x: '{0:.1f}'.format(round(float(x), 1))
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
        temp_var = calculated_product_values
        temp_var = temp_var.set_index("name")

        lipid = float(temp_var.loc['lipid', 'per 100g'])
        sacharid = float(temp_var.loc['sacharides', 'per 100g'])
        protein = float(temp_var.loc['protein', 'per 100g'])

        kj = int((17 * protein) + (37 * lipid) + (17 * sacharid))
        kcal = int((4 * protein) + (9 * lipid) + (4 * sacharid))
        kj = str(kj).replace('.', ',')
        kcal = str(kcal).replace('.', ',')

        format_repace = lambda x: str(x).replace('.', ',')
        calculated_product_values['per 100g'] = \
            calculated_product_values['per 100g'].map(format_repace)

        en_value_dict = \
            dict(zip(calculated_product_values['name_sk'],
                     calculated_product_values['per 100g']))

        print(product_weight)
        return dict(items=working_frame,
                    en_value=en_value_dict,
                    kj=kj,
                    kcal=kcal,
                    total_product_weight=product_weight,
                    product_name=self.product_name)

    def render_with_jinja(self):
        content = self.calculate()
        _output = self.template.render(**content)
        with(open(self.html_file, encoding='utf8', mode='w')) as f:
            f.write(_output)
        return _output


# x_francuzka_bageta
x_zemiakovy_salat = FoodLabel(sheet_name='x_zemiakovy_salat',
                               html_file = 'outputs/x_zemiakovy_salat.html',
                               product_name = 'x_zemiakovy_salat')
x_zemiakovy_salat.render_with_jinja()


# x_francuzka_bageta
x_francuzka_bageta = FoodLabel(sheet_name='x_francuzka_bageta',
                               html_file='outputs/x_francuzka_bageta.html',
                               product_name='x_francuzka_bageta')
x_francuzka_bageta.render_with_jinja()
# x_moriavia_bageta
x_moriavia_bageta = FoodLabel(sheet_name='x_moriavia_bageta',
                              html_file='outputs/x_moriavia_bageta.html',
                              product_name='x_moriavia_bageta')
x_moriavia_bageta.render_with_jinja()
# x_sunkova_bageta
x_sunkova_bageta = FoodLabel(sheet_name='x_sunkova_bageta',
                             html_file='outputs/x_sunkova_bageta.html',
                             product_name='x_sunkova_bageta')
x_sunkova_bageta.render_with_jinja()
# x_gyros_bageta
x_gyros_bageta = FoodLabel(sheet_name='x_gyros_bageta',
                           html_file='outputs/x_gyros_bageta.html',
                           product_name='x_gyros_bageta')
x_gyros_bageta.render_with_jinja()
# x_golden_nugets
x_golden_nugets = FoodLabel(sheet_name='x_golden_nugets',
                            html_file='outputs/x_golden_nugets.html',
                            product_name='Golden Nuggets')
x_golden_nugets.render_with_jinja()
# x_stripsy_1
x_stripsy_1 = FoodLabel(sheet_name='x_stripsy_1',
                        html_file='outputs/x_stripsy_1.html',
                        product_name='x_stripsy_1')
x_stripsy_1.render_with_jinja()
# x_labuznik_1
x_labuznik_1 = FoodLabel(sheet_name='x_labuznik_1',
                         html_file='outputs/x_labuznik_1.html',
                         product_name='x_labuznik_1')
x_labuznik_1.render_with_jinja()
# x_labuznik_2
x_labuznik_2 = FoodLabel(sheet_name='x_labuznik_2',
                         html_file='outputs/x_labuznik_2.html',
                         product_name='x_labuznik_2')
x_labuznik_2.render_with_jinja()
# x_zivanska_bageta_1
x_zivanska_bageta_1 = FoodLabel(sheet_name='x_zivanska_bageta_1',
                                html_file='outputs/x_zivanska_bageta_1.html',
                                product_name='x_zivanska_bageta_1')
x_zivanska_bageta_1.render_with_jinja()
# x_zivanska_bageta_2
x_zivanska_bageta_2 = FoodLabel(sheet_name='x_zivanska_bageta_2',
                                html_file='outputs/x_zivanska_bageta_2.html',
                                product_name='x_zivanska_bageta_2')
x_zivanska_bageta_2.render_with_jinja()
# x_debrecinska_bageta
x_debrecinska_bageta = FoodLabel(sheet_name='x_debrecinska_bageta',
                                 html_file='outputs/x_debrecinska_bageta.html',
                                 product_name='x_debrecinska_bageta')
x_debrecinska_bageta.render_with_jinja()
# x_maja_bageta
x_maja_bageta = FoodLabel(sheet_name='x_maja_bageta',
                          html_file='outputs/x_maja_bageta.html',
                          product_name='x_maja_bageta')
x_maja_bageta.render_with_jinja()
# x_bavorska_bageta
x_bavorska_bageta = FoodLabel(sheet_name='x_bavorska_bageta',
                              html_file='outputs/x_bavorska_bageta.html',
                              product_name='x_bavorska_bageta')
x_bavorska_bageta.render_with_jinja()












        # css_1A = FoodLabel(sheet_name='1A',
#                    html_file='1A.html',
#                    product_name='1A')
# css_1A.render_with_jinja()
#
# css_1B = FoodLabel(sheet_name='1B',
#                    html_file='1B.html',
#                    product_name='1B')
# css_1B.render_with_jinja()
#
# """ ... ... ... ... ... ... ... ... ..  """
#
# css_2A = FoodLabel(sheet_name='2A',
#                    html_file='2A.html',
#                    product_name='2A')
# css_2A.render_with_jinja()
#
# css_2B = FoodLabel(sheet_name='2B',
#                    html_file='2B.html',
#                    product_name='2B')
# css_2B.render_with_jinja()
#
# """ ... ... ... ... ... ... ... ... ..  """
#
# css_3A = FoodLabel(sheet_name='3A',
#                    html_file='3A.html',
#                    product_name='3A')
# css_3A.render_with_jinja()
#
# css_3B = FoodLabel(sheet_name='3B',
#                    html_file='3B.html',
#                    product_name='3B')
# css_3B.render_with_jinja()
#
# """ ... ... ... ... ... ... ... ... ..  """
#
# css_4A = FoodLabel(sheet_name='4A',
#                    html_file='4A.html',
#                    product_name='4A')
# css_4A.render_with_jinja()
#
# css_4B = FoodLabel(sheet_name='4B',
#                    html_file='4B.html',
#                    product_name='4B')
# css_4B.render_with_jinja()
#
# """ ... ... ... ... ... ... ... ... ..  """
# css_banany = FoodLabel(sheet_name='banany',
#                        html_file='css_banany.html',
#                        product_name='banany_v_cokolade')
# css_banany.render_with_jinja()
#
# css_maliny = FoodLabel(sheet_name='maliny',
#                        html_file='css_maliny.html',
#                        product_name='maliny_v_cokolade')
# css_maliny.render_with_jinja()
#
# caesar_salat = FoodLabel(sheet_name='caesar_salat',
#                        html_file='caesar_salat.html',
#                        product_name='caesar_salat')
# caesar_salat.render_with_jinja()
#
#
# caesar_salat = FoodLabel(sheet_name='x_francuzka_bageta',
#                        html_file='x_francuzka_bageta.html',
#                        product_name='x_francuzka_bageta')
# caesar_salat.render_with_jinja()




#
#css_53 = FoodLabel(sheet_name='css_53',
#                   html_file='css_53.html',
#                   product_name='css_53')
#css_53.render_with_jinja()
#
#css_54 = FoodLabel(sheet_name='css_54',
#                   html_file='css_54.html',
#                   product_name='css_54')
#css_54.render_with_jinja()