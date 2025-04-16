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
    STANDARD_ORDER_1 = 1
    STANDARD_ORDER_2 = 2
    STANDARD_ORDER_3 = 3
    STANDARD_ORDER_4 = 4
    STANDARD_ORDER_5 = 5


class MachineQuality(Enum):
    NEW_MACHINE = 0
    OLD_MACHINE = 1


class MachineType(Enum):
    PACKAGING_MACHINE = 0
    MANUFACTURING_MACHINE_A = 1
    MANUFACTURING_MACHINE_B = 2
    MANUFACTURING_MACHINE_C = 3


class ProductGroup(Enum):
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
        return {
            ProductGroup.ONE: ("ballfreunde", "fussballfreunde_4teilig"),
            ProductGroup.TWO: ("bauernfreunde", "bauernfreunde_4teilig"),
            ProductGroup.THREE: ("janosch_4teilig", "janosch_6teilig"),
            ProductGroup.FOUR: ("kÃ¶nig_lÃ¶wen_4teilig", "kÃ¶nig_lÃ¶wen_6teilig"),
            ProductGroup.FIVE: ("LYTO_AMEFA_BAUERNFREUNDE", "LYTO_AMEFA_WALDFREUNDE"),
            ProductGroup.SIX: ("LYTO_AMEFA_FUSSBALLFREUNDE", "LYTO_AMEFA_PRINZESSIN", "LYTO_WMF_SAFARI"),
            ProductGroup.SEVEN: ("Namensgravur_Tiere", "Safari_Namensgravur"),
            ProductGroup.EIGHT: ("prinzessinnen", "prinzessin_4teilig"),
            ProductGroup.NINE: ("waldfreunde", "waldfreunde_4teilig"),
            ProductGroup.TEN: ("wmf_einhorn_4teilig", "wmf_farm_4teilig", "wmf_first_lyric_4teilig"),
            ProductGroup.ELEVEN: ("wmf_kinderbesteck_knuddel", "wmf_knuddel_gravur"),
            ProductGroup.TWELVE: ("wmf_safari_new", "wmf_lion_king_4teilig"),
            ProductGroup.THIRTEEN: ("wmf_safari_set_6teilig", "wmf_zwerge_gravur"),
            ProductGroup.FOURTEEN: ("zoo", "zoo_4teilig"),
            ProductGroup.FIFTEEN: "zwerge_gravur"
        }.get(self)


class TransportRobotStatus(Enum):
    IDLE = "idle"
    MOVING_TO_PICKUP = "moving to pick up"
    LOADING = "loading"
    MOVING_TO_DROP_OFF = "moving to drop off"
    UNLOADING = "unloading"
    RETURNING = "returning to base"
    PAUSED = "paused"


class WorkingRobotStatus(Enum):
    IDLE = "idle"
    MOVING_TO_MACHINE = "moving to machine"
    WAITING_IN_FRONT_OF_MACHINE = "waiting in front of the machine"
    WORKING_ON_MACHINE = "working on machine"
    WAITING_IN_MACHINE_TO_EXIT = "waiting in the machine to exit area"
    WAITING_FOR_ORDER = "waiting for order"
    RETURNING = "returning to base"
    PAUSED = "paused"


class MachineProcessStatus(Enum):
    IDLE = "idle"
    WAITING_NEXT_ORDER = "waiting to start next order process"
    SETUP = "setup"
    READY_TO_PRODUCE = "machine is ready to produce"
    INPUT_EMPTY = "input is empty"
    OUTPUT_FULL = "output is full"
    PRODUCING_PRODUCT = "producing product"


class MachineWorkingRobotStatus(Enum):
    NO_WR = "no WR in machine"
    WAITING_WR = "waiting for WR arriving"
    WR_PRESENT = "WR is in machine"
    WR_LEAVING = "WR is leaving machine"
