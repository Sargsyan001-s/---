
import hashlib
import json
import os
from cryptography.fernet import Fernet

class User:
    def __init__(self, username, password, key=None):
        self.username = username
        self.hashed_password = self.hash_password(password)
        self.cart = set()
        self.purchase_history = []
        self.personal_data = {}
        self.key = key if key else Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.hashed_password == self.hash_password(password)

    def add_to_cart(self, item_id):
        self.cart.add(item_id)

    def purchase(self, admin):
        if self.cart:
            self.purchase_history.extend(self.cart)
            self.cart.clear()
            print("Покупка оформлена!")
        else:
            print("Корзина пуста.")

    def view_cart(self, admin):
        if self.cart:
            cart_items = [admin.get_item_by_id(item_id) for item_id in self.cart if admin.get_item_by_id(item_id)]
            return cart_items
        else:
            return "Корзина пуста."

    def view_purchase_history(self, admin):
        purchase_items = [admin.get_item_by_id(item_id) for item_id in self.purchase_history if admin.get_item_by_id(item_id)]
        return purchase_items

    def clear_cart(self):
        self.cart.clear()

    def update_password(self, new_password):
        self.hashed_password = self.hash_password(new_password)

    def format_items(self, items):
        if not items:
            return "Товары не найдены."
        result = "{:<5} {:<25} {:<10}\n".format("ID", "Название", "Цена")
        for item in items:
            result += "{:<5} {:<25} {:<10}\n".format(item.get('id'), item.get('name'), item.get('price'))
        return result

    def set_personal_data(self, data):
        encrypted_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted_data[key] = self.cipher.encrypt(value.encode()).decode()
            else:
                encrypted_data[key] = value
        self.personal_data = encrypted_data

    def get_personal_data(self):
        decrypted_data = {}
        for key, value in self.personal_data.items():
            if isinstance(value, str):
                try:
                    decrypted_data[key] = self.cipher.decrypt(value.encode()).decode()
                except Exception as e:
                    print(f"Ошибка дешифровки: {e}")
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
        return decrypted_data

    def __str__(self):
        return f"User: {self.username}"


class Admin(User):
    def __init__(self, username, password, items=None, key=None):
        super().__init__(username, password, key)
        self.items = items if items else [
            {'name': 'Кольцо с бриллиантом', 'price': 35000, 'id': 1},
            {'name': 'Кольцо с фианитом', 'price': 20000, 'id': 2},
            {'name': 'Золотые серьги', 'price': 6780, 'id': 3},
            {'name': 'Серебряные серьги', 'price': 1500, 'id': 4},
            {'name': 'Колье золотое', 'price': 8000, 'id': 5},
            {'name': 'Колье серебряное', 'price': 4500, 'id': 6}
        ]

    def add_item(self, item_name, price):
        new_id = max(item['id'] for item in self.items) + 1 if self.items else 1
        self.items.append({'name': item_name, 'price': price, 'id': new_id})

    def remove_item(self, item_id):
        self.items = [item for item in self.items if item['id'] != item_id]

    def view_items(self, sort_by=None, filter_price=None):
        items_to_show = self.items[:]
        if sort_by == 'price':
            items_to_show.sort(key=lambda item: item['price'])
        if filter_price:
            items_to_show = [item for item in items_to_show if item['price'] <= filter_price]
        return items_to_show

    def display_items(self, items_to_show):
        print("{:<5} {:<25} {:<10}".format("ID", "Название", "Цена"))
        for item in items_to_show:
            print("{:<5} {:<25} {:<10}".format(item.get('id', 'N/A'), item.get('name', 'N/A'), item.get('price', 'N/A')))

    def get_item_by_id(self, item_id):
        for item in self.items:
            if item['id'] == item_id:
                return item
        return None


class DataManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)


    def save_user(self, user):
        filename = os.path.join(self.data_dir, f'{user.username}.json')
        with open(filename, 'w') as f:
            data = {
                'username': user.username,
                'hashed_password': user.hashed_password,
                'cart': list(user.cart),
                'purchase_history': user.purchase_history,
                'personal_data': user.personal_data,
                'key': user.key.decode()
            }
            json.dump(data, f, indent=4)

    def load_user(self, username):
        filename = os.path.join(self.data_dir, f'{username}.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                user = User(data['username'], "dummy_password", key=data['key'].encode())
                user.hashed_password = data['hashed_password']
                user.cart = set(data['cart'])
                user.purchase_history = data['purchase_history']
                user.personal_data = data['personal_data']
                return user
        return None

    def save_admin(self, admin):
        filename = os.path.join(self.data_dir, f'{admin.username}_admin.json')
        with open(filename, 'w') as f:
            data = {
                'username': admin.username,
                'hashed_password': admin.hashed_password,
                'items': admin.items,
                'key': admin.key.decode()
            }
            json.dump(data, f, indent=4)

    def load_admin(self, username):
        filename = os.path.join(self.data_dir, f'{username}_admin.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                admin = Admin(data['username'], "dummy_password", items=data['items'], key=data['key'].encode())
                admin.hashed_password = data['hashed_password']
                return admin
        return None

def demonstrate_hashing():
    password = input("Введите пароль для хеширования: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print(f"Хеш пароля: {hashed_password}")


def main_menu():
    print("\n--- Главное меню ---")
    print("1. Войти как администратор")
    print("2. Войти как пользователь")
    print("3. Продемонстрировать хеширование")
    print("4. Выйти")
    choice = input("Выберите опцию: ")
    return choice

def admin_menu(admin):
    while True:
        print("\n--- Меню администратора ---")
        print("1. Просмотреть товары")
        print("2. Добавить товар")
        print("3. Удалить товар")
        print("4. Выйти из меню администратора")
        choice = input("Выберите опцию: ")

        if choice == '1':
            items = admin.view_items()
            admin.display_items(items)
        elif choice == '2':
            name = input("Введите название товара: ")
            price = float(input("Введите цену товара: "))
            admin.add_item(name, price)
            data_manager.save_admin(admin)
            print("Товар добавлен.")
        elif choice == '3':
            item_id = int(input("Введите ID товара для удаления: "))
            admin.remove_item(item_id)
            data_manager.save_admin(admin)
            print("Товар удален.")
        elif choice == '4':
            data_manager.save_admin(admin)
            break
        else:
            print("Неверная опция.")


def user_menu(user, admin):
    while True:
        print("\n--- Меню пользователя ---")
        print("1. Просмотреть товары")
        print("2. Добавить товар в корзину")
        print("3. Просмотреть корзину")
        print("4. Оформить покупку")
        print("5. Очистить корзину")
        print("6. Просмотреть историю покупок")
        print("7. Управление персональными данными")
        print("8. Выйти из меню пользователя")

        choice = input("Выберите опцию: ")

        if choice == '1':
            items = admin.view_items()
            admin.display_items(items)
            item_id = input("Введите ID товара для добавления в корзину (или нажмите Enter для отмены): ")
            if item_id:
                try:
                    item_id = int(item_id)
                    item_to_add = admin.get_item_by_id(item_id)
                    if item_to_add:
                        user.add_to_cart(item_id)
                        data_manager.save_user(user)
                        print(f"Товар '{item_to_add['name']}' добавлен в корзину.")
                    else:
                        print("Товар с указанным ID не найден.")
                except ValueError:
                    print("Неверный формат ID товара.")

        elif choice == '2':
            cart_items = user.view_cart(admin)
            print("Содержимое корзины:")
            if isinstance(cart_items, str):
                print(cart_items)
            else:
                admin.display_items(cart_items)
        elif choice == '3':
            user.purchase(admin)
            data_manager.save_user(user)
        elif choice == '4':
            user.clear_cart()
            data_manager.save_user(user)
            print("Корзина очищена.")
        elif choice == '5':
            history = user.view_purchase_history(admin)
            print("История покупок:")
            if history:
                admin.display_items(history)
            else:
                print("История покупок пуста.")
        elif choice == '6':
            print("Управление персональными данными:")
            while True:
                print("\n1. Ввести персональные данные")
                print("2. Просмотреть персональные данные")
                print("3. Вернуться в главное меню")
                pd_choice = input("Выберите опцию: ")
                if pd_choice == '1':
                    new_data = {}
                    new_data['email'] = input("Введите email: ")
                    new_data['phone'] = input("Введите телефон: ")
                    user.set_personal_data(new_data)
                    data_manager.save_user(user)
                    print("Персональные данные сохранены.")
                elif pd_choice == '2':
                    print("Ваши персональные данные:")
                    data = user.get_personal_data()
                    for key, value in data.items():
                        print(f"{key}: {value}")
                elif pd_choice == '3':
                    break
                else:
                    print("Неверная опция.")
        elif choice == '7':
            data_manager.save_user(user)
            break
        else:
            print("Неверная опция.")


data_manager = DataManager()

admin = data_manager.load_admin('admin')
if not admin:
    admin = Admin('admin', 'password')
    data_manager.save_admin(admin)

user = data_manager.load_user('user')
if not user:
    user = User('user', 'password')
    data_manager.save_user(user)


while True:
    main_choice = main_menu()

    if main_choice == '1':
        admin_menu(admin)
    elif main_choice == '2':
        user_menu(user, admin)
    elif main_choice == '3':
        demonstrate_hashing()
    elif main_choice == '4':
        print("Выход из программы.")
        break
    else:
        print("Неверная опция.")

