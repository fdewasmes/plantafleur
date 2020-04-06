import requests
import datetime
from datetime import timedelta
import pytz
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, PageBreak

# Query orders
tz = pytz.timezone('Europe/Berlin')
now = datetime.datetime.now(tz)
past = now - timedelta(hours=48)
past_str = past.strftime("%Y-%m-%dT%H:%M:%S%z")
print(past_str)

ploads = {'created_at_min': past_str, 'fields': 'name,created_at,line_items'}
headers = {'Content-Type': 'application/json'}
r = requests.get("https://4bacebee6942d6e0aa755151709e743e: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@plantafleurdrive.myshopify.com/admin/api/2020-04/orders.json", params=ploads)

json_response = r.json()
orders = json_response['orders']

# Parse orders
preparation_list = [['Produit', 'Quantité']]
r_items = dict()
r_orders = [['Numéro de commande', 'Date', 'détail']]

for order in orders:
    order_detail = ""

    # build preparation list
    for item in order['line_items']:
        order_detail += "\n " + str(item['quantity']) + " " + item['name']

        name = item['name']
        if name in r_items:
            previous_qty = r_items[name]
            new_qty = previous_qty + item['quantity']
            r_items[name] = new_qty
        else:
            r_items[name] = item['quantity']

    date_time_obj = datetime.datetime.strptime(order['created_at'], '%Y-%m-%dT%H:%M:%S%z')
    o = [order['name'], date_time_obj.strftime("%d %b %Y %H:%M:%S"), order_detail]
    r_orders.append(o)

for item in r_items:
    line = [item, r_items[item]]
    preparation_list.append(line)

# create PDF
doc = SimpleDocTemplate('test.pdf', pagesize=letter)
styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']
story = []
story.append(Paragraph("Liste de préparation",styleH))
t = Table(preparation_list)
t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
data_len = len(preparation_list)
for each in range(data_len):
    if each % 2 == 0:
        bg_color = colors.whitesmoke
    else:
        bg_color = colors.lightgrey

    t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

story.append(t)
story.append(PageBreak())


story.append(Paragraph("Commandes", styleH))
t = Table(r_orders)
t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))
data_len = len(r_orders)
for each in range(data_len):
    if each % 2 == 0:
        bg_color = colors.whitesmoke
    else:
        bg_color = colors.lightgrey

    t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

story.append(t)
doc.build(story)

# end