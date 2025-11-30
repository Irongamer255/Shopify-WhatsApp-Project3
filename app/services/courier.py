import random
import string

class CourierService:
    def generate_tracking(self, courier_name="DHL"):
        # Mock tracking generation
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        tracking_url = f"https://track.example.com/{courier_name.lower()}/{tracking_number}"
        return tracking_number, tracking_url

courier_service = CourierService()
