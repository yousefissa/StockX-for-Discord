import json

import discord
import requests
from bs4 import BeautifulSoup


with open('config.json') as json_file:
    config = json.load(json_file)

discord_token = config['discord_token']
api_url = config['api_url']
base_url = config['base_url']

client = discord.Client()


@client.event
async def on_ready():
    print('{} Logged In!'.format(client.user.name))


@client.event
async def on_message(message):
    if message.content.startswith('!stockx '):
        product_name = message.content.split('!stockx ')[1]

        payload = {
            'x-algolia-agent': 'Algolia for vanilla JavaScript 3.27.1',
            'x-algolia-api-key': '6bfb5abee4dcd8cea8f0ca1ca085c2b3',
            'x-algolia-application-id': 'XW7SBCT9V6'
        }

        json_payload = {
            "params": "query={}&hitsPerPage=1".format(product_name)
        }

        r = requests.post(url=api_url, params=payload, json=json_payload)
        output = json.loads(r.text)

        product_name = ''
        thumbnail_url = ''
        product_url = ''
        release_date = ''
        style_id = ''
        highest_bid = ''
        lowest_ask = ''
        last_sale = ''
        sales_last_72 = ''
        deadstock_sold = ''
        retail_price = ''
        try:
            product_name = output['hits'][0]['name']
            thumbnail_url = output['hits'][0]['thumbnail_url']
            product_url = base_url + output['hits'][0]['url']
            release_date = output['hits'][0]['release_date']
            style_id = output['hits'][0]['style_id']
            highest_bid = output['hits'][0]['highest_bid']
            lowest_ask = output['hits'][0]['lowest_ask']
            last_sale = output['hits'][0]['last_sale']
            sales_last_72 = output['hits'][0]['sales_last_72']
            deadstock_sold = output['hits'][0]['deadstock_sold']
            retail_price = output['hits'][0]['searchable_traits']['Retail Price']
        except KeyError:
            pass
        except IndexError:
            await client.send_message(message.channel, 'Error fetching data from the API. Please try another product.')
            raise

        r = requests.get(url=product_url)
        soup = BeautifulSoup(r.text, 'html.parser')

        last_sale_size = ''
        lowest_ask_size = ''
        highest_bid_size = ''
        try:
            last_sale_size = soup.find('div', {'class': 'last-sale-block'}).find(
                'span', {'class':'bid-ask-sizes'}).text
            lowest_ask_size = soup.find('div', {'class': 'bid bid-button-b'}).find(
                'span', {'class':'bid-ask-sizes'}).text
            highest_bid_size = soup.find('div', {'class': 'ask ask-button-b'}).find(
                'span', {'class':'bid-ask-sizes'}).text
        except AttributeError:
            pass

        embed = discord.Embed(color=4500277)
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name='Product Name', value='[{}]({})'.format(product_name, product_url), inline=False)
        embed.add_field(name='Style ID', value = '{}'.format(style_id), inline=True)
        embed.add_field(name='Release Date', value='{}'.format(release_date), inline=True)
        embed.add_field(name='Retail Price', value='${}'.format(retail_price), inline=True)
        embed.add_field(name='Last Sale', value='${}, {}'.format(last_sale, last_sale_size), inline=True)
        embed.add_field(name='Lowest Ask', value='${}, {}'.format(lowest_ask, lowest_ask_size), inline=True)
        embed.add_field(name='Highest Bid', value='${}, {}'.format(highest_bid, highest_bid_size), inline=True)
        embed.add_field(name='Units Sold in Last 3 Days', value='{}'.format(sales_last_72), inline=True)
        embed.add_field(name='Total Units Sold', value='{}'.format(deadstock_sold), inline=True)

        await client.send_message(message.channel, embed=embed)

if __name__ == '__main__':
    client.run(discord_token)