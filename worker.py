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
a_toast_prosciutto = FoodLabel(sheet_name='a_toast_prosciutto',
                               html_file='outputs/a_toast_prosciutto.html',
                               product_name='a_toast_prosciutto')
a_toast_prosciutto.render_with_jinja()


a_toast_mozzarella = FoodLabel(sheet_name='a_toast_mozzarella',
                               html_file='outputs/a_toast_mozzarella.html',
                               product_name='a_toast_mozzarella')
a_toast_mozzarella.render_with_jinja()


a_toast_sunka_syr = FoodLabel(sheet_name='a_toast_sunka_syr',
                              html_file='outputs/a_toast_sunka_syr.html',
                              product_name='a_toast_sunka_syr')
a_toast_sunka_syr.render_with_jinja()


b_salat_mrkvovy = FoodLabel(sheet_name='b_salat_mrkvovy',
                            html_file='outputs/b_salat_mrkvovy.html',
                            product_name='b_salat_mrkvovy')
b_salat_mrkvovy.render_with_jinja()


b_salat_civklovy = FoodLabel(sheet_name='b_salat_civklovy',
                             html_file='outputs/b_salat_civklovy.html',
                             product_name='b_salat_civklovy')
b_salat_civklovy.render_with_jinja()


b_salat_zelerovy = FoodLabel(sheet_name='b_salat_zelerovy',
                             html_file='outputs/b_salat_zelerovy.html',
                             product_name='b_salat_zelerovy')
b_salat_zelerovy.render_with_jinja()


c_salat_capresse = FoodLabel(sheet_name='c_salat_capresse',
                             html_file='outputs/c_salat_capresse.html',
                             product_name='c_salat_capresse')
c_salat_capresse.render_with_jinja()


c_protein_box = FoodLabel(sheet_name='c_protein_box',
                          html_file='outputs/c_protein_box.html',
                          product_name='c_protein_box')
c_protein_box.render_with_jinja()


c_salat_uhorkovy = FoodLabel(sheet_name='c_salat_uhorkovy',
                             html_file='outputs/c_salat_uhorkovy.html',
                             product_name='c_salat_uhorkovy')
c_salat_uhorkovy.render_with_jinja()


c_salat_cicerovo_zeleninovy_01 = FoodLabel(sheet_name='c_salat_cicerovo_zeleninovy_01',
                                           html_file='outputs/c_salat_cicerovo_zeleninovy_01.html',
                                           product_name='c_salat_cicerovo_zeleninovy_01')
c_salat_cicerovo_zeleninovy_01.render_with_jinja()


c_salat_cicerovo_zeleninovy_02 = FoodLabel(sheet_name='c_salat_cicerovo_zeleninovy_02',
                                           html_file='outputs/c_salat_cicerovo_zeleninovy_02.html',
                                           product_name='c_salat_cicerovo_zeleninovy_02')
c_salat_cicerovo_zeleninovy_02.render_with_jinja()


c_salat_caesar = FoodLabel(sheet_name='c_salat_caesar',
                           html_file='outputs/c_salat_caesar.html',
                           product_name='c_salat_caesar')
c_salat_caesar.render_with_jinja()


c_salat_grecky = FoodLabel(sheet_name='c_salat_grecky',
                           html_file='outputs/c_salat_grecky.html',
                           product_name='c_salat_grecky')
c_salat_grecky.render_with_jinja()


c_salat_gyros = FoodLabel(sheet_name='c_salat_gyros',
                          html_file='outputs/c_salat_gyros.html',
                          product_name='c_salat_gyros')
c_salat_gyros.render_with_jinja()



'''
ENDING
'''

# # x_francuzka_bageta
# x_zemiakovy_salat = FoodLabel(sheet_name='x_zemiakovy_salat',
#                                html_file = 'outputs/x_zemiakovy_salat.html',
#                                product_name = 'x_zemiakovy_salat')
# x_zemiakovy_salat.render_with_jinja()
#
#
# # x_francuzka_bageta
# x_francuzka_bageta = FoodLabel(sheet_name='x_francuzka_bageta',
#                                html_file='outputs/x_francuzka_bageta.html',
#                                product_name='Francúzska bageta')
# x_francuzka_bageta.render_with_jinja()
# # x_moriavia_bageta
# x_moriavia_bageta = FoodLabel(sheet_name='x_moriavia_bageta',
#                               html_file='outputs/x_moriavia_bageta.html',
#                               product_name='Bageta Moravia')
# x_moriavia_bageta.render_with_jinja()
# # x_sunkova_bageta
# x_sunkova_bageta = FoodLabel(sheet_name='x_sunkova_bageta',
#                              html_file='outputs/x_sunkova_bageta.html',
#                              product_name='Šunková Bageta')
# x_sunkova_bageta.render_with_jinja()
# # x_gyros_bageta
# x_gyros_bageta = FoodLabel(sheet_name='x_gyros_bageta',
#                            html_file='outputs/x_gyros_bageta.html',
#                            product_name='Bageta Gyros')
# x_gyros_bageta.render_with_jinja()
# # x_golden_nugets
# x_golden_nugets = FoodLabel(sheet_name='x_golden_nugets',
#                             html_file='outputs/x_golden_nugets.html',
#                             product_name='Golden Nuggets')
# x_golden_nugets.render_with_jinja()
# # x_stripsy_1
# x_stripsy_1 = FoodLabel(sheet_name='x_stripsy_1',
#                         html_file='outputs/x_stripsy_1.html',
#                         product_name='Bageta Kuracie Stripsy')
# x_stripsy_1.render_with_jinja()
# # x_labuznik_1
# x_labuznik_1 = FoodLabel(sheet_name='x_labuznik_1',
#                          html_file='outputs/x_labuznik_1.html',
#                          product_name='Bageta Labužník I')
# x_labuznik_1.render_with_jinja()
# # x_labuznik_2
# x_labuznik_2 = FoodLabel(sheet_name='x_labuznik_2',
#                          html_file='outputs/x_labuznik_2.html',
#                          product_name='Bageta Labužník II')
# x_labuznik_2.render_with_jinja()
# # x_zivanska_bageta_1
# x_zivanska_bageta_1 = FoodLabel(sheet_name='x_zivanska_bageta_1',
#                                 html_file='outputs/x_zivanska_bageta_1.html',
#                                 product_name='Živánska Bageta I')
# x_zivanska_bageta_1.render_with_jinja()
# # x_zivanska_bageta_2
# x_zivanska_bageta_2 = FoodLabel(sheet_name='x_zivanska_bageta_2',
#                                 html_file='outputs/x_zivanska_bageta_2.html',
#                                 product_name='Živánska Bageta II')
# x_zivanska_bageta_2.render_with_jinja()
# # x_debrecinska_bageta
# x_debrecinska_bageta = FoodLabel(sheet_name='x_debrecinska_bageta',
#                                  html_file='outputs/x_debrecinska_bageta.html',
#                                  product_name='Debrecínska Bageta')
# x_debrecinska_bageta.render_with_jinja()
# # x_maja_bageta
# x_maja_bageta = FoodLabel(sheet_name='x_maja_bageta',
#                           html_file='outputs/x_maja_bageta.html',
#                           product_name='Bageta Maja')
# x_maja_bageta.render_with_jinja()
# # x_bavorska_bageta
# x_bavorska_bageta = FoodLabel(sheet_name='x_bavorska_bageta',
#                               html_file='outputs/x_bavorska_bageta.html',
#                               product_name='Bavorská Bageta')
# x_bavorska_bageta.render_with_jinja()
#
# '''
# *******************************************
# *   25/0202018
# *******************************************
# '''
# _t_bazalkove_pesto = FoodLabel(sheet_name='_t_bazalkove_pesto',
#                               html_file='outputs/_t_bazalkove_pesto.html',
#                               product_name='Bavorská Bageta')
# _t_bazalkove_pesto.render_with_jinja()
#
#
# t_salat_caesar = FoodLabel(sheet_name='t_salat_caesar',
#                               html_file='outputs/t_salat_caesar.html',
#                               product_name='Ceaesar Šalát')
# t_salat_caesar.render_with_jinja()
#
# t_salat_s_pecenou_cviklou = FoodLabel(sheet_name='t_salat_s_pecenou_cviklou',
#                               html_file='outputs/t_salat_s_pecenou_cviklou.html',
#                               product_name='Šalát s pečenou cviklou')
# t_salat_s_pecenou_cviklou.render_with_jinja()
#
# t_salat_cestovinovy_s_kuracim = FoodLabel(sheet_name='t_salat_cestovinovy_s_kuracim',
#                               html_file='outputs/t_salat_cestovinovy_s_kuracim.html',
#                               product_name='Cestovinový šalát s kuracím mäsom a zeleninou')
# t_salat_cestovinovy_s_kuracim.render_with_jinja()
#
#
# t_salat_cous_cous = FoodLabel(sheet_name='t_salat_cous_cous',
#                               html_file='outputs/t_salat_cous_cous.html',
#                               product_name='Cous cous šalát s kuracím mäsom a zeleninou')
# t_salat_cous_cous.render_with_jinja()
#
#
# t_salat_exoticky_mix = FoodLabel(sheet_name='t_salat_exoticky_mix',
#                               html_file='outputs/t_salat_exoticky_mix.html',
#                               product_name='Šalát exotický mix')
# t_salat_exoticky_mix.render_with_jinja()
#
# '''
# 03/April/2018
# '''
#
# k_debrecinka_psenicna = FoodLabel(sheet_name='k_debrecinka_psenicna',
#                                   html_file='outputs/k_debrecinka_psenicna.html',
#                                   product_name='Debrecínka pšeničná')
# k_debrecinka_psenicna.render_with_jinja()
# k_debrecinka_psenicna_mala = FoodLabel(sheet_name='k_debrecinka_psenicna_mala',
#                                        html_file='outputs/k_debrecinka_psenicna_mala.html',
#                                        product_name='Debrecínka pšeničná malá')
# k_debrecinka_psenicna_mala.render_with_jinja()
# k_francuzka_psenicna = FoodLabel(sheet_name='k_francuzka_psenicna',
#                                  html_file='outputs/k_francuzka_psenicna.html',
#                                  product_name='Francúzka pšeničná')
# k_francuzka_psenicna.render_with_jinja()
# k_gyros_psenicna = FoodLabel(sheet_name='k_gyros_psenicna',
#                              html_file='outputs/k_gyros_psenicna.html',
#                              product_name='Gyros pšeničná')
# k_gyros_psenicna.render_with_jinja()
# k_gyros_psenicna_mala = FoodLabel(sheet_name='k_gyros_psenicna_mala',
#                                   html_file='outputs/k_gyros_psenicna_mala.html',
#                                   product_name='Gyros pšeničná malá')
# k_gyros_psenicna_mala.render_with_jinja()
# k_labuznik_spaldova = FoodLabel(sheet_name='k_labuznik_spaldova',
#                                 html_file='outputs/k_labuznik_spaldova.html',
#                                 product_name='Labužník špaldová')
# k_labuznik_spaldova.render_with_jinja()
# k_morcacia_spaldova = FoodLabel(sheet_name='k_morcacia_spaldova',
#                                 html_file='outputs/k_morcacia_spaldova.html',
#                                 product_name='Morčacia špaldová')
# k_morcacia_spaldova.render_with_jinja()
# k_moravia_staroceska = FoodLabel(sheet_name='k_moravia_staroceska',
#                                  html_file='outputs/k_moravia_staroceska.html',
#                                  product_name='Moravia staročeská')
# k_moravia_staroceska.render_with_jinja()
# k_kuracie_stripsy_psenicna = FoodLabel(sheet_name='k_kuracie_stripsy_psenicna',
#                                        html_file='outputs/k_kuracie_stripsy_psenicna.html',
#                                        product_name='Kuracie stripsy pšeničná')
# k_kuracie_stripsy_psenicna.render_with_jinja()
# k_kuracie_stripsy_psenicna_mala = FoodLabel(sheet_name='k_kuracie_stripsy_psenicna_mala',
#                                             html_file='outputs/k_kuracie_stripsy_psenicna_mala.html',
#                                             product_name='Kuracie stripsy pšeničná malá')
# k_kuracie_stripsy_psenicna_mala.render_with_jinja()
# k_sunkova_spaldova = FoodLabel(sheet_name='k_sunkova_spaldova',
#                                html_file='outputs/k_sunkova_spaldova.html',
#                                product_name='Šunková špaldová')
# k_sunkova_spaldova.render_with_jinja()
# k_sunkova_psenicna_mala = FoodLabel(sheet_name='k_sunkova_psenicna_mala',
#                                     html_file='outputs/k_sunkova_psenicna_mala.html',
#                                     product_name='Šunková pšeničná')
# k_sunkova_psenicna_mala.render_with_jinja()
# k_farmarska_psenicna = FoodLabel(sheet_name='k_farmarska_psenicna',
#                                  html_file='outputs/k_farmarska_psenicna.html',
#                                  product_name='Farmárska pšeničná')
# k_farmarska_psenicna.render_with_jinja()
#
# k_bavaria_staroceska = FoodLabel(sheet_name='k_bavaria_staroceska',
#                                  html_file='outputs/k_bavaria_staroceska.html',
#                                  product_name='Bavaria staročeská')
# k_bavaria_staroceska.render_with_jinja()
#
# k_syrova_grahamova = FoodLabel(sheet_name='k_syrova_grahamova',
#                                  html_file='outputs/k_syrova_grahamova.html',
#                                  product_name='Syrová grahamová')
# k_syrova_grahamova.render_with_jinja()
#
#


# a_toast_prosciutto
# a_toast_mozzarella
# a_toast_sunka_syr
# b_salat_mrkvovy
# b_salat_civklovy
# b_salat_zelerovy
# c_salat_capresse
# c_protein_box
# c_salat_uhorkovy
# c_salat_cicerovo_zeleninovy_01
# c_salat_cicerovo_zeleninovy_02
# c_salat_caesar
# c_salat_grécky
# c_salat_gyros










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