'''
Short improvement
'''


def load_render(_file):
    """

    :param _file:
    :return:
    """
    with open(_file, "r") as f:
        x = f.readlines()
    t = [i.strip() for i in x if not i.startswith("#")]
    return t


def render_simple(_input):
    for i in _input:
        print("\n{0} = FoodLabel(sheet_name='{0}',\n\thtml_file='outputs/{0}.html',\n\tproduct_name='{0}')\n{0}.render_with_jinja()\n".format(i))

    def render_product_jinja(self, _particular_product):
        """

        :param _particular_product:
        :return:
        """
        _output = self.product.render(product_name=_particular_product)
        print(_output)
        return _particular_product, _output


'''
Code's starting over here
'''
file = "k_series.txt"

vec = load_render(file)
render_simple(vec)