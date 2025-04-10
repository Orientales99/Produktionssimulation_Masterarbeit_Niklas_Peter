import json
from src import RESOURCES
from src.constant.constant import ProductGroup, ItemType
from src.production.base.coordinates import Coordinates
from src.order_data.product import Product
from src.order_data.production_material import ProductionMaterial


class ProductInformationService:
    product_list: list[Product]

    def __init__(self):
        self.data_product_information = None
        self.get_product_information_files_for_init()
        self.product_list = []

    def get_product_information_files_for_init(self):
        with open(RESOURCES / "product_information.json", 'r', encoding='utf-8') as p:
            self.data_product_information = json.load(p)

    def create_product_information_list(self):
        """Creates a list of products, with each product's details including the steps needed for production,
        the time each step takes and which material(production_material) is necessary for this step"""
        for product_key, product_data_list in self.data_product_information.items():
            for product in product_data_list:

                product_id = ProductGroup(int(product_key.split()[1]))

                x, y = product['product_size']
                product_size = Coordinates(x, y)
                item_type = ItemType.FINAL_PRODUCT_PACKED
                processing_step_1 = product['processing_step_1']
                processing_step_2 = product['processing_step_2']
                processing_step_3 = product['processing_step_3']
                processing_step_4 = product['processing_step_4']

                required_product_type_step_1 = ProductionMaterial(f'{product_id}.0', product_id, product_size, ItemType(0))
                processing_time_step_1 = product['processing_time_step_1']

                if processing_step_2 is not None:
                    required_product_type_step_2 = ProductionMaterial(f'{product_id}.1', product_id, product_size, ItemType(1))
                    processing_time_step_2 = product['processing_time_step_2']
                else:
                    required_product_type_step_2 = None
                    processing_time_step_2 = None

                if processing_step_3 is not None:
                    required_product_type_step_3 = ProductionMaterial(f'{product_id}.2', product_id, product_size, ItemType(2))
                    processing_time_step_3 = product['processing_time_step_3']
                else:
                    required_product_type_step_3 = None
                    processing_time_step_3 = None

                required_product_type_step_4 = ProductionMaterial(f'{product_id}.3', product_id, product_size, ItemType(3))
                processing_time_step_4 = product['processing_time_step_4']

                self.product_list.append(
                        Product(product_id, product_size, item_type,
                                required_product_type_step_1, processing_step_1, processing_time_step_1,
                                required_product_type_step_2, processing_step_2, processing_time_step_2,
                                required_product_type_step_3, processing_step_3, processing_time_step_3,
                                required_product_type_step_4, processing_step_4, processing_time_step_4))
        return self.product_list
