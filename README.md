# Nest — Inventory & Order Fulfillment System

A lightweight OOP-based inventory manager that handles product catalogs, order fulfillment, and a backlog queue for out-of-stock items.

---

## How It Works

### The `Nest` Class

Everything lives in one class. On init, you pass in product info and it sets up the inventory. Two main data structures power the whole thing:

- **`self.inventory`** — a dict mapping product IDs to their name, mass (in kg), and current stock
- **`self.backlog`** — a `deque` of orders that couldn't be fully fulfilled due to stock shortages

```python
nest = Nest(product_info=[
    {"product_id": 1, "product_name": "Widget", "mass_g": 500},
    {"product_id": 2, "product_name": "Gadget", "mass_g": 900},
])
```

---

## Core Features

### Inventory Management

Products are initialized via `init_catalog()`, which converts mass from grams to kg and sets stock to 0.

Restock with `process_restock()`:

```python
nest.process_restock([
    {"product_id": 1, "quantity": 10},
    {"product_id": 2, "quantity": 5},
])
```

After restocking, it automatically retries any orders sitting in the backlog.

---

### Order Processing

Call `process_order()` with an order dict:

```python
nest.process_order({
    "order_id": "order_001",
    "requested": [
        {"product_id": 1, "quantity": 3},
        {"product_id": 2, "quantity": 2},
    ]
})
```

Internally, it does two things:
1. **Pack & ship** — creates as many packages as possible given current stock and weight limits
2. **Backlog** — anything that couldn't ship gets queued up for later

---

### Backlog Logic

If an order can't be fully fulfilled (out of stock), the remaining items get added to `self.backlog`. The next time `process_restock()` is called, those backlogged orders are retried automatically.

```
Order comes in → try to fulfill → partially fulfilled?
                                        ↓
                                  remainder → backlog
                                        ↓
                              restock happens → retry backlog
```

---

### Packing Logic

Packages have a **1.8 kg weight limit**. The packer loops through items in an order and fills each package greedily until the limit is hit or stock runs out. Then it ships and starts a new package if there's still more to send.

```
_pack_products()
    └── loops calling _create_single_package()
            └── for each item: _should_skip_item()? → _pack_item()
```

An item is skipped if:
- It's out of stock
- All requested units of that item have already shipped

---

## Utility Methods

```python
nest.show_inventory()   # prints current stock levels
nest.show_back_log()    # prints pending backlogged orders
```

---

## Class Structure at a Glance

```
Nest
├── __init__()              # sets up inventory + backlog
├── init_catalog()          # loads products into inventory
├── process_restock()       # restocks + retries backlog
├── process_order()         # entry point for new orders
├── ship_package()          # ships a package (prints it)
├── _pack_products()        # drives the packing loop
├── _create_single_package()# builds one package
├── _should_skip_item()     # checks stock + fulfillment status
├── _pack_item()            # packs a single item into a package
├── _add_to_back_log()      # queues unfulfilled remainder
├── show_inventory()        # debug: print inventory
└── show_back_log()         # debug: print backlog
```

---

## Quick Example

```python
nest = Nest([
    {"product_id": 1, "product_name": "Widget", "mass_g": 500},
    {"product_id": 2, "product_name": "Gadget", "mass_g": 900},
])

nest.process_restock([{"product_id": 1, "quantity": 2}])

nest.process_order({
    "order_id": "order_001",
    "requested": [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 1},  # out of stock → backlog
    ]
})

nest.process_restock([{"product_id": 2, "quantity": 3}])  # triggers backlog retry
```
