from jinja2 import Template
import jinja2

from IPython.display import display, clear_output, HTML

dt1 = Template(
    """
<table>
{% for key, value in data.items() %}
   <tr>
        <th style="text-align:left;padding:15px"> {{ key }} </th>
        <td style="text-align:right;padding:15px"> {{ value }} </td>
   </tr>
{% endfor %}
</table>"""
)
dt2 = Template(
    """
<table>
   <tr>
   {% for key,_ in data.items() %}
        <th style="text-align:left"> {{ key }} </th>
   {% endfor %}
   </tr>
   {% for _,value in data.items() %}
        <td style="text-align:left"> {{ value }} </td>
   {% endfor %}
   </tr>
</table>"""
)

t2 = Template(
    """<table>
{%- for row in data|batch(ncols, '&nbsp;') %}
  <tr>
  {%- for column in row %}
    <td>{{ column }}</td>
  {%- endfor %}
  </tr>
{%- endfor %}
</table>"""
)

t3 = Template(
    """
<pre style="white-space: pre !important;"></pre>
{% block content %}
<h3 align="center"> {{title}} </h3>
    <img src="{{ fname }}" alt="image alt text" />
{% endblock %}
"""
)





def get_table_columns(table_descriptions):
    return {t: set(f["Field"]) for t, f in table_descriptions.items()}

def ddict(d, template=dt1):
    return template.render(data=d)


def view_dict(d, vertical=False):
    if vertical:
        return HTML(ddict(d))
    else:
        return HTML(ddict(d, template=dt2))

def dlist(l, ncols=5, sort=False):

    if sort:
        l.sort()
    return t2.render(data=l, ncols=ncols)
