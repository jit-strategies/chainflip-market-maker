from unittest import TestCase


class TestChainflipUtils(TestCase):

    def setUp(self) -> None:
        import chainflip_partnernet.utils.format as utils
        self.utils = utils

    def test_format_asset_str(self):
        formatted_asset = self.utils.asset_to_str('ETH')
        self.assertEqual(formatted_asset, 'Eth')

        formatted_asset = self.utils.asset_to_str('btc')
        self.assertEqual(formatted_asset, 'Btc')

        formatted_asset = self.utils.asset_to_str('DoT')
        self.assertEqual(formatted_asset, 'Dot')

        formatted_asset = self.utils.asset_to_str('UsdC')
        self.assertEqual(formatted_asset, 'Usdc')

    def test_format_amount_eth(self):
        formatted_amount = self.utils.asset_to_amount('Eth', 1.0)
        self.assertEqual(formatted_amount, 1000000000000000000)

        formatted_amount = self.utils.asset_to_amount('ETH', 1.0)
        self.assertEqual(formatted_amount, 1000000000000000000)

        formatted_amount = self.utils.asset_to_amount('Eth', 0.1)
        self.assertEqual(formatted_amount, 100000000000000000)

        formatted_amount = self.utils.asset_to_amount('eth', 0.4732112)
        self.assertEqual(formatted_amount, 473211200000000000)

    def test_format_amount_btc(self):
        formatted_amount = self.utils.asset_to_amount('Btc', 1.0)
        self.assertEqual(formatted_amount, 100000000)

        formatted_amount = self.utils.asset_to_amount('BTC', 1.0)
        self.assertEqual(formatted_amount, 100000000)

        formatted_amount = self.utils.asset_to_amount('Btc', 0.1)
        self.assertEqual(formatted_amount, 10000000)

        formatted_amount = self.utils.asset_to_amount('btc', 0.4732112)
        self.assertEqual(formatted_amount, 47321120)

    def test_format_amount_dot(self):
        formatted_amount = self.utils.asset_to_amount('Dot', 1.0)
        self.assertEqual(formatted_amount, 10000000000)

        formatted_amount = self.utils.asset_to_amount('DOT', 1.0)
        self.assertEqual(formatted_amount, 10000000000)

        formatted_amount = self.utils.asset_to_amount('Dot', 0.1)
        self.assertEqual(formatted_amount, 1000000000)

        formatted_amount = self.utils.asset_to_amount('dot', 0.4732112)
        self.assertEqual(formatted_amount, 4732112000)

    def test_format_amount_usdc(self):
        formatted_amount = self.utils.asset_to_amount('Usdc', 1.0)
        self.assertEqual(formatted_amount, 1000000)

        formatted_amount = self.utils.asset_to_amount('USDC', 1.0)
        self.assertEqual(formatted_amount, 1000000)

        formatted_amount = self.utils.asset_to_amount('Usdc', 0.1)
        self.assertEqual(formatted_amount, 100000)

        formatted_amount = self.utils.asset_to_amount('usdc', 0.4732112)
        self.assertEqual(formatted_amount, 473211)

    def test_format_price_to_sqrt_price(self):
        sqrt_price_x_96 = self.utils.calculate_sqrt_price(1888.9727296834467, 'Eth')
        self.assertEqual(sqrt_price_x_96, 3443439269043970974615269)

        sqrt_price_x_96 = self.utils.calculate_sqrt_price(1140.3045984164828, 'Eth')
        self.assertEqual(sqrt_price_x_96, 2675408001331669207632817)

    def test_format_sqrt_price_x96_to_price(self):
        price = self.utils.calculate_price_from_sqrt_price(3443439269043970780644209, 'Eth')
        self.assertAlmostEqual(price, 1888.9727296834467, 6)

        price = self.utils.calculate_price_from_sqrt_price(2675408001331669207632817, 'Eth')
        self.assertAlmostEqual(price, 1140.3045984164828, 6)

    def test_format_price_to_tick(self):
        tick = self.utils.price_to_tick('Eth', 1888.53)
        self.assertEqual(tick, -200884)

        tick = self.utils.price_to_tick('Eth', 1847.64)
        self.assertEqual(tick, -201104)

        tick = self.utils.price_to_tick('Eth', 1140.23)
        self.assertEqual(tick, -205930)

        tick = self.utils.price_to_tick('Eth', 3306.97)
        self.assertEqual(tick, -195282)

    def test_format_tick_to_price(self):
        price = self.utils.tick_to_price(-205930, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 1140.304598, 6)

        price = self.utils.tick_to_price(-200697, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 1924.3134505, 6)

        price = self.utils.tick_to_price(-201104, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 1847.5700512, 6)

        price = self.utils.tick_to_price(257109, 'Btc', 'Eth')
        self.assertAlmostEqual(price, 14.64008933677512)
