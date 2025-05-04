from src.order_data.order import Order
from src.order_data.production_material import ProductionMaterial


class ConvertOrderToDict:
    def __init__(self):
        pass

    def order_to_dict(self, order: Order) -> dict:
        product = order.product

        step_1 = self.get_step_dict(
            required_material=product.required_product_type_step_1,
            machine_type=product.processing_step_1,
            processing_time=product.processing_time_step_1
        )
        step_2 = self.get_step_dict(
            required_material=product.required_product_type_step_2,
            machine_type=product.processing_step_2,
            processing_time=product.processing_time_step_2
        )
        step_3 = self.get_step_dict(
            required_material=product.required_product_type_step_3,
            machine_type=product.processing_step_3,
            processing_time=product.processing_time_step_3
        )
        step_4 = self.get_step_dict(
            required_material=product.required_product_type_step_4,
            machine_type=product.processing_step_4,
            processing_time=product.processing_time_step_4
        )

        product_dict = {
            "product_id": product.product_id.name,
            "size": {
                "x": product.size.x,
                "y": product.size.y
            },
            "item_type": product.item_type.name,
            "identification_str": product.identification_str,
            "steps": {
                "step_1": step_1,
                "step_2": step_2,
                "step_3": step_3,
                "step_4": step_4
            }
        }

        return {
            "product": product_dict,
            "number_of_products_per_order": order.number_of_products_per_order,
            "order_date": order.order_date.isoformat(),
            "priority": order.priority.name,
            "daily_manufacturing_sequence": order.daily_manufacturing_sequence
        }

    def get_step_dict(self, required_material, machine_type, processing_time) -> dict:
        return {
            "required_product": self.material_to_dict(required_material),
            "machine_type": machine_type,
            "processing_time": processing_time
        }

    def material_to_dict(self, material: ProductionMaterial | None) -> dict | None:
        if material is None:
            return None
        return {
            "identification_str": material.identification_str
        }
