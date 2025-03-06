from enum import Enum


class ItemType(Enum):
    RAW_MATERIAL = 0
    INTERMEDIATE_GOOD_1 = 1
    INTERMEDIATE_GOOD_2 = 2
    FINAL_PRODUCT_UNPACKED = 3
    FINAL_PRODUCT_PACKED = 4


class ColorRGB(Enum):
    WHITE = [255, 255, 255]
    RED = [255, 0, 0]
    GREEN = [0, 255, 0]
    BLUE = [0, 0, 255]
    YELLOW = [255, 255, 0]
    CYAN = [0, 255, 255]
    MAGENTA = [255, 0, 255]
    ORANGE = [255, 165, 0]
    PURPLE = [128, 0, 128]
    PINK = [255, 192, 203]
    BROWN = [165, 42, 42]
    DARK_GREEN = [0, 100, 0]
    LIGHT_BLUE = [173, 216, 230]
    DARK_GRAY = [105, 105, 105]
    GOLD = [255, 215, 0]
    SILVER = [192, 192, 192]
    BLACK = [0, 0, 0]


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


class ProductGroup():
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    THIRTEEN = 13
    FOURTEEN = 14
    FIFTEEN = 15

    def building_groups_of_product(self):
        ProductGroup.ONE = "Ballfreunde", "Fuballfreunde_4teilig"
        pass

    def building_random_groups_of_product(self):
        pass
