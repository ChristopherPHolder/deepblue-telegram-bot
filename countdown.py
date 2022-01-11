class Countdown:
    def __init__(self, countdown):
        self.id = countdown['countdown_id']
        self.owner_id = countdown['countdown_owner_id']
        self.name = countdown['countdown_name']
        self.date = countdown['countdown_date']
        self.start_img = countdown['countdown_start_img']
        self.start_cap = countdown['countdown_start_cap']
        self.end_img = countdown['countdown_end_img']
        self.end_cap = countdown['countdown_end_cap']
        self.state = countdown['state']
        return self

    def update_name(self, countdown_name):
        self.name = countdown_name
        return self
    
    def update_date(self, countdown_date):
        self.date = countdown_date
        # Verify date is date
        # Verify date in future
        return self

    def update_start_img(self, start_img):
        self.start_img = start_img
        return self
    
    def update_start_cap(self, start_cap):
        self.start_cap = start_cap
        return self

    def update_end_img(self, end_img):
        self.end_img = end_img
        return self

    def update_end_cap(self, end_cap):
        self.end_cap = end_cap
        return self

    def update_state(self, state):
        self.state = state
        return self

    def is_active(self):
        if self.state == 'active':
            return True
        else: return False

    def is_future_date(self):
        # Check if date in future
        pass