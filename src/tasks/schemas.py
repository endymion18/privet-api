from src.tasks.models import Task
import datetime


class TaskSchema:
    airport_meeting: bool
    motel_checked_in: bool
    money_exchange: bool
    sim_card_created: bool
    medical_examinated: bool
    passport_translated: bool
    bank_card: bool
    enrollment_documents: bool
    insurance: bool
    dormitory_documents: bool
    student_ID: bool
    medical_tests: tuple[bool, datetime.date]
    visa_extension: tuple[bool, datetime.date]
    fingerprinting: tuple[bool, datetime.date]

    def __init__(
            self,
            task_info: Task,
            visa_expiration: datetime.datetime,
            last_arrival: datetime.datetime,

    ):
        self.airport_meeting = task_info.airport_meeting
        self.motel_checked_in = task_info.motel_checked_in
        self.money_exchange = task_info.money_exchange
        self.sim_card_created = task_info.sim_card_created
        self.medical_examinated = task_info.medical_examinated
        self.passport_translated = task_info.passport_translated
        self.bank_card = task_info.bank_card
        self.enrollment_documents = task_info.enrollment_documents
        self.insurance = task_info.insurance
        self.dormitory_documents = task_info.dormitory_documents
        self.student_ID = task_info.student_ID

        visa_extension_deadline = datetime.datetime.fromtimestamp(
            datetime.datetime.timestamp(visa_expiration) - 3_456_000
        )
        medical_tests_deadline = datetime.datetime.fromtimestamp(
            datetime.datetime.timestamp(visa_extension_deadline) - 259_200
        )
        self.medical_tests = (task_info.medical_tests, datetime.date(medical_tests_deadline.year,
                                                                     medical_tests_deadline.month,
                                                                     medical_tests_deadline.day))
        self.visa_extension = (task_info.visa_extension, datetime.date(visa_extension_deadline.year,
                                                                       visa_extension_deadline.month,
                                                                       visa_extension_deadline.day))

        fingerprinting_deadline = datetime.datetime.fromtimestamp(
            datetime.datetime.timestamp(last_arrival) + 7_776_000
        )
        self.fingerprinting = (task_info.fingerprinting, datetime.date(fingerprinting_deadline.year,
                                                                       fingerprinting_deadline.month,
                                                                       fingerprinting_deadline.day))


#  visa_expiration in init
