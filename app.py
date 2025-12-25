class InventorySystem:
    def __init__(self):
        self.inventory = {} # Format: { product_id: { 'qty': 0, 'total_cost': 0 } }

    def stock_in(self, product_id, qty, unit_price):
        if product_id not in self.inventory:
            self.inventory[product_id] = {'qty': 0, 'total_cost': 0}
        
        self.inventory[product_id]['qty'] += qty
        self.inventory[product_id]['total_cost'] += (qty * unit_price)
        print(f"Masuk: {qty} unit. Harga Rata-rata sekarang: {self.get_avg_price(product_id)}")

    def get_avg_price(self, product_id):
        data = self.inventory.get(product_id)
        if data and data['qty'] > 0:
            return data['total_cost'] / data['qty']
        return 0

    def stock_out(self, product_id, qty):
        if product_id in self.inventory and self.inventory[product_id]['qty'] >= qty:
            avg_price = self.get_avg_price(product_id)
            hpp = qty * avg_price
            self.inventory[product_id]['qty'] -= qty
            self.inventory[product_id]['total_cost'] -= hpp
            print(f"Keluar: {qty} unit. HPP (Beban): Rp{hpp}")
        else:
            print("Error: Stok tidak mencukupi!")

# Simulasi
inv = InventorySystem()
inv.stock_in("Kopi-01", 10, 5000)  # Beli 10 pcs harga 5000
inv.stock_in("Kopi-01", 5, 8000)   # Beli lagi 5 pcs harga 8000 (harga naik)
inv.stock_out("Kopi-01", 3)        # Jual 3 pcs (HPP dihitung dari rata-rata)
