from unittest import TestCase


class TestChainflipUtils(TestCase):

    def setUp(self) -> None:
        import chainflip_perseverance.utils.format as utils
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
        formatted_amount = self.utils.amount_in_asset('Eth', 1.0)
        self.assertEqual(formatted_amount, 1000000000000000000)

        formatted_amount = self.utils.amount_in_asset('ETH', 1.0)
        self.assertEqual(formatted_amount, 1000000000000000000)

        formatted_amount = self.utils.amount_in_asset('Eth', 0.1)
        self.assertEqual(formatted_amount, 100000000000000000)

        formatted_amount = self.utils.amount_in_asset('eth', 0.4732112)
        self.assertEqual(formatted_amount, 473211200000000000)

    def test_format_amount_btc(self):
        formatted_amount = self.utils.amount_in_asset('Btc', 1.0)
        self.assertEqual(formatted_amount, 100000000)

        formatted_amount = self.utils.amount_in_asset('BTC', 1.0)
        self.assertEqual(formatted_amount, 100000000)

        formatted_amount = self.utils.amount_in_asset('Btc', 0.1)
        self.assertEqual(formatted_amount, 10000000)

        formatted_amount = self.utils.amount_in_asset('btc', 0.4732112)
        self.assertEqual(formatted_amount, 47321120)

    def test_format_amount_dot(self):
        formatted_amount = self.utils.amount_in_asset('Dot', 1.0)
        self.assertEqual(formatted_amount, 10000000000)

        formatted_amount = self.utils.amount_in_asset('DOT', 1.0)
        self.assertEqual(formatted_amount, 10000000000)

        formatted_amount = self.utils.amount_in_asset('Dot', 0.1)
        self.assertEqual(formatted_amount, 1000000000)

        formatted_amount = self.utils.amount_in_asset('dot', 0.4732112)
        self.assertEqual(formatted_amount, 4732112000)

    def test_format_amount_usdc(self):
        formatted_amount = self.utils.amount_in_asset('Usdc', 1.0)
        self.assertEqual(formatted_amount, 1000000)

        formatted_amount = self.utils.amount_in_asset('USDC', 1.0)
        self.assertEqual(formatted_amount, 1000000)

        formatted_amount = self.utils.amount_in_asset('Usdc', 0.1)
        self.assertEqual(formatted_amount, 100000)

        formatted_amount = self.utils.amount_in_asset('usdc', 0.4732112)
        self.assertEqual(formatted_amount, 473211)

    def test_format_price_to_sqrt_price_eth(self):
        sqrt_price_x_96 = self.utils.calculate_sqrt_price(1888.9727296834467, 'Eth')
        self.assertEqual(sqrt_price_x_96, 3443439269043971020554240)

        sqrt_price_x_96 = self.utils.calculate_sqrt_price(1140.3045984164828, 'Eth')
        self.assertEqual(sqrt_price_x_96, 2675408001331668950450176)

    def test_format_sqrt_price_x96_to_price_eth(self):
        price = self.utils.calculate_price_from_sqrt_price(3443439269043970780644209, 'Eth')
        self.assertAlmostEqual(price, 1888.9727296834467, 6)

        price = self.utils.calculate_price_from_sqrt_price(2675408001331669207632817, 'Eth')
        self.assertAlmostEqual(price, 1140.3045984164828, 6)

    def test_format_price_to_tick_eth(self):
        tick = self.utils.price_to_tick(1000.00, 'Eth')
        self.assertEqual(tick, -207244)

        tick = self.utils.price_to_tick(2000.00, 'Eth')
        self.assertEqual(tick, -200312)

        tick = self.utils.price_to_tick(1800.32, 'Eth')
        self.assertEqual(tick, -201364)

        tick = self.utils.price_to_tick(4780.73, 'Eth')
        self.assertEqual(tick, -191597)

        tick = self.utils.price_to_tick(4993.77, 'Eth')
        self.assertEqual(tick, -191161)

    def test_format_tick_to_price_eth(self):
        price = self.utils.tick_to_price(-207244, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 999.90199267)

        price = self.utils.tick_to_price(-200312, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 1999.8403056)

        price = self.utils.tick_to_price(-201364, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 1800.1546715)

        price = self.utils.tick_to_price(-191597, 'Eth', 'Usdc')
        self.assertAlmostEqual(price, 4780.3977679)

    def test_format_price_to_sqrt_price_btc(self):
        sqrt_price_x_96 = self.utils.calculate_sqrt_price(10000, 'Btc')
        self.assertEqual(sqrt_price_x_96, 792281625142643375935439503360)

        sqrt_price_x_96 = self.utils.calculate_sqrt_price(30513.21, 'Btc')
        self.assertEqual(sqrt_price_x_96, 1383959982959110770043383709696)

    def test_format_sqrt_price_x96_to_price_btc(self):
        price = self.utils.calculate_price_from_sqrt_price(792281625142643375935439503360, 'Btc')
        self.assertAlmostEqual(price, 10000, 6)

        price = self.utils.calculate_price_from_sqrt_price(1383959982959110770043383709696, 'Btc')
        self.assertAlmostEqual(price, 30513.21, 6)

    def test_format_price_to_tick_btc(self):
        tick = self.utils.price_to_tick(30000, 'Btc')
        self.assertEqual(tick, 57040)

        tick = self.utils.price_to_tick(10000, 'Btc')
        self.assertEqual(tick, 46054)

        tick = self.utils.price_to_tick(25603.86, 'Btc')
        self.assertEqual(tick, 55456)

        tick = self.utils.price_to_tick(65125.35, 'Btc')
        self.assertEqual(tick, 64792)

    def test_format_tick_to_price_btc(self):
        price = self.utils.tick_to_price(57040, 'Btc', 'Usdc')
        self.assertAlmostEqual(price, 29997.9703993)

        price = self.utils.tick_to_price(46054, 'Btc', 'Usdc')
        self.assertAlmostEqual(price, 9999.99559361)

        price = self.utils.tick_to_price(55456, 'Btc', 'Usdc')
        self.assertAlmostEqual(price, 25603.71979672)

        price = self.utils.tick_to_price(64792, 'Btc', 'Usdc')
        self.assertEqual(price, 65123.85827285656)

    def test_format_price_to_sqrt_price_dot(self):
        sqrt_price_x_96 = self.utils.calculate_sqrt_price(10, 'Dot')
        self.assertEqual(sqrt_price_x_96, 2505414483750479155158843392)

        sqrt_price_x_96 = self.utils.calculate_sqrt_price(5.63, 'Dot')
        self.assertEqual(sqrt_price_x_96, 1879895815470288748702334976)

    def test_format_sqrt_price_x96_to_price_dot(self):
        price = self.utils.calculate_price_from_sqrt_price(2505414483750479155158843392, 'Dot')
        self.assertAlmostEqual(price, 10, 6)

        price = self.utils.calculate_price_from_sqrt_price(1879895815470288748702334976, 'Dot')
        self.assertAlmostEqual(price, 5.63, 6)

    def test_format_price_to_tick_dot(self):
        tick = self.utils.price_to_tick(10, 'Dot')
        self.assertEqual(tick, -69082)

        tick = self.utils.price_to_tick(5, 'Dot')
        self.assertEqual(tick, -76013)

        tick = self.utils.price_to_tick(8.256, 'Dot')
        self.assertEqual(tick, -70998)

        tick = self.utils.price_to_tick(4.48, 'Dot')
        self.assertEqual(tick, -77112)

    def test_format_tick_to_price_dot(self):
        price = self.utils.tick_to_price(-69082, 'Dot', 'Usdc')
        self.assertAlmostEqual(price, 9.99900670)

        price = self.utils.tick_to_price(-76013, 'Dot', 'Usdc')
        self.assertAlmostEqual(price, 4.999912496)

        price = self.utils.tick_to_price(-70998, 'Dot', 'Usdc')
        self.assertAlmostEqual(price, 8.255629558)

        price = self.utils.tick_to_price(-77112, 'Dot', 'Usdc')
        self.assertAlmostEqual(price, 4.479564833)

    def test_format_price_from_hex(self):
        price = self.utils.u256_fixed_to_float('0x44b82fa09b5a53ffffffd38ad', 'Eth')
        self.assertAlmostEqual(price, 1000.00)

        price = self.utils.u256_fixed_to_float('0x6400000000000000000000000000000000', 'Btc')
        self.assertEqual(price, 10000.0)

        price = self.utils.u256_fixed_to_float('0x813103d1b24adfffffffaa5d8', 'Eth')
        self.assertAlmostEqual(price, 1879.98324)

        price = self.utils.u256_fixed_to_float('0x12c0a85bd43c2cffffffffffff2d74584bc', 'Btc')
        self.assertEqual(price, 30004.11032)
