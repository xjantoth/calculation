_template_product = {"product_name": " ",
                     "weight": " ",
                     "lipid": " ",
                     "nasytene": " ",
                     "sacharides": " ",
                     "sugar": " ",
                     "proteins": " ",
                     "salt": " ",
                     "n_lipid": 0,
                     "n_nasytene": 0,
                     "n_sacharides": 0,
                     "n_sugar": 0,
                     "n_proteins": 0,
                     "n_salt": 0
                     }


def load_products_from_file(_file_name):
    with open(_file_name, 'r') as fl:
        _lines = fl.readlines()
        return _lines


def process_unique_product(_product):
    _product = [_p.strip() for _p in _product.split(';')]
    unique_product = _template_product
    for _pk, _on in zip(["product_name",
                         "weight",
                         "lipid",
                         "nasytene",
                         "sacharides",
                         "sugar",
                         "proteins",
                         "salt"],
                        range(0, len(_product))):
        unique_product[_pk] = _product[_on]

    for _nw, _keys in zip(["n_lipid",
                           "n_nasytene",
                           "n_sacharides",
                           "n_sugar",
                           "n_proteins",
                           "n_salt"],
                          ["lipid",
                           "nasytene",
                           "sacharides",
                           "sugar",
                           "proteins",
                           "salt"]
                          ):
        _tmp = float(unique_product['weight']) * \
                float(unique_product[_keys]) / float(hundred_grams)
        unique_product[_nw] = _tmp

    return unique_product


path = "c:\\Users\\d58560\\Documents\\personal\\"
file_name = 'etikety.txt'
complete_file_name = str(path + file_name)
hundred_grams = 100


'''
all the product from text files will be stored 
within this list
'''
list_of_all_products = load_products_from_file(complete_file_name)


final_meal = []
for lop in list_of_all_products:
    item = process_unique_product(lop)
    '''
    Note: item is a {"product_name": "sunka", "...": "...", ...} structure 
    and if you want to append it to the list :) you need to use
    final_meal.append(item.copy())
    '''
    final_meal.append(item.copy())


sums_of_meal_attributes = {"sum_lipid": 0,
                           "sum_nasytene": 0,
                           "sum_sacharides": 0,
                           "sum_sugar": 0,
                           "sum_proteins": 0,
                           "sum_salt": 0}
for i in final_meal:
    print('polozka.: {:20} hm.: {:10} tuky: {:10} nasytene: {:10}'
          .format(i['product_name'],
                  i['weight'],
                  i['n_lipid'],
                  i['n_nasytene']))

    for _sums, _norms in zip(["sum_lipid",
                              "sum_nasytene",
                              "sum_sacharides",
                              "sum_sugar",
                              "sum_proteins",
                              "sum_salt"],
                             ["n_lipid",
                              "n_nasytene",
                              "n_sacharides",
                              "n_sugar",
                              "n_proteins",
                              "n_salt"]):
        sums_of_meal_attributes[_sums] = \
            sum([float(i[_norms]) for i in final_meal])


print(sums_of_meal_attributes)









