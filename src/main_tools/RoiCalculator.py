import cloudscraper

from src.common.common import Common


class RoiCalculator(Common):  # main_tools (Return Of Investment)
    def __init__(self):
        super(RoiCalculator, self).__init__()
        self._config = self.open_yaml('src/script_settings.yaml')
        self.win_bonus = 6
        self.fee = 0.04

    def calculate_roi(self, hero_rarity, battles_remain, purchased):
        profit_usd = self._hero_usd_earnings(hero_rarity, battles_remain, purchased)
        return profit_usd

    def _hero_gthc_earnings(self, hero_rarity, battles_remain):
        # hero_rarity = self._config.get('hero_rarity')
        win_ratio = self._config.get('win_ratio')
        # battle_cap = self._config.get('battle_cap')
        # battle_played = self._config.get('battle_played')

        lose_ratio = (1 - (win_ratio/100)) * 10
        hero_bonuses = {0: 1.45, 1: 5, 2: 23.55}
        const = (hero_bonuses[hero_rarity] + self.win_bonus)
        gthc = (const * battles_remain) * (win_ratio / 100) + ((lose_ratio/10) * battles_remain)
        return {'profit': gthc, 'currency': "gTHC", 'stock_price': 0.5}

    def _hero_usd_earnings(self, hero_rarity, battles_remain, purchased):
        thc_price = self._config.get('thc_price')
        # thg_price = self._config.get('thg_price')
        # purchased = self._config.get('purchased')
        gthc = self._hero_gthc_earnings(hero_rarity, battles_remain).get('profit')
        fee = (gthc * self.fee) * thc_price
        profit = (gthc * thc_price) - fee
        return {'profit': profit - purchased, 'currency': 'USD'}

    def _thc_price_settings_input(self):
        price = self._config.get('thc_price')
        return price

    def _thg_price_settings_input(self):
        price = self._config.get('thg_price')
        return price
