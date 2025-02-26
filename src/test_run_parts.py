from src.data.order_service import OrderService

order_service = OrderService()

order_service.get_file_production_entities()

b = order_service.generate_wr_list()
print(b)
