class Order:

    def __init__(self, type, price, stop_loss, order_id):
        self.order_type = type
        self.order_price = price
        self.stop_loss = stop_loss
        self.order_id = order_id