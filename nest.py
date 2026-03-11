from collections import deque

class Nest:

    def __init__(self, product_info):
  
        self.inventory = {}
        self.backlog = deque()
        self.init_catalog(product_info) 

    def init_catalog(self, product_info):

        '''Creates the inventory given a payload of items and their contents'''
       
        for product in product_info:
            self.inventory[product["product_id"]] = {"product_name": product["product_name"], "mass_kg": product["mass_g"] / 1000, "stock": 0}
    
    def process_restock(self, restock):
        
        '''Updates the stock in the inventory, then checks if we can ship anything from the backlog'''

        for product in restock: 
            
            #if we try to restock an item that is not in the inventory
            if product["product_id"] not in self.inventory:
                print("item with id:", product["product_id"],  "does not exist in the catalog. No refill made for this item.")

            else:
                self.inventory[product["product_id"]]["stock"] += product["quantity"]
        
        #after we restock, we need to check if we can ship anything from the backlog
        orders_to_retry = list(self.backlog)
        self.backlog.clear()

        for order in orders_to_retry:
            self.process_order(order)

    def process_order(self, order):
        '''Procces an order: 1. ship the products -> 2. add to backlog (if needed)'''

        orderId = order["order_id"]
        requested = order["requested"]

        productDict = {product["product_id"]: product["quantity"] for product in requested} #ex: {0: 5, 1: 10} - maps product IDs to quantities
                                                                                                  
        #turning the requested order parameter into a data structure we can use for packing logic
        requestedOrder = {"order_id": orderId, "products": productDict} 
    
        self._pack_products(requestedOrder)
         
        self._add_to_back_log(requestedOrder)
    
    def ship_package(self, shipment):

        '''ships the package'''

        print(shipment)
    
    def _pack_products(self, requestedOrder):

        '''Creating the packages for the order'''

        while True: #this loop continues until, for the order, there are no more shipments that can be made. ex. all items are shipped or we ran out of inventory for an item

            package = self._create_single_package(requestedOrder)

            if not package["shipped"]: #nothing else to pack
                break

            self.ship_package(package)

    def _create_single_package(self, requestedOrder):

        '''Creating a single package for the order'''

        package = {"order_id": requestedOrder["order_id"], "shipped": []}
        total_weight = 0

        for product_id in list(requestedOrder["products"].keys()): #loop through the requested products of the entire order

            if self._should_skip_item(product_id, requestedOrder): #check if we should not pack this item
                continue
                
            packed_qty, total_weight = self._pack_item(product_id, requestedOrder, total_weight) 

            if packed_qty > 0: #only add to shipment if we actually packed something
                package["shipped"].append({
                    "product_id": product_id,
                    "quantity": packed_qty
                })

        return package
    
    def _should_skip_item(self, product_id, requestedOrder):
         
         '''Check if item should be skipped (out of stock or item already shipped).'''
         return (
                self.inventory[product_id]["stock"] == 0 or  #out of product
                requestedOrder["products"][product_id] == 0     #already shipped entirety of item
                )  
    
    def _pack_item(self, product_id, requestedOrder, current_weight):
        
        '''Packing a specific item from the order'''

        stock = self.inventory[product_id]["stock"]
        requested = requestedOrder["products"][product_id]
        mass = self.inventory[product_id]["mass_kg"]

        packed = 0

        for _ in range(requested): #iterate through requested amount of item in order
            if stock > 0 and current_weight + mass <= 1.8: #if we are able to pack it
                current_weight += mass
                packed += 1
                stock -= 1
            else:
                break

        #update state
        if packed > 0:
            requestedOrder["products"][product_id] -= packed
            self.inventory[product_id]["stock"] = stock
        
        return packed, current_weight
    
    
    def _add_to_back_log(self, requestedOrder):
         
         '''takes remaining items from order and adds to backlog'''

         has_items = False

         backLogOrder = {"order_id": requestedOrder["order_id"], "requested": []} 

         for product_id in requestedOrder["products"]:

            if requestedOrder["products"][product_id] > 0:

                has_items = True #there is at least one item that we did not pack in the order
                productAdding = {"product_id": product_id, "quantity": requestedOrder["products"][product_id]}

                backLogOrder["requested"].append(productAdding)
            
         if has_items: #there is at least one item to add. This check is to make sure we dont add an empty object into the backlog 
            self.backlog.append(backLogOrder)

    def show_back_log(self):
        print(self.backlog)
       
    def show_inventory(self):
        print(self.inventory)
        