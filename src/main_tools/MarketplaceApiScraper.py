import math
import cloudscraper
import pandas as pd

from src.main_tools.RoiCalculator import RoiCalculator


class MarketplaceApiScraper(RoiCalculator):
    def __init__(self):
        super(MarketplaceApiScraper, self).__init__()
        self.s = cloudscraper.create_scraper()
        self.size = 50
        self.total_listings = 0
        self._base_url = f"https://data.thetanarena.com/thetan/v1/nif/search?from=0&size={self.size}"

    def run(self):
        pages = self._total_pages()
        idx = 0
        items = []
        for page in range(pages):
            url = f"https://data.thetanarena.com/thetan/v1/nif/search?from={self.size*page}&size={self.size}"
            r = self.get_response(url)
            listings = r.json().get('data')
            for listing in listings:
                idx += 1
                data = self._calculate_profit(listing)
                url = data['url']
                profit = data['profit']
                hero_rarity = data['hero_rarity']
                currency = data['currency']
                items.append({'url': url, 'profit': profit, 'currency': currency, 'hero_rarity': hero_rarity})
                print(f'{idx} / {self.total_listings}')

        print(60*'*')
        print(60*'*')
        print(60*'*')
        sorted_list = sorted(items, key=lambda d: d['profit'], reverse=True)
        for i in sorted_list:
            hero_rarity_names = {0: 'common', 1: 'epic', 2: 'legendary'}
            clean_data = {
                'url': i.get('url'),
                'profit': i.get('profit'),
                'currency': i.get('currency'),
                'hero_rarity': hero_rarity_names[i.get('hero_rarity')]
            }
            self.thetan_output(clean_data)
        self.writer()

    def _extract_data(self, listing: dict):
        data = {
            'url': f'https://marketplace.thetanarena.com/item/{listing.get("refId")}',
            'decimals': listing.get('systemCurrency')['decimals'],
            'price': listing.get('price'),
            'hero_rarity': listing.get('heroRarity'),
            'skin': listing.get('skinRarity'),
            'lvl': listing.get('trophyClass'),
            'battles_remain': listing.get('battleCap')
        }
        formatted_price = self._convert_price_to_usd(str(data['price']), data['decimals'])
        data['price'] = formatted_price
        return data

    def _calculate_profit(self, listing):
        data = self._extract_data(listing)
        profit_data = self.calculate_roi(hero_rarity=data['hero_rarity'], battles_remain=data['battles_remain'], purchased=data['price'])
        profit = profit_data['profit']
        currency = profit_data['currency']
        return {'url': data['url'], 'profit': profit, 'currency': currency, 'hero_rarity': data['hero_rarity']}

    def _total_pages(self):
        total_listing = self._get_total_listing_count()
        total_pages = math.ceil(int(total_listing) / 50)
        return total_pages

    def _get_total_listing_count(self):
        r = self.get_response(self._base_url)
        if r.json().get('success'):
            total = r.json()['page']['total']
            self.total_listings = total
            return total
        else:
            raise Exception(f'API Response failed, status_code: [Response<{r.status_code}>]')

    def _convert_price_to_usd(self, price, decimals):
        bnb_to_usd = self._config.get('bnb_price')
        converted_price = f'{price[:-decimals]}.{price[-decimals:]}'
        converted_price = float(converted_price) * bnb_to_usd
        return converted_price
