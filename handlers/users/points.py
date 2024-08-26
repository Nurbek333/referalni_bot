# points.py

def calculate_referral_points(referral_level):
    if referral_level == 1:
        return 10  # 1-daraja uchun ball
    elif referral_level == 2:
        return 5  # 2-daraja uchun ball
    elif referral_level == 3:
        return 2  # 3-daraja uchun ball
    return 0

def add_referral_points(db, referrer_id, referral_level):
    points = calculate_referral_points(referral_level)
    db.update_user_points(referrer_id, points)
