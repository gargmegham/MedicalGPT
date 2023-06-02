import re
import uuid
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import (
    Allergy,
    Base,
    Dialog,
    DiseaseAnswer,
    DiseaseInstructions,
    DiseaseQuestion,
    MedicalCondition,
    Medication,
    Medicine,
    Surgery,
    User,
)

import config


class MySQL:
    def __init__(self):
        self.engine = create_engine(
            config.mysql_uri, pool_recycle=280, pool_pre_ping=True, pool_size=25
        )
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables_if_not_exists()

    def create_tables_if_not_exists(self):
        Base.metadata.create_all(self.engine)

    def check_if_object_exists(
        self, user_id: int, raise_exception: bool = False, model: Base = User
    ) -> bool:
        try:
            session = self.Session()
            user = session.query(model).filter_by(user_id=str(user_id)).first()
            if raise_exception and user is None:
                raise Exception(f"User {user_id} does not exist in the database")
            session.close()
            return user is not None
        except:
            session.close()

    def update_n_used_tokens(
        self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int
    ):
        # common function for updating n_used_tokens
        n_used_tokens_dict = self.get_attribute(user_id, "n_used_tokens")
        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens,
            }
        self.set_attribute(user_id, "n_used_tokens", n_used_tokens_dict, User)

    def start_new_dialog(self, user_id: int):
        dialog_id = str(uuid.uuid4())
        self.add_instance(
            user_id,
            Dialog,
            {
                "uid": dialog_id,
                "chat_mode": self.get_attribute(user_id, "current_chat_mode"),
                "model": self.get_attribute(user_id, "current_model"),
            },
        )
        self.set_attribute(user_id, "current_dialog_id", dialog_id, User)
        return dialog_id

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        if dialog_id is None:
            dialog_id = self.get_attribute(user_id, "current_dialog_id")
        return self.get_attribute(
            user_id, "messages", model=Dialog, extra_filters={"uid": dialog_id}
        )

    def set_dialog_messages(
        self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None
    ):
        if dialog_id is None:
            dialog_id = self.get_attribute(user_id, "current_dialog_id")
        self.set_attribute(
            user_id,
            "messages",
            dialog_messages,
            model=Dialog,
            extra_filters={"uid": dialog_id},
        )

    def get_attribute(
        self, user_id: int, attribute: str, model: Base = User, extra_filters: dict = {}
    ):
        try:
            session = self.Session()
            instance = (
                session.query(model)
                .filter_by(user_id=str(user_id), **extra_filters)
                .first()
            )
            session.close()
            if instance is None:
                return None
            return getattr(instance, attribute)
        except:
            session.close()

    def set_attribute(
        self,
        user_id: int,
        attribute: str,
        value,
        model: Base = User,
        extra_filters: dict = {},
    ):
        try:
            session = self.Session()
            session.query(model).filter_by(
                user_id=str(user_id), **extra_filters
            ).update({attribute: value})
            session.commit()
        finally:
            session.close()

    def get_instances(
        self,
        user_id: int,
        model: Base,
        find_first: bool = False,
        extra_filters: dict = None,
        id_greater_than: int = None,
        find_last: bool = False,
    ):
        """
        Supported tables:
        """
        try:
            session = self.Session()
            instances = session.query(model)
            if user_id is not None:
                instances = instances.filter_by(user_id=str(user_id))
            if extra_filters is not None:
                instances = instances.filter_by(**extra_filters)
            if id_greater_than is not None:
                instances = instances.filter(model.id > id_greater_than)
            if find_first:
                instances = instances.order_by(model.id).first()
            elif find_last:
                instances = instances.order_by(model.id.desc()).first()
            else:
                instances = instances.all()
            session.close()
            return instances
        except:
            session.close()

    def add_instance(self, user_id: int, model: Base, data: dict):
        try:
            session = self.Session()
            instance = session.add(model(user_id=str(user_id), **data))
            session.commit()
            session.close()
            return instance
        except:
            session.close()

    def remove_instance(self, user_id: int, model: Base, extra_filters: dict = {}):
        try:
            session = self.Session()
            session.query(model).filter_by(
                user_id=str(user_id), **extra_filters
            ).delete()
            session.commit()
        finally:
            session.close()

    def prepare_patient_history(self, user_id: int, disease_id: int = None) -> list:
        user = self.get_instances(user_id, User, find_first=True)
        history = []
        if disease_id:
            disease_specific_instructions = "\n".join(
                [
                    instruction.detail
                    for instruction in self.get_instances(
                        None,
                        DiseaseInstructions,
                        extra_filters={"disease_id": disease_id},
                    )
                ]
            )
            history.extend(
                [
                    {
                        "role": "system",
                        "content": f"Here are some instructions for you from the doctor:\n\n{disease_specific_instructions}",
                    },
                ]
            )
        history.extend(
            [
                {
                    "role": "assistant",
                    "content": "Please tell me your name?",
                },
                {
                    "role": "user",
                    "content": f"My name is {user.first_name} {user.last_name}",
                },
                {
                    "role": "assistant",
                    "content": "What's your age?",
                },
                {"role": "user", "content": f"My age is {user.age}"},
                {
                    "role": "assistant",
                    "content": "What's your gender?",
                },
                {"role": "user", "content": f"My gender is {user.gender}"},
            ]
        )
        if user.gender == "Female":
            history.extend(
                [
                    {
                        "role": "assistant",
                        "content": "Are you pregnant?",
                    },
                    {
                        "role": "user",
                        "content": "Yes" if user.is_pregnant else "No",
                    },
                ]
            )
        allergies = "\n".join(
            [allergy.detail for allergy in self.get_instances(user_id, Allergy)]
        )
        medical_conditions = "\n".join(
            [mc.detail for mc in self.get_instances(user_id, MedicalCondition)]
        )
        medications = "\n".join(
            [
                medication.detail
                for medication in self.get_instances(user_id, Medication)
            ]
        )
        surgeries = "\n".join(
            [surgery.detail for surgery in self.get_instances(user_id, Surgery)]
        )
        history.extend(
            [
                {
                    "role": "assistant",
                    "content": "Do you have any allergies? If yes, please tell me about them.",
                },
                {
                    "role": "user",
                    "content": allergies if len(allergies) > 0 else "No",
                },
                {
                    "role": "assistant",
                    "content": "Do you have any medical conditions? If yes, please tell me about them.",
                },
                {
                    "role": "user",
                    "content": medical_conditions
                    if len(medical_conditions) > 0
                    else "No",
                },
                {
                    "role": "assistant",
                    "content": "Do you take any medications? If yes, please tell me about them.",
                },
                {
                    "role": "user",
                    "content": medications if len(medications) > 0 else "No",
                },
                {
                    "role": "assistant",
                    "content": "Have you had any surgeries? If yes, please tell me about them.",
                },
                {
                    "role": "user",
                    "content": surgeries if len(surgeries) > 0 else "No",
                },
            ]
        )
        if disease_id is not None:
            disease_specific_questions = self.get_instances(
                None, DiseaseQuestion, extra_filters={"disease_id": disease_id}
            )
            for disease_specific_question in disease_specific_questions:
                answer = self.get_instances(
                    user_id,
                    DiseaseAnswer,
                    extra_filters={"question_id": disease_specific_question.id},
                    find_last=True,
                )
                if answer is not None:
                    history.extend(
                        [
                            {
                                "role": "assistant",
                                "content": disease_specific_question.detail,
                            },
                            {
                                "role": "user",
                                "content": answer.detail,
                            },
                        ]
                    )
        return history

    def write_prescription(self, user_id: int, disease_id: int = None) -> list:
        def any_word_in_x_match_any_word_in_y(x: list, y: str):
            list1 = []
            list2 = [str(_).lower().strip() for _ in str(y).split(",")]
            for sentence in x:
                list1.extend([str(_).lower().strip() for _ in str(sentence).split(" ")])
            for word in list1:
                if word in list2:
                    return True
            return False
        
        def qna_prescription_filter(disease_question):
            a, b = [], []
            if disease_question.blocked_type:
                a = [
                        str(_).strip()
                        for _ in str(disease_question.blocked_type).split(
                            ","
                        )
                    ]
            if disease_question.prescribe:
                b = [
                        int(_)
                        for _ in str(disease_question.prescribe).split(",")
                    ]
            return a, b

        blocked_medicine_types = []
        disease_answes = self.get_instances(
            user_id, DiseaseAnswer, extra_filters={"disease_id": disease_id}
        )
        qna_prescription = []
        for disease_answer in disease_answes:
            disease_question = self.get_instances(
                None,
                DiseaseQuestion,
                extra_filters={"id": disease_answer.question_id},
                find_first=True,
            )
            if disease_question.value is None:
                continue
            if disease_question.filter == "<":
                try:
                    first_integer_in_answer = re.findall(r"\d+", disease_answer.detail)[
                        0
                    ]
                    if int(first_integer_in_answer) < int(disease_question.value):
                        a, b = qna_prescription_filter(disease_question)
                        blocked_medicine_types.extend(a)
                        qna_prescription.extend(b)
                except IndexError:
                    pass
            elif disease_question.filter == ">":
                try:
                    first_integer_in_answer = re.findall(r"\d+", disease_answer.detail)[
                        0
                    ]
                    if int(first_integer_in_answer) < int(disease_question.value):
                        a, b = qna_prescription_filter(disease_question)
                        blocked_medicine_types.extend(a)
                        qna_prescription.extend(b)
                except IndexError:
                    pass
            elif disease_question.filter == "yes":
                try:
                    is_yes = any_word_in_x_match_any_word_in_y(
                        ["yes"], disease_answer.detail
                    )
                    if is_yes:
                        a, b = qna_prescription_filter(disease_question)
                        blocked_medicine_types.extend(a)
                        qna_prescription.extend(b)
                except IndexError:
                    pass
        allowed_medicines = {}
        medicines = self.get_instances(
            None, Medicine, extra_filters={"disease_id": disease_id}
        )
        user = self.get_instances(user_id, User, find_first=True)
        try:
            age = int(user.age)
        except:
            age = 0
        gender = user.gender
        is_pregnant = user.is_pregnant
        medications = [
            str(medication.detail).lower()
            for medication in self.get_instances(user_id, Medication)
        ]
        conditions = [
            str(condition.detail).lower()
            for condition in self.get_instances(user_id, MedicalCondition)
        ]
        allergies = [
            str(allergy.detail).lower()
            for allergy in self.get_instances(user_id, Allergy)
        ]
        surgeries = [
            str(surgery.detail).lower()
            for surgery in self.get_instances(user_id, Surgery)
        ]
        for medicine in medicines:
            if medicine.type not in allowed_medicines:
                allowed_medicines[medicine.type] = None
            if (
                (age < medicine.min_age or age > medicine.max_age)
                or (
                    str(gender).lower().strip()
                    not in [
                        str(gend).lower().strip()
                        for gend in str(medicine.allowed_gender).split(",")
                    ]
                )
                or (is_pregnant and not medicine.allowed_for_pregnant)
                or (
                    any_word_in_x_match_any_word_in_y(
                        allergies, medicine.not_for_allergies
                    )
                )
                or (
                    any_word_in_x_match_any_word_in_y(
                        conditions, medicine.not_for_conditions
                    )
                )
                or (
                    any_word_in_x_match_any_word_in_y(
                        surgeries, medicine.not_for_surgeries
                    )
                )
                or (
                    any_word_in_x_match_any_word_in_y(
                        medications, medicine.not_for_medications
                    )
                )
                or (
                    allowed_medicines[medicine.type] is not None
                    and medicine.id not in qna_prescription
                )
                or medicine.type in blocked_medicine_types
            ):
                continue
            if allowed_medicines[medicine.type] is not None:
                allowed_medicines[f"{medicine.type}_{medicine.id}"] = medicine.detail
            else:
                allowed_medicines[medicine.type] = medicine.detail
        return "\n".join(
            [value for value in allowed_medicines.values() if value is not None]
        )
