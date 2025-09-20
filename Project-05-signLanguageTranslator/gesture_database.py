# Static Gestures
STATIC_GESTURES = {
    "HELLO": {"hand_shape": "B", "location": "forehead", "movement": "salute"},
    "THANK YOU": {"hand_shape": "flat", "location": "chin", "movement": "forward"},
    "YES": {"hand_shape": "S", "movement": "nod"},
    "NO": {"hand_shape": "index_side", "movement": "side_to_side"}
}

# Motion-Based Gestures
MOTION_GESTURES = {
    "I LOVE YOU": {
        "sequence": [
            {"hand_shape": "ILY", "duration": 0.3},
            {"movement": "forward", "speed": "medium"}
        ]
    },
    "PLEASE": {
        "sequence": [
            {"hand_shape": "flat", "location": "chest"},
            {"movement": "circular", "repetitions": 3}
        ]
    }
}

# Combined Dictionary
GESTURE_LIBRARY = {**STATIC_GESTURES, **MOTION_GESTURES}