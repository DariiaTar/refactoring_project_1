import datetime
from typing import Optional


# =============================================================================
# Техніка 1: Replace Magic Number with Symbolic Constant
# Усі числа і рядки-статуси замінені на іменовані константи
# =============================================================================

BONUS_RATE        = 0.01   # 1% від суми — нараховується бонус
BONUS_MAX_SPEND   = 0.10   # до 10% суми можна сплатити бонусами
RETURN_DAYS_LIMIT = 14     # максимум 14 днів для повернення

DELIVERY_COURIER     = 'courier'
DELIVERY_NOVA_POSHTA = 'novaposhta'
DELIVERY_PICKUP      = 'pickup'

DELIVERY_COSTS = {
    DELIVERY_COURIER:     99,
    DELIVERY_NOVA_POSHTA: 59,
    DELIVERY_PICKUP:       0,
}

STATUS_PENDING   = 'pending'
STATUS_CONFIRMED = 'confirmed'
STATUS_SHIPPED   = 'shipped'
STATUS_DELIVERED = 'delivered'
STATUS_CANCELLED = 'cancelled'
VALID_STATUSES   = {STATUS_PENDING, STATUS_CONFIRMED, STATUS_SHIPPED,
                    STATUS_DELIVERED, STATUS_CANCELLED}

TIER_BRONZE   = 'bronze'
TIER_SILVER   = 'silver'
TIER_GOLD     = 'gold'
TIER_PLATINUM = 'platinum'

PROMO_PERCENT = 'percent'
PROMO_FIXED   = 'fixed'


# =============================================================================
# Техніка 2: Replace Array with Object
# v[0]=розмір, v[1]=ціна, v[2]=кількість, v[3]=продано → клас ShoeVariant
# =============================================================================

class ShoeVariant:
    """Один варіант кросівки: розмір, ціна, залишок на складі."""

    def __init__(self, size: float, price: int):
        self.size     = size
        self.price    = price
        self.in_stock = 0
        self.sold     = 0

    def is_available(self) -> bool:
        return self.in_stock > 0

    def reserve(self, qty: int) -> None:
        self.in_stock -= qty
        self.sold     += qty

    def restore(self, qty: int) -> None:
        self.in_stock += qty
        self.sold     -= qty

    def restock(self, qty: int) -> None:
        self.in_stock += qty


class Shoe:
    """Модель кросівки з усіма варіантами розмірів."""

    def __init__(self, shoe_id: str, brand: str, model: str, colorway: str,
                 category: str, gender: str, material: str):
        self.shoe_id   = shoe_id
        self.brand     = brand
        self.model     = model
        self.colorway  = colorway
        self.category  = category
        self.gender    = gender
        self.material  = material
        self.variants: list[ShoeVariant] = []
        self.ratings:  list[int]         = []
        self.active    = True
        self.created   = datetime.datetime.now()

    @property
    def name(self) -> str:
        return f"{self.brand} {self.model}"

    @property
    def avg_rating(self) -> Optional[float]:
        if not self.ratings:
            return None
        return round(sum(self.ratings) / len(self.ratings), 1)

    def get_variant(self, size: float) -> Optional[ShoeVariant]:
        for v in self.variants:
            if v.size == size:
                return v
        return None

    def add_variant(self, size: float, price: int) -> ShoeVariant:
        v = ShoeVariant(size, price)
        self.variants.append(v)
        return v


class Customer:
    """Покупець магазину."""

    def __init__(self, customer_id: str, first_name: str, last_name: str,
                 email: str, phone: str, birthdate: str = None):
        self.customer_id  = customer_id
        self.full_name    = f"{first_name} {last_name}"
        self.email        = email
        self.phone        = phone
        self.birthdate    = birthdate
        self.registered   = datetime.datetime.now()
        self.order_ids:   list[str]  = []
        self.wishlist:    list[str]  = []
        self.addresses:   list[dict] = []
        self.total_spent  = 0
        self.bonus_points = 0
        self.tier         = TIER_BRONZE
        self.active       = True

    # =========================================================================
    # Техніка 3: Move Method
    # Логіка рівня і бонусів перенесена сюди з placeOrder/updateOrderStatus
    # =========================================================================

    def recalculate_tier(self) -> None:
        if self.total_spent >= 50_000:
            self.tier = TIER_PLATINUM
        elif self.total_spent >= 20_000:
            self.tier = TIER_GOLD
        elif self.total_spent >= 8_000:
            self.tier = TIER_SILVER
        else:
            self.tier = TIER_BRONZE

    def earn_bonus(self, amount: int) -> int:
        earned = round(amount * BONUS_RATE)
        self.bonus_points += earned
        return earned

    def use_bonus(self, order_total: int) -> int:
        cap = round(order_total * BONUS_MAX_SPEND)
        spent = min(self.bonus_points, cap)
        self.bonus_points -= spent
        return spent

    def cancel_bonus(self, amount: int) -> None:
        self.bonus_points = max(0, self.bonus_points - amount)


# =============================================================================
# Техніка 2 (продовження): Replace Array with Object
# item[0], item[1], item[2], item[3] → клас OrderItem із зрозумілими полями
# =============================================================================

class OrderItem:
    """Рядок замовлення."""

    def __init__(self, shoe_id: str, size: float, qty: int, price: int,
                 brand: str, model: str):
        self.shoe_id = shoe_id
        self.size    = size
        self.qty     = qty
        self.price   = price
        self.brand   = brand
        self.model   = model

    @property
    def subtotal(self) -> int:
        return self.price * self.qty

    @property
    def label(self) -> str:
        return f"{self.brand} {self.model} р.{self.size}"


class CartItem:
    """Рядок кошика."""

    def __init__(self, shoe_id: str, size: float, qty: int, price: int):
        self.shoe_id = shoe_id
        self.size    = size
        self.qty     = qty
        self.price   = price

    @property
    def subtotal(self) -> int:
        return self.price * self.qty


class Cart:
    """Кошик покупця."""

    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.items: list[CartItem] = []
        self.created = datetime.datetime.now()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def total(self) -> int:
        return sum(item.subtotal for item in self.items)

    def find_item(self, shoe_id: str, size: float) -> Optional[CartItem]:
        for item in self.items:
            if item.shoe_id == shoe_id and item.size == size:
                return item
        return None

    def remove_item(self, shoe_id: str, size: float) -> bool:
        for i, item in enumerate(self.items):
            if item.shoe_id == shoe_id and item.size == size:
                self.items.pop(i)
                return True
        return False

    def clear(self) -> None:
        self.items = []


class Order:
    """Замовлення клієнта."""

    def __init__(self, order_id: str, customer_id: str, items: list[OrderItem],
                 subtotal: int, delivery_type: str, delivery_cost: int,
                 discount: int, bonus_used: int, bonus_earned: int,
                 total: int, address: dict, promo_code: str):
        self.order_id      = order_id
        self.customer_id   = customer_id
        self.items         = items
        self.subtotal      = subtotal
        self.delivery_type = delivery_type
        self.delivery_cost = delivery_cost
        self.discount      = discount
        self.bonus_used    = bonus_used
        self.bonus_earned  = bonus_earned
        self.total         = total
        self.address       = address
        self.promo_code    = promo_code
        self.status        = STATUS_PENDING
        self.created       = datetime.datetime.now()


class PromoCode:
    """Промокод."""

    def __init__(self, code: str, discount: int, promo_type: str,
                 min_order: int = 0, uses_left: int = None,
                 expiry: datetime.datetime = None):
        self.code       = code
        self.discount   = discount
        self.promo_type = promo_type
        self.min_order  = min_order
        self.uses_left  = uses_left
        self.expiry     = expiry
        self.active     = True
        self.used_by:   list[str] = []

    def is_valid(self) -> bool:
        if not self.active:
            return False
        if self.expiry and datetime.datetime.now() > self.expiry:
            return False
        if self.uses_left is not None and self.uses_left <= 0:
            return False
        return True

    def calculate_discount(self, order_total: int) -> int:
        if self.promo_type == PROMO_PERCENT:
            return round(order_total * self.discount / 100)
        elif self.promo_type == PROMO_FIXED:
            return min(self.discount, order_total)
        return 0

    def mark_used(self, customer_id: str) -> None:
        self.used_by.append(customer_id)
        if self.uses_left is not None:
            self.uses_left -= 1


class Supplier:
    """Постачальник."""

    def __init__(self, supplier_id: str, name: str, country: str,
                 contact: str, markup: int):
        self.supplier_id = supplier_id
        self.name        = name
        self.country     = country
        self.contact     = contact
        self.markup      = markup
        self.active      = True


class ReturnRequest:
    """Заявка на повернення товару."""

    def __init__(self, return_id: str, order_id: str, customer_id: str,
                 items: list, reason: str, refund_amount: int):
        self.return_id     = return_id
        self.order_id      = order_id
        self.customer_id   = customer_id
        self.items         = items
        self.reason        = reason
        self.refund_amount = refund_amount
        self.status        = 'pending'
        self.created       = datetime.datetime.now()


# =============================================================================
# Головний клас магазину
# =============================================================================

class SneakerShop:

    def __init__(self):
        self.inventory:   list[Shoe]          = []
        self.customers:   list[Customer]      = []
        self.orders:      list[Order]         = []
        self.carts:       dict[str, Cart]     = {}
        self.promo_codes: list[PromoCode]     = []
        self.returns:     list[ReturnRequest] = []
        self.suppliers:   list[Supplier]      = []
        self.deliveries:  list[dict]          = []

    # =========================================================================
    # Техніка 4: Extract Method
    # Повторюваний пошук по списках винесено в окремі методи
    # ==========================================================================

    def _find_shoe(self, shoe_id: str) -> Optional[Shoe]:
        for shoe in self.inventory:
            if shoe.shoe_id == shoe_id:
                return shoe
        return None

    def _find_customer(self, customer_id: str) -> Optional[Customer]:
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer
        return None

    def _find_order(self, order_id: str) -> Optional[Order]:
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def _find_promo(self, code: str) -> Optional[PromoCode]:
        for promo in self.promo_codes:
            if promo.code == code:
                return promo
        return None

    def _find_supplier(self, supplier_id: str) -> Optional[Supplier]:
        for s in self.suppliers:
            if s.supplier_id == supplier_id:
                return s
        return None

    def _get_cart(self, customer_id: str) -> Cart:
        if customer_id not in self.carts:
            self.carts[customer_id] = Cart(customer_id)
        return self.carts[customer_id]

    # =========================================================================
    # Техніка 5: Extract Method (продовження)
    # Валідація і резервування товарів виокремлені з place_order
    # ==========================================================================

    def _validate_cart_items(self, cart: Cart) -> Optional[list[OrderItem]]:
        order_items = []
        for item in cart.items:
            shoe = self._find_shoe(item.shoe_id)
            if not shoe:
                print("товар недоступний")
                return None
            variant = shoe.get_variant(item.size)
            if not variant or variant.in_stock < item.qty:
                print(f"недостатньо товару: {shoe.name} р.{item.size}")
                return None
            order_items.append(OrderItem(
                item.shoe_id, item.size, item.qty, item.price,
                shoe.brand, shoe.model,
            ))
        return order_items

    def _reserve_items(self, order_items: list[OrderItem]) -> None:
        for item in order_items:
            shoe = self._find_shoe(item.shoe_id)
            if shoe:
                v = shoe.get_variant(item.size)
                if v:
                    v.reserve(item.qty)

    def _restore_items(self, order: Order) -> None:
        for item in order.items:
            shoe = self._find_shoe(item.shoe_id)
            if shoe:
                v = shoe.get_variant(item.size)
                if v:
                    v.restore(item.qty)

    # =========================================================================
    # Техніка 6: Separate Query from Modifier
    # salesReport() розбито на get_sales_stats() (query) і show_sales_report() (modifier/display)
    # ==========================================================================

    def get_sales_stats(self, days: int = 30) -> dict:
        """Повертає статистику — не друкує нічого."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        stats = {'orders': 0, 'cancelled': 0, 'revenue': 0,
                 'pairs': 0, 'top_id': None, 'top_qty': 0}
        sales: dict[str, int] = {}
        for order in self.orders:
            if order.created < cutoff:
                continue
            stats['orders'] += 1
            if order.status == STATUS_CANCELLED:
                stats['cancelled'] += 1
                continue
            stats['revenue'] += order.total
            for item in order.items:
                stats['pairs'] += item.qty
                sales[item.shoe_id] = sales.get(item.shoe_id, 0) + item.qty
        if sales:
            best = max(sales, key=sales.get)
            stats['top_id']  = best
            stats['top_qty'] = sales[best]
        return stats

    def show_sales_report(self, days: int = 30) -> None:
        """Відображає звіт — викликає query-метод."""
        stats = self.get_sales_stats(days)
        print(f"\n{'='*40}")
        print(f"ЗВІТ ЗА {days} ДНІВ")
        print(f"замовлень: {stats['orders']} (скасовано: {stats['cancelled']})")
        print(f"виручка: {stats['revenue']} грн | пар продано: {stats['pairs']}")
        if stats['top_id']:
            shoe = self._find_shoe(stats['top_id'])
            if shoe:
                print(f"топ товар: {shoe.name} — {stats['top_qty']} пар")

    def get_low_stock(self, threshold: int = 3) -> list[tuple]:
        """Повертає список товарів з малим залишком — не друкує."""
        result = []
        for shoe in self.inventory:
            if not shoe.active:
                continue
            for v in shoe.variants:
                if 0 < v.in_stock <= threshold:
                    result.append((shoe.name, v.size, v.in_stock))
        return result

    def show_low_stock(self, threshold: int = 3) -> None:
        items = self.get_low_stock(threshold)
        print(f"\n{'='*40}")
        print(f"МАЛО НА СКЛАДІ (менше {threshold} шт):")
        if not items:
            print("  все в нормі")
            return
        for name, size, qty in items:
            print(f"  {name} р.{size}: {qty} шт")

    def get_inventory_stats(self) -> dict:
        """Повертає статистику складу — не друкує."""
        lines, total_pairs, total_value = [], 0, 0
        for shoe in self.inventory:
            if not shoe.active:
                continue
            pairs = sum(v.in_stock for v in shoe.variants)
            value = sum(v.price * v.in_stock for v in shoe.variants)
            total_pairs += pairs
            total_value += value
            if pairs > 0:
                lines.append((shoe.name, pairs, value))
        return {'lines': lines, 'total_pairs': total_pairs, 'total_value': total_value}

    def show_inventory_report(self) -> None:
        stats = self.get_inventory_stats()
        print(f"\n{'='*40}\nЗВІТ ПО СКЛАДУ")
        for name, pairs, value in stats['lines']:
            print(f"  {name}: {pairs} пар на {value} грн")
        print(f"ВСЬОГО: {stats['total_pairs']} пар | вартість: {stats['total_value']} грн")

    # =========================================================================
    # Техніка 7: Replace Nested Conditional with Guard Clauses
    # place_order і інші методи: спочатку всі перевірки з раннім return,
    # потім — основна логіка без вкладень
    # ==========================================================================

    def place_order(self, customer_id: str, delivery_type: str,
                    address_idx: int = 0, promo_code: str = None,
                    use_bonus: bool = False) -> Optional[str]:

        # Guard clauses — ранні виходи замість вкладених if-else
        customer = self._find_customer(customer_id)
        if not customer:
            print("клієнта не знайдено")
            return None

        cart = self._get_cart(customer_id)
        if cart.is_empty():
            print("кошик порожній")
            return None

        order_items = self._validate_cart_items(cart)
        if order_items is None:
            return None

        # Основна логіка — без вкладень
        subtotal      = sum(i.subtotal for i in order_items)
        delivery_cost = DELIVERY_COSTS.get(delivery_type, 0)
        total         = subtotal + delivery_cost

        discount = 0
        if promo_code:
            discount = self.apply_promo(promo_code, total, customer_id)
            total   -= discount

        bonus_used = 0
        if use_bonus:
            bonus_used = customer.use_bonus(total)
            total     -= bonus_used

        self._reserve_items(order_items)

        if promo_code and discount > 0:
            promo = self._find_promo(promo_code)
            if promo:
                promo.mark_used(customer_id)

        bonus_earned = customer.earn_bonus(total)
        order_id     = f"ORD{len(self.orders) + 1:06d}"
        address      = customer.addresses[address_idx] if customer.addresses else {}

        order = Order(order_id, customer_id, order_items, subtotal,
                      delivery_type, delivery_cost, discount,
                      bonus_used, bonus_earned, total, address, promo_code)
        self.orders.append(order)
        customer.order_ids.append(order_id)
        customer.recalculate_tier()
        self._get_cart(customer_id).clear()

        print(f"\nзамовлення #{order_id} оформлено!")
        print(f"сума: {subtotal} | доставка: {delivery_cost} | знижка: {discount}")
        print(f"до сплати: {total} грн | бонусів нараховано: +{bonus_earned}")
        return order_id

    def update_order_status(self, order_id: str, new_status: str) -> None:
        # Guard clauses
        if new_status not in VALID_STATUSES:
            print("невірний статус")
            return

        order = self._find_order(order_id)
        if not order:
            print("замовлення не знайдено")
            return
        if order.status == STATUS_CANCELLED:
            print("замовлення вже скасовано")
            return
        if order.status == STATUS_DELIVERED and new_status != STATUS_DELIVERED:
            print("доставлене замовлення не можна змінити")
            return

        old_status    = order.status
        order.status  = new_status

        if new_status == STATUS_CANCELLED:
            self._restore_items(order)
            customer = self._find_customer(order.customer_id)
            if customer:
                customer.cancel_bonus(order.bonus_earned)

        elif new_status == STATUS_DELIVERED:
            customer = self._find_customer(order.customer_id)
            if customer:
                customer.total_spent += order.total
                customer.recalculate_tier()

        print(f"статус оновлено: {old_status} → {new_status}")

    def create_return(self, order_id: str, customer_id: str,
                      items_to_return: list, reason: str) -> None:
        # Guard clauses
        order = self._find_order(order_id)
        if not order or order.customer_id != customer_id:
            print("замовлення не знайдено")
            return
        if order.status != STATUS_DELIVERED:
            print("повернення можливе тільки для доставлених замовлень")
            return
        if (datetime.datetime.now() - order.created).days > RETURN_DAYS_LIMIT:
            print(f"строк повернення вичерпано ({RETURN_DAYS_LIMIT} днів)")
            return

        valid_items, refund = [], 0
        for ret in items_to_return:
            match = next((i for i in order.items
                          if i.shoe_id == ret[0] and i.size == ret[1]), None)
            if match:
                if ret[2] > match.qty:
                    print("кількість перевищує замовлену")
                    return
                valid_items.append(ret)
                refund += match.price * ret[2]

        if not valid_items:
            print("товари не знайдено в замовленні")
            return

        ret_id = f"RET{len(self.returns) + 1:05d}"
        self.returns.append(ReturnRequest(ret_id, order_id, customer_id,
                                          valid_items, reason, refund))
        print(f"заявку створено: {ret_id} | сума повернення: {refund} грн")

    def process_return(self, return_id: str, approve: bool) -> None:
        # Guard clauses
        ret = next((r for r in self.returns if r.return_id == return_id), None)
        if not ret:
            print("заявку не знайдено")
            return
        if ret.status != 'pending':
            print("заявка вже оброблена")
            return

        if approve:
            ret.status = 'approved'
            for item in ret.items:
                shoe = self._find_shoe(item[0])
                if shoe:
                    v = shoe.get_variant(item[1])
                    if v:
                        v.restock(item[2])
            customer = self._find_customer(ret.customer_id)
            if customer:
                customer.earn_bonus(ret.refund_amount)
            print(f"повернення схвалено. до повернення: {ret.refund_amount} грн")
        else:
            ret.status = 'rejected'
            print("повернення відхилено")

    # =========================================================================
    # Техніка 8: Rename Method
    # camelCase → snake_case, скорочення → повні назви
    # newShoe→add_shoe, stockUp→restock, findShoe→search_shoes тощо
    # ==========================================================================

    def add_shoe(self, brand: str, model: str, colorway: str,
                 size_prices: dict, category: str, gender: str,
                 material: str) -> None:
        for shoe in self.inventory:
            if shoe.brand == brand and shoe.model == model and shoe.colorway == colorway:
                for size, price in size_prices.items():
                    v = shoe.get_variant(size)
                    if v:
                        v.price = price
                    else:
                        shoe.add_variant(size, price)
                print(f"оновлено: {brand} {model}")
                return
        shoe_id = f"SH{len(self.inventory) + 1:04d}"
        shoe = Shoe(shoe_id, brand, model, colorway, category, gender, material)
        for size, price in size_prices.items():
            shoe.add_variant(size, price)
        self.inventory.append(shoe)
        print(f"додано: {shoe_id} {brand} {model} {colorway}")

    def restock(self, shoe_id: str, size: float, qty: int,
                supplier_id: str = None) -> None:
        shoe = self._find_shoe(shoe_id)
        if not shoe:
            print("товар не знайдено")
            return
        v = shoe.get_variant(size)
        if v:
            v.restock(qty)
        else:
            v = shoe.add_variant(size, 0)
            v.restock(qty)
            print(f"новий розмір {size} для {shoe_id}")
        if supplier_id:
            self.deliveries.append({
                'shoe': shoe_id, 'size': size, 'qty': qty,
                'supplier': supplier_id, 'date': datetime.datetime.now(),
                'status': 'received',
            })
        print(f"поповнено {shoe_id} розмір {size}: +{qty} шт")

    def search_shoes(self, brand: str = None, category: str = None,
                     gender: str = None, size: float = None,
                     max_price: int = None, in_stock: bool = True) -> list[dict]:
        results = []
        for shoe in self.inventory:
            if not shoe.active:
                continue
            if brand    and brand.lower() not in shoe.brand.lower():
                continue
            if category and shoe.category != category:
                continue
            if gender   and shoe.gender   != gender:
                continue
            matched = [v for v in shoe.variants
                       if (not in_stock or v.is_available())
                       and (size is None or v.size == size)
                       and (max_price is None or v.price <= max_price)]
            if matched:
                results.append({'shoe': shoe, 'variants': matched})
        return results

    def show_shoe(self, shoe_id: str) -> None:
        shoe = self._find_shoe(shoe_id)
        if not shoe:
            print("не знайдено")
            return
        rating = shoe.avg_rating or 'немає'
        print(f"\n{'='*40}")
        print(f"{shoe.brand} {shoe.model} — {shoe.colorway}")
        print(f"категорія: {shoe.category} | стать: {shoe.gender} | матеріал: {shoe.material}")
        print(f"рейтинг: {rating}/5")
        print("наявність:")
        for v in sorted(shoe.variants, key=lambda x: x.size):
            stock = f"{v.in_stock} шт" if v.is_available() else "немає"
            print(f"  розмір {v.size}: {v.price} грн — {stock}")

    def deactivate_shoe(self, shoe_id: str) -> None:
        shoe = self._find_shoe(shoe_id)
        if not shoe:
            print("не знайдено")
            return
        if not shoe.active:
            print("вже неактивний")
            return
        shoe.active = False
        print(f"знято з продажу: {shoe_id}")

    def rate_shoe(self, shoe_id: str, customer_id: str, score: int) -> None:
        # Guard clauses
        if not (1 <= score <= 5):
            print("оцінка від 1 до 5")
            return
        bought = any(
            item.shoe_id == shoe_id
            for order in self.orders
            if order.customer_id == customer_id and order.status == STATUS_DELIVERED
            for item in order.items
        )
        if not bought:
            print("можна оцінити тільки куплений товар")
            return
        shoe = self._find_shoe(shoe_id)
        if shoe:
            shoe.ratings.append(score)
            print(f"дякуємо за відгук! рейтинг: {shoe.avg_rating}")

    def add_supplier(self, name: str, country: str, contact: str, markup: int) -> None:
        if any(s.name == name for s in self.suppliers):
            print("постачальник існує")
            return
        sup_id = f"SUP{len(self.suppliers) + 1:03d}"
        self.suppliers.append(Supplier(sup_id, name, country, contact, markup))
        print(f"постачальника додано: {sup_id} {name}")

    def show_supplier(self, supplier_id: str) -> None:
        s = self._find_supplier(supplier_id)
        if not s:
            print("не знайдено")
            return
        count = sum(1 for d in self.deliveries if d['supplier'] == supplier_id)
        print(f"постачальник: {s.name} | країна: {s.country}")
        print(f"контакт: {s.contact} | націнка: {s.markup}% | поставок: {count}")

    def register_customer(self, first_name: str, last_name: str,
                          email: str, phone: str, birthdate: str = None) -> Optional[str]:
        if any(c.email == email for c in self.customers):
            print("клієнт з таким email вже є")
            return None
        cid = f"C{len(self.customers) + 1:05d}"
        self.customers.append(Customer(cid, first_name, last_name, email, phone, birthdate))
        print(f"реєстрація успішна! ваш id: {cid}")
        return cid

    def add_address(self, customer_id: str, city: str, street: str,
                    building: str, apt: str = None, is_default: bool = False) -> None:
        customer = self._find_customer(customer_id)
        if not customer:
            print("клієнта не знайдено")
            return
        if is_default:
            for addr in customer.addresses:
                addr['default'] = False
        customer.addresses.append({
            'city': city, 'street': street,
            'building': building, 'apt': apt, 'default': is_default,
        })
        print("адресу додано")

    def show_customer(self, customer_id: str) -> None:
        customer = self._find_customer(customer_id)
        if not customer:
            print("клієнта не знайдено")
            return
        print(f"\n{'='*40}")
        print(f"клієнт: {customer.full_name}")
        print(f"email: {customer.email} | тел: {customer.phone}")
        print(f"рівень: {customer.tier} | бонуси: {customer.bonus_points}")
        print(f"замовлень: {len(customer.order_ids)} | витрачено: {customer.total_spent} грн")

    def add_to_wishlist(self, customer_id: str, shoe_id: str) -> None:
        customer = self._find_customer(customer_id)
        if not customer:
            print("клієнта не знайдено")
            return
        if shoe_id in customer.wishlist:
            print("вже в вішлісті")
            return
        customer.wishlist.append(shoe_id)
        print("додано до вішліста")

    def add_to_cart(self, customer_id: str, shoe_id: str,
                    size: float, qty: int = 1) -> None:
        shoe = self._find_shoe(shoe_id)
        if not shoe or not shoe.active:
            print("товар не знайдено або недоступний")
            return
        v = shoe.get_variant(size)
        if not v or v.in_stock < qty:
            print(f"немає в наявності розмір {size}")
            return
        cart     = self._get_cart(customer_id)
        existing = cart.find_item(shoe_id, size)
        if existing:
            existing.qty += qty
            print(f"оновлено кошик: {shoe.name} р.{size} x{existing.qty}")
        else:
            cart.items.append(CartItem(shoe_id, size, qty, v.price))
            print(f"додано до кошика: {shoe.name} р.{size} — {v.price} грн")

    def remove_from_cart(self, customer_id: str, shoe_id: str, size: float) -> None:
        cart = self._get_cart(customer_id)
        if cart.remove_item(shoe_id, size):
            print("видалено з кошика")
        else:
            print("товару немає в кошику")

    def show_cart(self, customer_id: str) -> None:
        cart = self._get_cart(customer_id)
        if cart.is_empty():
            print("кошик порожній")
            return
        print(f"\n{'='*40}\nВАШ КОШИК:")
        for item in cart.items:
            shoe = self._find_shoe(item.shoe_id)
            name = shoe.name if shoe else item.shoe_id
            print(f"  {name} р.{item.size} x{item.qty} = {item.subtotal} грн")
        print(f"{'='*40}\nРАЗОМ: {cart.total()} грн")

    # =========================================================================
    # Техніка 9: Consolidate Conditional Expression
    # Кілька умов в updateTier об'єднані через elif в одну послідовність
    # =========================================================================
    # (реалізовано у Customer.recalculate_tier — раніше були 4 окремих if)

    # =========================================================================
    # Техніка 10: Remove Control Flag
    # Булевий прапорець 'bought' у rateShoe → замінено на any()
    # =========================================================================
    # (реалізовано у rate_shoe вище)

    def create_promo(self, code: str, discount: int, promo_type: str,
                     min_order: int = 0, uses: int = None,
                     expiry: datetime.datetime = None) -> None:
        if self._find_promo(code):
            print("промокод існує")
            return
        self.promo_codes.append(PromoCode(code, discount, promo_type, min_order, uses, expiry))
        suffix = '%' if promo_type == PROMO_PERCENT else ' грн'
        print(f"промокод створено: {code} — {discount}{suffix}")

    def apply_promo(self, code: str, order_total: int, customer_id: str) -> int:
        # Guard clauses
        promo = self._find_promo(code)
        if not promo:
            print("промокод не знайдено")
            return 0
        if not promo.is_valid():
            print("промокод недійсний або вичерпано")
            return 0
        if order_total < promo.min_order:
            print(f"мінімальна сума замовлення: {promo.min_order} грн")
            return 0
        if customer_id in promo.used_by:
            print("ви вже використовували цей промокод")
            return 0
        discount = promo.calculate_discount(order_total)
        print(f"знижка: {discount} грн")
        return discount

    def show_order(self, order_id: str) -> None:
        order = self._find_order(order_id)
        if not order:
            print("замовлення не знайдено")
            return
        print(f"\n{'='*40}")
        print(f"замовлення: {order.order_id} | статус: {order.status}")
        print(f"дата: {order.created.strftime('%d.%m.%Y %H:%M')}")
        print("товари:")
        for item in order.items:
            print(f"  {item.label} x{item.qty} = {item.subtotal} грн")
        print(f"доставка ({order.delivery_type}): {order.delivery_cost} грн")
        if order.discount:
            print(f"знижка: -{order.discount} грн")
        if order.bonus_used:
            print(f"бонуси: -{order.bonus_used}")
        print(f"РАЗОМ: {order.total} грн")

    def show_customer_stats(self, customer_id: str) -> None:
        customer = self._find_customer(customer_id)
        if not customer:
            print("клієнта не знайдено")
            return
        all_orders = [o for o in self.orders if o.customer_id == customer_id]
        delivered  = [o for o in all_orders if o.status == STATUS_DELIVERED]
        cancelled  = [o for o in all_orders if o.status == STATUS_CANCELLED]
        cat_counts: dict[str, int] = {}
        for order in delivered:
            for item in order.items:
                shoe = self._find_shoe(item.shoe_id)
                if shoe:
                    cat_counts[shoe.category] = cat_counts.get(shoe.category, 0) + item.qty
        print(f"\n{'='*40}")
        print(f"статистика: {customer.full_name} | рівень: {customer.tier}")
        print(f"замовлень: {len(all_orders)} | виконано: {len(delivered)} | скасовано: {len(cancelled)}")
        print(f"витрачено: {customer.total_spent} грн | бонусів: {customer.bonus_points}")
        if cat_counts:
            fav = max(cat_counts, key=cat_counts.get)
            print(f"улюблена категорія: {fav}")


# =============================================================================
# Демонстрація
# =============================================================================

if __name__ == "__main__":
    shop = SneakerShop()

    shop.add_supplier("Nike UA",     "Ukraine", "nike@ua.com",   30)
    shop.add_supplier("Adidas EU",   "Germany", "adidas@eu.com", 25)
    shop.add_supplier("New Balance", "USA",     "nb@usa.com",    35)

    shop.add_shoe("Nike",        "Air Max 90",        "White/Red",
                  {40:3200,41:3200,42:3300,43:3300,44:3400}, "lifestyle",  "M", "шкіра")
    shop.add_shoe("Nike",        "React Infinity",    "Black/White",
                  {37:4100,38:4100,39:4200,40:4200,41:4300}, "running",    "F", "сітка")
    shop.add_shoe("Adidas",      "Ultraboost 22",     "Core Black",
                  {40:5200,41:5200,42:5300,43:5300,44:5400}, "running",    "M", "сітка")
    shop.add_shoe("Adidas",      "Stan Smith",        "White/Green",
                  {36:2100,37:2100,38:2200,39:2200,40:2300}, "lifestyle",  "U", "шкіра")
    shop.add_shoe("New Balance", "990v5",             "Grey",
                  {40:6800,41:6800,42:6900,43:6900,44:7000}, "lifestyle",  "M", "замша")
    shop.add_shoe("Jordan",      "Air Jordan 1 High", "Chicago",
                  {40:8500,41:8500,42:8600,43:8700,44:8800}, "basketball", "M", "шкіра")

    shop.restock("SH0001",42,10,"SUP001"); shop.restock("SH0001",43, 8,"SUP001")
    shop.restock("SH0002",38, 5,"SUP001"); shop.restock("SH0002",39, 7,"SUP001")
    shop.restock("SH0003",41,12,"SUP002"); shop.restock("SH0003",42,10,"SUP002")
    shop.restock("SH0004",38,15,"SUP002"); shop.restock("SH0004",39,12,"SUP002")
    shop.restock("SH0005",42, 6,"SUP003"); shop.restock("SH0005",43, 4,"SUP003")
    shop.restock("SH0006",42, 3,"SUP001"); shop.restock("SH0006",43, 2,"SUP001")

    shop.register_customer("Олена", "Коваль",    "olena@gmail.com",  "0501234567", "1995-03-15")
    shop.register_customer("Максим","Руденко",   "maxim@gmail.com",  "0671234567", "1988-11-22")
    shop.register_customer("Аліна", "Шевченко",  "alina@gmail.com",  "0931234567", "2001-07-08")
    shop.register_customer("Богдан","Мельник",   "bogdan@gmail.com", "0661234567", "1979-04-30")

    shop.add_address("C00001","Київ", "Хрещатик",      "22","15", True)
    shop.add_address("C00002","Львів","Городоцька",     "45",None, True)
    shop.add_address("C00003","Одеса","Дерибасівська",  "10","3",  True)

    shop.create_promo("NIKE10",  10, PROMO_PERCENT, min_order=2000, uses=100)
    shop.create_promo("WELCOME",300, PROMO_FIXED,   min_order=1500)
    shop.create_promo("VIP20",   20, PROMO_PERCENT, min_order=5000, uses=50)

    shop.add_to_cart("C00001","SH0001",42); shop.add_to_cart("C00001","SH0004",38)
    shop.show_cart("C00001")
    o1 = shop.place_order("C00001", DELIVERY_COURIER, 0, "WELCOME")

    shop.add_to_cart("C00002","SH0003",42)
    o2 = shop.place_order("C00002", DELIVERY_NOVA_POSHTA, 0, "NIKE10")

    shop.add_to_cart("C00003","SH0006",42)
    o3 = shop.place_order("C00003", DELIVERY_PICKUP)

    shop.add_to_cart("C00004","SH0005",42); shop.add_to_cart("C00004","SH0001",43)
    o4 = shop.place_order("C00004", DELIVERY_COURIER, 0, "VIP20")

    shop.update_order_status(o1, STATUS_CONFIRMED)
    shop.update_order_status(o1, STATUS_SHIPPED)
    shop.update_order_status(o1, STATUS_DELIVERED)
    shop.update_order_status(o2, STATUS_CONFIRMED)
    shop.update_order_status(o2, STATUS_DELIVERED)

    shop.rate_shoe("SH0001","C00001",5)
    shop.rate_shoe("SH0003","C00002",4)

    shop.show_shoe("SH0001")
    shop.show_order(o1)
    shop.show_customer_stats("C00001")
    shop.show_sales_report(30)
    shop.show_low_stock()
    shop.show_inventory_report()

    r = shop.search_shoes(brand="Nike", in_stock=True)
    print(f"\nзнайдено Nike: {len(r)} модель(ей)")
