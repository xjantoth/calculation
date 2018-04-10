{{ product_name }} = FoodLabel(sheet_name='{{ product_name }}',
                                 html_file='outputs/{{ product_name }}.html',
                                 product_name='{{ product_name }}')
{{ product_name }}.render_with_jinja()
