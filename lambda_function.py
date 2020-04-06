import json
import urllib
import io
import boto3
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

def query_orders(timedelta_hours):
    # Query orders
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.datetime.now(tz)
    past = now - timedelta(hours=timedelta_hours)
    past_str = past.strftime("%Y-%m-%dT%H:%M:%S%z")

    ploads = {'created_at_min': past_str, 'fields': 'name,created_at,line_items'}
    headers = {'Content-Type': 'application/json'}
    r = requests.get("https://4bacebee6942d6e0aa755151709e743e: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@plantafleurdrive.myshopify.com/admin/api/2020-04/orders.json", params=ploads)

    json_response = r.json()
    orders = json_response['orders']
    return orders

def parse_orders(orders):
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
    return (preparation_list,r_orders)

def create_pdf(preparation_list, r_orders):
    # create PDF
    stream = io.BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=letter)
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

    # get buffer
    pdf_buffer = stream.getbuffer()
    tz = pytz.timezone('Europe/Berlin')
    now = datetime.datetime.now(tz)
    now_str = now.strftime("%Y-%m-%dT%H:%M:%S")

    filename = "commandes"+now_str+".pdf"
    bucket_name = 'arn:aws:s3:eu-west-3:274275471339:accesspoint/plantafleur'
    object_name = bucket_name

    # here is where I get stuck - how should be passing the pdf_buffer to s3?

    # how you typically write to s3 :
    # Method 1

    stream.seek(0)
    s3 = boto3.client('s3')
    #with open(filename, "rb") as f:
    #    s3.upload_fileobj(f, bucket_name, object_name)

    # Method 2
    s3.put_object(Key=filename, Body=stream.getvalue(), Bucket=bucket_name)
    print ("generated file: "+filename)
    fileurl = "https://plantafleur.s3.eu-west-3.amazonaws.com/"+urllib.parse.quote(filename)
    print(fileurl)
    return fileurl

# end

def main():
    orders = query_orders()
    (preparation_list,r_orders) = parse_orders(orders)
    create_pdf(preparation_list, r_orders)

if __name__ == "__main__":
    main()

def lambda_handler(event, context):
    params = event['queryStringParameters']
    timedelta_hours = 0
    timedelta_str = ''
    if 'timedelta' in params:
        try:
            timedelta_str = params['timedelta']
            timedelta_hours = int(timedelta_str)
        except ValueError as e:
            print("bad input parameter timedelta: "+params['timedelta'])

    orders = query_orders(timedelta_hours)
    (preparation_list,r_orders) = parse_orders(orders)
    filename = create_pdf(preparation_list, r_orders)
    HTML = '<HTML><BODY><a href="'+filename+'">fichier </a> g&eacute;n&eacute;r&eacute; avec un delta de '+timedelta_str+"</BODY></HTML>"
    return {
        'statusCode': 200,
        #'body': json.dumps(filename+' File generated using timedelta: '+timedelta_str),
        'body': HTML,
        'headers': {"Content-Type": "text/html"}
    }
