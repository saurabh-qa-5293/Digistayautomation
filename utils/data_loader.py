import json
from pathlib import Path


class DataLoader:
    ROOT_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = ROOT_DIR / "data" / "checkin"
    TEST_DATA_DIR = ROOT_DIR / "test_data"

    @classmethod
    def load_json(cls, file_name):
        file_path = cls.DATA_DIR / file_name
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def get_test_case_data(cls, test_case_id):
        mapping = cls.load_json("room_view_checkin_data.json")

        guest_key = mapping[test_case_id]["guest_key"]

        if test_case_id.startswith("TC_CHECKIN_RV_ERR"):
            guest_data_file = "invalid_guest_data.json"
        else:
            guest_data_file = "guest_data.json"

        guest_data = cls.load_json(guest_data_file)[guest_key]

        document_relative_path = guest_data["document_file"]
        document_full_path = cls.TEST_DATA_DIR / document_relative_path

        guest_data["document_full_path"] = str(document_full_path)

        return guest_data