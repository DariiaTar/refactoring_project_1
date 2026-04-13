"""
tests/test_cases.py
Юніт-тести для рефакторизованого магазину кросівок.
Запуск: python -m unittest tests/test_cases.py -v
"""

import sys, os, unittest, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from refactored_code import (
    SneakerShop, Shoe, ShoeVariant, Customer, Cart, CartItem, OrderItem,
    STATUS_PENDING, STATUS_CONFIRMED, STATUS_DELIVERED, STATUS_CANCELLED,
    DELIVERY_COURIER, DELIVERY_NOVA_POSHTA, DELIVERY_PICKUP,
    PROMO_PERCENT, PROMO_FIXED,
    TIER_BRONZE, TIER_SILVER, TIER_GOLD, TIER_PLATINUM,
    RETURN_DAYS_LIMIT, BONUS_RATE,
)


class TestShoeVariant(unittest.TestCase):

    def setUp(self):
        self.variant = ShoeVariant(42, 3300)

    def test_new_variant_has_zero_stock(self):
        """Тест 1: Новий варіант має нульовий залишок."""
        self.assertEqual(self.variant.in_stock, 0)
        self.assertFalse(self.variant.is_available())

    def test_restock_increases_stock(self):
        """Тест 2: restock збільшує залишок."""
        self.variant.restock(10)
        self.assertEqual(self.variant.in_stock, 10)
        self.assertTrue(self.variant.is_available())

    def test_reserve_reduces_stock_and_increases_sold(self):
        """Тест 3: reserve зменшує in_stock і збільшує sold."""
        self.variant.restock(10)
        self.variant.reserve(3)
        self.assertEqual(self.variant.in_stock, 7)
        self.assertEqual(self.variant.sold, 3)

    def test_restore_reverses_reserve(self):
        """Тест 4: restore повертає залишок при скасуванні."""
        self.variant.restock(10)
        self.variant.reserve(4)
        self.variant.restore(4)
        self.assertEqual(self.variant.in_stock, 10)
        self.assertEqual(self.variant.sold, 0)


class TestShoe(unittest.TestCase):

    def setUp(self):
        self.shoe = Shoe("SH0001","Nike","Air Max 90","White/Red","lifestyle","M","шкіра")

    def test_name_property(self):
        """Тест 5: name повертає бренд + модель."""
        self.assertEqual(self.shoe.name, "Nike Air Max 90")

    def test_avg_rating_no_ratings(self):
        """Тест 6: avg_rating повертає None без оцінок."""
        self.assertIsNone(self.shoe.avg_rating)

    def test_avg_rating_calculated(self):
        """Тест 7: avg_rating правильно рахує середнє."""
        self.shoe.ratings = [4, 5, 3]
        self.assertAlmostEqual(self.shoe.avg_rating, 4.0)

    def test_get_variant_found(self):
        """Тест 8: get_variant знаходить існуючий варіант."""
        self.shoe.add_variant(42, 3300)
        v = self.shoe.get_variant(42)
        self.assertIsNotNone(v)
        self.assertEqual(v.price, 3300)

    def test_get_variant_missing(self):
        """Тест 9: get_variant повертає None для відсутнього розміру."""
        self.assertIsNone(self.shoe.get_variant(99))


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("C00001","Олена","Коваль","olena@gmail.com","050")

    def test_initial_tier_is_bronze(self):
        """Тест 10: Новий клієнт має рівень bronze."""
        self.assertEqual(self.customer.tier, TIER_BRONZE)

    def test_tier_becomes_silver(self):
        """Тест 11: При витратах 8000+ рівень стає silver."""
        self.customer.total_spent = 8000
        self.customer.recalculate_tier()
        self.assertEqual(self.customer.tier, TIER_SILVER)

    def test_tier_becomes_gold(self):
        """Тест 12: При витратах 20000+ рівень стає gold."""
        self.customer.total_spent = 20000
        self.customer.recalculate_tier()
        self.assertEqual(self.customer.tier, TIER_GOLD)

    def test_tier_becomes_platinum(self):
        """Тест 13: При витратах 50000+ рівень стає platinum."""
        self.customer.total_spent = 50000
        self.customer.recalculate_tier()
        self.assertEqual(self.customer.tier, TIER_PLATINUM)

    def test_earn_bonus_one_percent(self):
        """Тест 14: earn_bonus нараховує BONUS_RATE від суми."""
        earned = self.customer.earn_bonus(10000)
        self.assertEqual(earned, round(10000 * BONUS_RATE))
        self.assertEqual(self.customer.bonus_points, earned)

    def test_use_bonus_capped_at_10_percent(self):
        """Тест 15: use_bonus обмежений 10% від суми замовлення."""
        self.customer.bonus_points = 5000
        spent = self.customer.use_bonus(1000)
        self.assertEqual(spent, 100)
        self.assertEqual(self.customer.bonus_points, 4900)

    def test_cancel_bonus_no_negative(self):
        """Тест 16: cancel_bonus не дає від'ємних бонусів."""
        self.customer.bonus_points = 50
        self.customer.cancel_bonus(200)
        self.assertEqual(self.customer.bonus_points, 0)


class TestCart(unittest.TestCase):

    def setUp(self):
        self.cart = Cart("C00001")

    def test_new_cart_is_empty(self):
        """Тест 17: Новий кошик порожній."""
        self.assertTrue(self.cart.is_empty())
        self.assertEqual(self.cart.total(), 0)

    def test_find_item(self):
        """Тест 18: find_item знаходить товар у кошику."""
        self.cart.items.append(CartItem("SH0001",42,1,3300))
        self.assertIsNotNone(self.cart.find_item("SH0001",42))

    def test_find_item_missing(self):
        """Тест 19: find_item повертає None для відсутнього."""
        self.assertIsNone(self.cart.find_item("SH9999",42))

    def test_remove_item(self):
        """Тест 20: remove_item видаляє товар."""
        self.cart.items.append(CartItem("SH0001",42,1,3300))
        self.assertTrue(self.cart.remove_item("SH0001",42))
        self.assertTrue(self.cart.is_empty())

    def test_total(self):
        """Тест 21: total() правильно підраховує суму."""
        self.cart.items.append(CartItem("SH0001",42,2,3300))
        self.cart.items.append(CartItem("SH0002",38,1,4100))
        self.assertEqual(self.cart.total(), 10700)

    def test_clear(self):
        """Тест 22: clear() очищає кошик."""
        self.cart.items.append(CartItem("SH0001",42,1,3300))
        self.cart.clear()
        self.assertTrue(self.cart.is_empty())


class TestSneakerShop(unittest.TestCase):

    def setUp(self):
        self.shop = SneakerShop()
        self.shop.add_shoe("Nike","Air Max 90","White/Red",
                           {42:3300,43:3400},"lifestyle","M","шкіра")
        self.shop.add_shoe("Adidas","Stan Smith","White/Green",
                           {38:2200,39:2300},"lifestyle","U","шкіра")
        self.shop.restock("SH0001",42,10)
        self.shop.restock("SH0001",43,5)
        self.shop.restock("SH0002",38,8)
        self.shop.register_customer("Олена","Коваль","olena@gmail.com","050")
        self.shop.register_customer("Іван","Петренко","ivan@gmail.com","067")
        self.shop.add_address("C00001","Київ","Хрещатик","1",is_default=True)

    def test_add_shoe(self):
        """Тест 23: add_shoe додає нову модель."""
        self.assertEqual(len(self.shop.inventory), 2)
        self.assertIsNotNone(self.shop._find_shoe("SH0001"))

    def test_add_shoe_updates_existing(self):
        """Тест 24: Повторне додавання оновлює ціни."""
        self.shop.add_shoe("Nike","Air Max 90","White/Red",{42:3500},"lifestyle","M","шкіра")
        self.assertEqual(len(self.shop.inventory), 2)
        v = self.shop._find_shoe("SH0001").get_variant(42)
        self.assertEqual(v.price, 3500)

    def test_restock(self):
        """Тест 25: restock збільшує залишок."""
        self.shop.restock("SH0001",42,5)
        v = self.shop._find_shoe("SH0001").get_variant(42)
        self.assertEqual(v.in_stock, 15)

    def test_register_customer(self):
        """Тест 26: register_customer додає клієнта."""
        cid = self.shop.register_customer("Аліна","Бонд","alina@gmail.com","093")
        self.assertIsNotNone(cid)
        self.assertEqual(len(self.shop.customers), 3)

    def test_register_duplicate_email(self):
        """Тест 27: Дублікат email не реєструється."""
        result = self.shop.register_customer("Копія","Юзер","olena@gmail.com","000")
        self.assertIsNone(result)
        self.assertEqual(len(self.shop.customers), 2)

    def test_add_to_cart(self):
        """Тест 28: add_to_cart додає товар до кошика."""
        self.shop.add_to_cart("C00001","SH0001",42,1)
        cart = self.shop._get_cart("C00001")
        self.assertEqual(len(cart.items), 1)

    def test_add_to_cart_unavailable(self):
        """Тест 29: add_to_cart відхиляє недоступний розмір."""
        self.shop.add_to_cart("C00001","SH0001",99,1)
        self.assertTrue(self.shop._get_cart("C00001").is_empty())

    def test_remove_from_cart(self):
        """Тест 30: remove_from_cart видаляє товар."""
        self.shop.add_to_cart("C00001","SH0001",42)
        self.shop.remove_from_cart("C00001","SH0001",42)
        self.assertTrue(self.shop._get_cart("C00001").is_empty())

    def test_place_order_success(self):
        """Тест 31: place_order успішно створює замовлення."""
        self.shop.add_to_cart("C00001","SH0001",42)
        oid = self.shop.place_order("C00001", DELIVERY_COURIER)
        self.assertIsNotNone(oid)
        self.assertEqual(len(self.shop.orders), 1)

    def test_place_order_reduces_stock(self):
        """Тест 32: place_order зменшує залишок."""
        self.shop.add_to_cart("C00001","SH0001",42,3)
        self.shop.place_order("C00001", DELIVERY_PICKUP)
        v = self.shop._find_shoe("SH0001").get_variant(42)
        self.assertEqual(v.in_stock, 7)

    def test_place_order_empty_cart(self):
        """Тест 33: place_order з порожнім кошиком повертає None."""
        self.assertIsNone(self.shop.place_order("C00001", DELIVERY_PICKUP))

    def test_order_delivered_increases_spent(self):
        """Тест 34: STATUS_DELIVERED збільшує total_spent клієнта."""
        self.shop.add_to_cart("C00001","SH0001",42)
        oid = self.shop.place_order("C00001", DELIVERY_PICKUP)
        self.shop.update_order_status(oid, STATUS_DELIVERED)
        customer = self.shop._find_customer("C00001")
        self.assertGreater(customer.total_spent, 0)

    def test_order_cancelled_restores_stock(self):
        """Тест 35: Скасування повертає товар на склад."""
        self.shop.add_to_cart("C00001","SH0001",42,2)
        oid = self.shop.place_order("C00001", DELIVERY_PICKUP)
        stock_before = self.shop._find_shoe("SH0001").get_variant(42).in_stock
        self.shop.update_order_status(oid, STATUS_CANCELLED)
        stock_after = self.shop._find_shoe("SH0001").get_variant(42).in_stock
        self.assertEqual(stock_after, stock_before + 2)

    def test_promo_percent(self):
        """Тест 36: Процентна знижка."""
        self.shop.create_promo("T10",10,PROMO_PERCENT,min_order=0)
        disc = self.shop.apply_promo("T10",10000,"C00001")
        self.assertEqual(disc, 1000)

    def test_promo_fixed(self):
        """Тест 37: Фіксована знижка."""
        self.shop.create_promo("F500",500,PROMO_FIXED,min_order=0)
        disc = self.shop.apply_promo("F500",10000,"C00001")
        self.assertEqual(disc, 500)

    def test_promo_min_order_not_met(self):
        """Тест 38: Промокод не спрацьовує при малій сумі."""
        self.shop.create_promo("BIG",10,PROMO_PERCENT,min_order=5000)
        disc = self.shop.apply_promo("BIG",1000,"C00001")
        self.assertEqual(disc, 0)

    def test_promo_used_twice(self):
        """Тест 39: Промокод не можна використати двічі."""
        self.shop.create_promo("ONCE",10,PROMO_PERCENT)
        promo = self.shop._find_promo("ONCE")
        promo.mark_used("C00001")
        disc = self.shop.apply_promo("ONCE",5000,"C00001")
        self.assertEqual(disc, 0)

    def test_search_by_brand(self):
        """Тест 40: search_shoes фільтрує за брендом."""
        results = self.shop.search_shoes(brand="Nike",in_stock=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['shoe'].brand,"Nike")

    


if __name__ == "__main__":
    unittest.main(verbosity=2)
