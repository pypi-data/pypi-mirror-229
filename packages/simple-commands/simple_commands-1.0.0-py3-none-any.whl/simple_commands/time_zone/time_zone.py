import datetime
import pytz

class Time_zone:
    def __init__(self, timezone_name):
        self.timezone = pytz.timezone(timezone_name)
    
    def get_current_time(self):
        current_time = datetime.datetime.now(self.timezone)
        return current_time
    
    def convert_time(self, source_time, target_timezone_name):
        # ตรวจสอบว่า source_time มี timezone หรือไม่
        if source_time.tzinfo is None:
            raise ValueError("source_time must have a timezone")

        target_timezone = pytz.timezone(target_timezone_name)
        target_time = source_time.astimezone(target_timezone)
        return target_time
    
    def add_hours(self, source_time, hours):
        # เพิ่มเวลาในรูปแบบชั่วโมง
        return source_time + datetime.timedelta(hours=hours)
    
    def subtract_hours(self, source_time, hours):
        # ลดเวลาในรูปแบบชั่วโมง
        return source_time - datetime.timedelta(hours=hours)
    
    def add_minutes(self, source_time, minutes):
        # เพิ่มเวลาในรูปแบบนาที
        return source_time + datetime.timedelta(minutes=minutes)
    
    def subtract_minutes(self, source_time, minutes):
        # ลดเวลาในรูปแบบนาที
        return source_time - datetime.timedelta(minutes=minutes)
    
    def time_difference(self, time1, time2):
        # คำนวณระยะเวลาระหว่างเวลาที่1 และเวลาที่2
        difference = time1 - time2
        
        # คำนวณปี
        years = difference.days // 365
        remaining_days = difference.days % 365
        
        # คำนวณเดือน
        months = remaining_days // 30
        remaining_days = remaining_days % 30
        
        # คำนวณวัน
        days = remaining_days
        
        # คำนวณชั่วโมง
        hours, remainder = divmod(difference.seconds, 3600)
        
        # คำนวณนาที
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "years": years,
            "months": months,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        }

        def get_time_in_timezone(self, timezone_name):
            # ดึงเวลาใน timezone ที่ระบุโดยผู้ใช้
            target_timezone = pytz.timezone(timezone_name)
            current_time = datetime.datetime.now(target_timezone)
            return current_time