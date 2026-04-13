
import datetime, random

######## ДАНІ ########
INVENTORY = []
CUSTOMERS = []  
ORDERS = []
CARTS = []
PROMO = []
RETURNS = []
SUPPLIERS = []
DELIVERIES = []

# розміри які є в магазині
SIZES = [36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,46,47]

######## ТОВАРИ ########

# додати кросівки в магазин
def newShoe(brand, model, colorway, sz_prices, cat, gender, material):
    # sz_prices це словник {розмір: ціна}
    # перевірити чи є вже такі
    for x in INVENTORY:
        if x['brand']==brand and x['model']==model and x['colorway']==colorway:
            # просто оновити ціни якщо є
            for s in sz_prices:
                found=False
                for v in x['variants']:
                    if v[0]==s:
                        v[1]=sz_prices[s]
                        found=True
                if not found:
                    x['variants'].append([s, sz_prices[s], 0, 0]) # розмір, ціна, кількість, продано
            print(f"оновлено: {brand} {model}")
            return
    # нова пара
    variants = []
    for s in sz_prices:
        variants.append([s, sz_prices[s], 0, 0])
    id = 'SH' + str(len(INVENTORY)+1).zfill(4)
    INVENTORY.append({
        'id': id,
        'brand': brand,
        'model': model, 
        'colorway': colorway,
        'category': cat,         # running/basketball/lifestyle/training
        'gender': gender,        # M/F/U (unisex)
        'material': material,    # шкіра/сітка/замша тощо
        'variants': variants,    # [розмір, ціна, кількість, продано]
        'active': True,
        'rating': [],
        'created': datetime.datetime.now()
    })
    print(f"додано: {id} {brand} {model} {colorway}")

def stockUp(shoe_id, sz, qty, supplier_id=None):
    # поповнити склад
    for x in INVENTORY:
        if x['id'] == shoe_id:
            for v in x['variants']:
                if v[0] == sz:
                    v[2] += qty
                    # записати поставку якщо є постачальник
                    if supplier_id:
                        DELIVERIES.append({
                            'shoe': shoe_id,
                            'size': sz,
                            'qty': qty,
                            'supplier': supplier_id,
                            'date': datetime.datetime.now(),
                            'status': 'received'
                        })
                    print(f"поповнено {shoe_id} розмір {sz}: +{qty} шт")
                    return
            # розміру не було — додати
            x['variants'].append([sz, 0, qty, 0])
            print(f"новий розмір {sz} для {shoe_id}: {qty} шт")
            return
    print("товар не знайдено")

def findShoe(brand=None, cat=None, gender=None, sz=None, max_price=None, in_stock=True):
    res = []
    for x in INVENTORY:
        if not x['active']:
            continue
        if brand and brand.lower() not in x['brand'].lower():
            continue
        if cat and x['category'] != cat:
            continue
        if gender and x['gender'] != gender:
            continue
        # перевірити розмір і ціну
        ok_variants = []
        for v in x['variants']:
            if in_stock and v[2] <= 0:
                continue
            if sz and v[0] != sz:
                continue
            if max_price and v[1] > max_price:
                continue
            ok_variants.append(v)
        if ok_variants:
            res.append({'shoe': x, 'variants': ok_variants})
    return res

def showShoe(shoe_id):
    for x in INVENTORY:
        if x['id'] == shoe_id:
            avg_r = round(sum(x['rating'])/len(x['rating']),1) if x['rating'] else 'немає'
            print(f"\n{'='*40}")
            print(f"{x['brand']} {x['model']} — {x['colorway']}")
            print(f"категорія: {x['category']} | стать: {x['gender']} | матеріал: {x['material']}")
            print(f"рейтинг: {avg_r}/5")
            print(f"наявність:")
            for v in sorted(x['variants'], key=lambda q: q[0]):
                stock_str = f"{v[2]} шт" if v[2]>0 else "немає"
                print(f"  розмір {v[0]}: {v[1]} грн — {stock_str}")
            return
    print("не знайдено")

def deactivateShoe(shoe_id):
    for x in INVENTORY:
        if x['id'] == shoe_id:
            if not x['active']:
                print("вже неактивний")
                return
            x['active'] = False
            print(f"знято з продажу: {shoe_id}")
            return
    print("не знайдено")

def rateShoe(shoe_id, customer_id, score, comment=""):
    # перевірити що клієнт купував цей товар
    bought = False
    for o in ORDERS:
        if o['customer'] == customer_id and o['status'] == 'delivered':
            for item in o['items']:
                if item[0] == shoe_id:
                    bought = True
    if not bought:
        print("можна оцінити тільки куплений товар")
        return
    if score < 1 or score > 5:
        print("оцінка від 1 до 5")
        return
    for x in INVENTORY:
        if x['id'] == shoe_id:
            x['rating'].append(score)
            print(f"дякуємо за відгук! поточний рейтинг: {round(sum(x['rating'])/len(x['rating']),1)}")
            return

######## ПОСТАЧАЛЬНИКИ ########

def addSupplier(name, country, contact, markup):
    for s in SUPPLIERS:
        if s['name'] == name:
            print("постачальник існує")
            return
    id = 'SUP' + str(len(SUPPLIERS)+1).zfill(3)
    SUPPLIERS.append({
        'id': id,
        'name': name,
        'country': country,
        'contact': contact,
        'markup': markup,    # відсоток націнки
        'active': True,
        'deliveries': 0
    })
    print(f"постачальника додано: {id} {name}")

def showSupplier(sup_id):
    for s in SUPPLIERS:
        if s['id'] == sup_id:
            d_count = len([d for d in DELIVERIES if d['supplier']==sup_id])
            print(f"постачальник: {s['name']}")
            print(f"країна: {s['country']}")
            print(f"контакт: {s['contact']}")
            print(f"націнка: {s['markup']}%")
            print(f"поставок: {d_count}")
            return
    print("не знайдено")

######## КЛІЄНТИ ########

def registerCustomer(first, last, email, phone, bday=None):
    for c in CUSTOMERS:
        if c['email'] == email:
            print(f"клієнт з таким email вже є")
            return None
    id = 'C' + str(len(CUSTOMERS)+1).zfill(5)
    CUSTOMERS.append({
        'id': id,
        'name': first + ' ' + last,
        'email': email,
        'phone': phone,
        'bday': bday,
        'registered': datetime.datetime.now(),
        'orders': [],
        'wishlist': [],
        'total_spent': 0,
        'bonus_points': 0,
        'tier': 'bronze',   # bronze/silver/gold/platinum
        'active': True,
        'addresses': []
    })
    print(f"реєстрація успішна! ваш id: {id}")
    return id

def addAddress(customer_id, city, street, building, apt=None, is_default=False):
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            addr = {
                'city': city,
                'street': street,
                'building': building,
                'apt': apt,
                'default': is_default
            }
            if is_default:
                for a in c['addresses']:
                    a['default'] = False
            c['addresses'].append(addr)
            print("адресу додано")
            return
    print("клієнта не знайдено")

def showCustomer(customer_id):
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            print(f"\n{'='*40}")
            print(f"клієнт: {c['name']}")
            print(f"email: {c['email']} | тел: {c['phone']}")
            print(f"рівень: {c['tier']} | бонуси: {c['bonus_points']}")
            print(f"замовлень: {len(c['orders'])} | витрачено: {c['total_spent']} грн")
            print(f"вішлист: {len(c['wishlist'])} товарів")
            return
    print("клієнта не знайдено")

def updateTier(customer_id):
    # оновити рівень на основі витрат
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            spent = c['total_spent']
            if spent >= 50000:
                c['tier'] = 'platinum'
            if spent >= 20000 and spent < 50000:
                c['tier'] = 'gold'
            if spent >= 8000 and spent < 20000:
                c['tier'] = 'silver'
            if spent < 8000:
                c['tier'] = 'bronze'
            return

def addToWishlist(customer_id, shoe_id):
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            if shoe_id in c['wishlist']:
                print("вже в вішлісті")
                return
            c['wishlist'].append(shoe_id)
            print("додано до вішліста")
            return
    print("клієнта не знайдено")

######## КОШИК ########

def getCart(customer_id):
    for cart in CARTS:
        if cart['customer'] == customer_id and cart['active']:
            return cart
    # створити новий
    new_cart = {
        'customer': customer_id,
        'items': [],   # [shoe_id, size, qty, price]
        'active': True,
        'created': datetime.datetime.now()
    }
    CARTS.append(new_cart)
    return new_cart

def addToCart(customer_id, shoe_id, size, qty=1):
    # перевірити наявність
    shoe = None
    variant = None
    for x in INVENTORY:
        if x['id'] == shoe_id and x['active']:
            for v in x['variants']:
                if v[0] == size:
                    shoe = x
                    variant = v
    if not shoe:
        print("товар не знайдено або недоступний")
        return
    if not variant or variant[2] < qty:
        print(f"немає в наявності розмір {size}")
        return
    cart = getCart(customer_id)
    # перевірити чи є вже в кошику
    for item in cart['items']:
        if item[0] == shoe_id and item[1] == size:
            item[2] += qty
            print(f"оновлено кошик: {shoe['brand']} {shoe['model']} р.{size} x{item[2]}")
            return
    cart['items'].append([shoe_id, size, qty, variant[1]])
    print(f"додано до кошика: {shoe['brand']} {shoe['model']} р.{size} — {variant[1]} грн")

def removeFromCart(customer_id, shoe_id, size):
    cart = getCart(customer_id)
    for i, item in enumerate(cart['items']):
        if item[0]==shoe_id and item[1]==size:
            cart['items'].pop(i)
            print("видалено з кошика")
            return
    print("товару немає в кошику")

def showCart(customer_id):
    cart = getCart(customer_id)
    if not cart['items']:
        print("кошик порожній")
        return
    print(f"\n{'='*40}")
    print("ВАШ КОШИК:")
    total = 0
    for item in cart['items']:
        for x in INVENTORY:
            if x['id'] == item[0]:
                print(f"  {x['brand']} {x['model']} р.{item[1]} x{item[2]} = {item[3]*item[2]} грн")
                total += item[3]*item[2]
    print(f"{'='*40}")
    print(f"РАЗОМ: {total} грн")

def clearCart(customer_id):
    cart = getCart(customer_id)
    cart['items'] = []
    print("кошик очищено")

######## ПРОМОКОДИ ########

def createPromo(code, discount, type, min_order=0, uses=None, expiry=None):
    # type: percent або fixed
    for p in PROMO:
        if p['code'] == code:
            print("промокод існує")
            return
    PROMO.append({
        'code': code,
        'discount': discount,
        'type': type,
        'min_order': min_order,
        'uses_left': uses,       # None = безліміт
        'expiry': expiry,
        'active': True,
        'used_by': []
    })
    print(f"промокод створено: {code} — {discount}{'%' if type=='percent' else ' грн'}")

def applyPromo(code, order_total, customer_id):
    for p in PROMO:
        if p['code'] == code:
            if not p['active']:
                print("промокод неактивний")
                return 0
            if p['expiry'] and datetime.datetime.now() > p['expiry']:
                print("термін дії вичерпано")
                return 0
            if order_total < p['min_order']:
                print(f"мінімальна сума замовлення: {p['min_order']} грн")
                return 0
            if p['uses_left'] != None and p['uses_left'] <= 0:
                print("промокод вичерпано")
                return 0
            if customer_id in p['used_by']:
                print("ви вже використовували цей промокод")
                return 0
            if p['type'] == 'percent':
                disc = round(order_total * p['discount'] / 100)
            if p['type'] == 'fixed':
                disc = min(p['discount'], order_total)
            print(f"знижка: {disc} грн")
            return disc
    print("промокод не знайдено")
    return 0

######## ЗАМОВЛЕННЯ ########

def placeOrder(customer_id, delivery_type, address_idx=0, promo_code=None, use_bonus=False):
    # знайти клієнта
    customer = None
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            customer = c
    if not customer:
        print("клієнта не знайдено")
        return None
    cart = getCart(customer_id)
    if not cart['items']:
        print("кошик порожній")
        return None
    # перевірити наявність всього і зарезервувати
    items_to_order = []
    subtotal = 0
    for item in cart['items']:
        shoe_id, size, qty, price = item
        found = False
        for x in INVENTORY:
            if x['id'] == shoe_id:
                for v in x['variants']:
                    if v[0] == size:
                        if v[2] < qty:
                            print(f"недостатньо товару: {x['brand']} {x['model']} р.{size}")
                            return None
                        found = True
                        items_to_order.append({'shoe': shoe_id, 'size': size, 'qty': qty, 'price': price, 'brand': x['brand'], 'model': x['model']})
                        subtotal += price * qty
        if not found:
            print("товар недоступний")
            return None
    # доставка
    delivery_cost = 0
    if delivery_type == 'courier':
        delivery_cost = 99
    if delivery_type == 'novaposhta':
        delivery_cost = 59
    if delivery_type == 'pickup':
        delivery_cost = 0
    total = subtotal + delivery_cost
    # промокод
    discount = 0
    if promo_code:
        discount = applyPromo(promo_code, total, customer_id)
        total -= discount
    # бонуси
    bonus_used = 0
    if use_bonus and customer['bonus_points'] > 0:
        bonus_used = min(customer['bonus_points'], round(total * 0.1))
        total -= bonus_used
        customer['bonus_points'] -= bonus_used
    # нараховані бонуси (1% від суми)
    bonus_earned = round(total * 0.01)
    # списати з залишків
    for item in items_to_order:
        for x in INVENTORY:
            if x['id'] == item['shoe']:
                for v in x['variants']:
                    if v[0] == item['size']:
                        v[2] -= item['qty']
                        v[3] += item['qty']
    # оновити промокод
    if promo_code and discount > 0:
        for p in PROMO:
            if p['code'] == promo_code:
                p['used_by'].append(customer_id)
                if p['uses_left'] != None:
                    p['uses_left'] -= 1
    order_id = 'ORD' + str(len(ORDERS)+1).zfill(6)
    addr = customer['addresses'][address_idx] if customer['addresses'] else {}
    ORDERS.append({
        'id': order_id,
        'customer': customer_id,
        'items': [(i['shoe'], i['size'], i['qty'], i['price']) for i in items_to_order],
        'subtotal': subtotal,
        'delivery_type': delivery_type,
        'delivery_cost': delivery_cost,
        'discount': discount,
        'bonus_used': bonus_used,
        'bonus_earned': bonus_earned,
        'total': total,
        'address': addr,
        'status': 'pending',
        'created': datetime.datetime.now(),
        'promo': promo_code
    })
    customer['orders'].append(order_id)
    customer['bonus_points'] += bonus_earned
    updateTier(customer_id)
    clearCart(customer_id)
    print(f"\nзамовлення #{order_id} оформлено!")
    print(f"сума: {subtotal} грн | доставка: {delivery_cost} грн | знижка: {discount} грн | бонуси: -{bonus_used} грн")
    print(f"до сплати: {total} грн")
    print(f"нараховано бонусів: +{bonus_earned}")
    return order_id

def updateOrderStatus(order_id, new_status):
    valid = ['pending','confirmed','shipped','delivered','cancelled']
    if new_status not in valid:
        print("невірний статус")
        return
    for o in ORDERS:
        if o['id'] == order_id:
            old = o['status']
            if old == 'cancelled':
                print("замовлення вже скасовано")
                return
            if old == 'delivered' and new_status != 'delivered':
                print("доставлене замовлення не можна змінити")
                return
            o['status'] = new_status
            if new_status == 'cancelled':
                for item in o['items']:
                    for x in INVENTORY:
                        if x['id'] == item[0]:
                            for v in x['variants']:
                                if v[0] == item[1]:
                                    v[2] += item[2]
                                    v[3] -= item[2]
                for c in CUSTOMERS:
                    if c['id'] == o['customer']:
                        c['bonus_points'] -= o['bonus_earned']
                        c['bonus_points'] = max(0, c['bonus_points'])
            if new_status == 'delivered':
                for c in CUSTOMERS:
                    if c['id'] == o['customer']:
                        c['total_spent'] += o['total']
                        updateTier(c['id'])
            print(f"статус оновлено: {old} → {new_status}")
            return
    print("замовлення не знайдено")

def showOrder(order_id):
    for o in ORDERS:
        if o['id'] == order_id:
            print(f"\n{'='*40}")
            print(f"замовлення: {o['id']}")
            print(f"статус: {o['status']}")
            print(f"дата: {o['created'].strftime('%d.%m.%Y %H:%M')}")
            print(f"товари:")
            for item in o['items']:
                for x in INVENTORY:
                    if x['id'] == item[0]:
                        print(f"  {x['brand']} {x['model']} р.{item[1]} x{item[2]} = {item[3]*item[2]} грн")
            print(f"доставка ({o['delivery_type']}): {o['delivery_cost']} грн")
            if o['discount']:
                print(f"знижка: -{o['discount']} грн")
            if o['bonus_used']:
                print(f"бонуси використано: -{o['bonus_used']}")
            print(f"РАЗОМ: {o['total']} грн")
            return
    print("замовлення не знайдено")

######## ПОВЕРНЕННЯ ########

def createReturn(order_id, customer_id, items_to_return, reason):
    order = None
    for o in ORDERS:
        if o['id'] == order_id and o['customer'] == customer_id:
            order = o
    if not order:
        print("замовлення не знайдено")
        return
    if order['status'] != 'delivered':
        print("повернення можливе тільки для доставлених замовлень")
        return
    if (datetime.datetime.now() - order['created']).days > 14:
        print("строк повернення вичерпано (14 днів)")
        return
    refund = 0
    valid_items = []
    for ret_item in items_to_return:
        for o_item in order['items']:
            if o_item[0]==ret_item[0] and o_item[1]==ret_item[1]:
                if ret_item[2] > o_item[2]:
                    print(f"кількість перевищує замовлену")
                    return
                valid_items.append(ret_item)
                refund += o_item[3] * ret_item[2]
    if not valid_items:
        print("товари не знайдено в замовленні")
        return
    ret_id = 'RET' + str(len(RETURNS)+1).zfill(5)
    RETURNS.append({
        'id': ret_id,
        'order': order_id,
        'customer': customer_id,
        'items': valid_items,
        'reason': reason,
        'refund': refund,
        'status': 'pending',
        'created': datetime.datetime.now()
    })
    print(f"заявку на повернення створено: {ret_id}")
    print(f"сума повернення: {refund} грн")

def processReturn(ret_id, approve):
    for r in RETURNS:
        if r['id'] == ret_id:
            if r['status'] != 'pending':
                print("заявка вже оброблена")
                return
            if approve:
                r['status'] = 'approved'
                for item in r['items']:
                    for x in INVENTORY:
                        if x['id'] == item[0]:
                            for v in x['variants']:
                                if v[0] == item[1]:
                                    v[2] += item[2]
                for c in CUSTOMERS:
                    if c['id'] == r['customer']:
                        refund_bonus = round(r['refund'] * 0.01)
                        c['bonus_points'] += refund_bonus
                print(f"повернення схвалено. сума до повернення: {r['refund']} грн")
            else:
                r['status'] = 'rejected'
                print("повернення відхилено")
            return
    print("заявку не знайдено")

######## АНАЛІТИКА ########

def salesReport(days=30):
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    total_rev = 0
    total_orders = 0
    total_items = 0
    cancelled = 0
    top = {}
    for o in ORDERS:
        if o['created'] < cutoff:
            continue
        total_orders += 1
        if o['status'] == 'cancelled':
            cancelled += 1
            continue
        total_rev += o['total']
        for item in o['items']:
            total_items += item[2]
            key = item[0]
            if key not in top:
                top[key] = 0
            top[key] += item[2]
    print(f"\n{'='*40}")
    print(f"ЗВІТ ЗА {days} ДНІВ")
    print(f"замовлень: {total_orders} (скасовано: {cancelled})")
    print(f"виручка: {total_rev} грн")
    print(f"продано пар: {total_items}")
    if top:
        best_id = max(top, key=top.get)
        for x in INVENTORY:
            if x['id'] == best_id:
                print(f"топ товар: {x['brand']} {x['model']} — {top[best_id]} пар")

def lowStockAlert(threshold=3):
    print(f"\n{'='*40}")
    print(f"МАЛО НА СКЛАДІ (менше {threshold} шт):")
    found = False
    for x in INVENTORY:
        if not x['active']:
            continue
        for v in x['variants']:
            if 0 < v[2] <= threshold:
                found = True
                print(f"  {x['brand']} {x['model']} р.{v[0]}: {v[2]} шт")
    if not found:
        print("  все в нормі")

def customerStats(customer_id):
    for c in CUSTOMERS:
        if c['id'] == customer_id:
            orders = [o for o in ORDERS if o['customer']==customer_id]
            delivered = [o for o in orders if o['status']=='delivered']
            cancelled_o = [o for o in orders if o['status']=='cancelled']
            fav_cat = {}
            for o in delivered:
                for item in o['items']:
                    for x in INVENTORY:
                        if x['id']==item[0]:
                            cat = x['category']
                            fav_cat[cat] = fav_cat.get(cat,0)+item[2]
            print(f"\n{'='*40}")
            print(f"статистика: {c['name']}")
            print(f"рівень: {c['tier']}")
            print(f"замовлень: {len(orders)} | виконано: {len(delivered)} | скасовано: {len(cancelled_o)}")
            print(f"витрачено: {c['total_spent']} грн")
            print(f"бонусів: {c['bonus_points']}")
            if fav_cat:
                fav = max(fav_cat, key=fav_cat.get)
                print(f"улюблена категорія: {fav}")
            return
    print("клієнта не знайдено")

def inventoryReport():
    print(f"\n{'='*40}")
    print("ЗВІТ ПО СКЛАДУ")
    total_pairs = 0
    total_value = 0
    for x in INVENTORY:
        if not x['active']: continue
        pairs = sum(v[2] for v in x['variants'])
        value = sum(v[1]*v[2] for v in x['variants'])
        total_pairs += pairs
        total_value += value
        if pairs > 0:
            print(f"  {x['brand']} {x['model']}: {pairs} пар на {value} грн")
    print(f"ВСЬОГО: {total_pairs} пар | вартість: {total_value} грн")
