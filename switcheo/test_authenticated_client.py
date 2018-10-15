import unittest
import time
from switcheo.neo.utils import open_wallet
from switcheo.authenticated_client import AuthenticatedClient


ac = AuthenticatedClient(blockchain='neo')
testnet_privatekey_hexstring = '70f642894bc73dc50013be6d1dbe198f43237eaf9458d193c0b416c5385d9717'
kp = open_wallet(testnet_privatekey_hexstring)


class TestAuthenticatedClient(unittest.TestCase):

    def test_deposit(self):
        deposited_dict = {'result': 'ok'}
        self.assertDictEqual(ac.deposit(asset="SWTH", amount=0.000001, kp=kp), deposited_dict)
        self.assertDictEqual(ac.deposit(asset="GAS", amount=0.000001, kp=kp), deposited_dict)

    def test_withdrawal(self):
        swth_withdrawn_dict = {
            'event_type': 'withdrawal',
            'amount': -100,
            'asset_id': 'ab38352559b8b203bde5fddfa0b07d8b2525e132',
            'blockchain': 'neo',
            'reason_code': 9,
            'address': 'fea2b883725ef2d194c9060f606cd0a0468a2c59',
            'transaction_hash': None,
            'contract_hash': 'a195c1549e7da61b8da315765a790ac7e7633b82',
            'approval_transaction_hash': None
        }
        swth_withdrawal_dict = ac.withdrawal(asset="SWTH", amount=0.000001, kp=kp)
        swth_withdrawal_dict.pop('id')
        swth_withdrawal_dict.pop('status')
        swth_withdrawal_dict.pop('created_at')
        swth_withdrawal_dict.pop('updated_at')
        self.assertDictEqual(swth_withdrawal_dict, swth_withdrawn_dict)

        gas_withdrawn_dict = {
            'event_type': 'withdrawal',
            'amount': -100,
            'asset_id': '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7',
            'blockchain': 'neo',
            'reason_code': 9,
            'address': 'fea2b883725ef2d194c9060f606cd0a0468a2c59',
            'transaction_hash': None,
            'contract_hash': 'a195c1549e7da61b8da315765a790ac7e7633b82',
            'approval_transaction_hash': None
        }
        gas_withdrawal_dict = ac.withdrawal(asset="GAS", amount=0.000001, kp=kp)
        gas_withdrawal_dict.pop('id')
        gas_withdrawal_dict.pop('status')
        gas_withdrawal_dict.pop('created_at')
        gas_withdrawal_dict.pop('updated_at')
        self.assertDictEqual(gas_withdrawal_dict, gas_withdrawn_dict)

    def test_create_and_cancel_order(self):
        order = ac.order(kp=kp, pair="SWTH_NEO", side="buy",
                         price=0.0001, amount=100,
                         use_native_token=True, order_type="limit")
        ac.cancel_order(order_id=order['id'], kp=kp)
        testnet_scripthash = 'fea2b883725ef2d194c9060f606cd0a0468a2c59'
        cancelled = False
        for trade in ac.get_orders(address=testnet_scripthash):
            if trade['id'] == order['id'] and\
                    trade['status'] == 'processed' and\
                    trade['makes'][0]['status'] in ['cancelled', 'cancelling']:
                cancelled = True
        self.assertTrue(cancelled)

    def test_order_filter(self):
        # Test side filter
        with self.assertRaises(ValueError):
            ac.order(kp=kp, pair="SWTH_NEO", side="test",
                     price=0.0001, amount=100,
                     use_native_token=True, order_type="limit")
        # Test order_type filter
        with self.assertRaises(ValueError):
            ac.order(kp=kp, pair="SWTH_NEO", side="buy",
                     price=0.0001, amount=100,
                     use_native_token=True, order_type="test")
