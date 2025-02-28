from enum import Enum


class ItemType(Enum):
    RAW_MATERIAL = 0
    INTERMEDIATE_GOOD_1 = 1
    INTERMEDIATE_GOOD_2 = 2
    FINAL_PRODUCT_UNPACKED = 3
    FINAL_PRODUCT_PACKED = 4


class OrderPriority(Enum):
    EXPRESS_ORDER = 0
    STANDARD_ORDER = 1


class MachineQuality(Enum):
    NEW_MACHINE = 0
    OLD_MACHINE = 1


class MachineType(Enum):
    PACKAGING_MACHINE = 0
    MANUFACTURING_MACHINE_A = 1
    MANUFACTURING_MACHINE_B = 2
    MANUFACTURING_MACHINE_C = 3

