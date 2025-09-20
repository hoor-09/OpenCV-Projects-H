# Complete ASL Fingerspelling Mappings
LETTER_MAPPINGS = {
    # A-Z with detailed finger configurations
    "A": {"thumb_out": True, "other_fingers_closed": True},
    "B": {"index_up": True, "other_fingers_closed": True, "thumb_closed": True},
    "C": {"thumb_tip_to_index_tip": False, "hand_c_shape": True},
    "D": {"index_up": True, "middle_down": True, "thumb_out": True},
    "E": {"all_fingers_closed": True, "thumb_over_fingers": True},
    "F": {"thumb_index_circle": True, "other_fingers_up": True},
    "G": {"index_pointing": True, "thumb_out": True},
    "H": {"index_middle_up": True, "thumb_out": True},
    "I": {"pinky_up": True, "thumb_out": True},
    "J": {"pinky_up": True, "thumb_out": True, "movement": "j_swipe"},
    "K": {"index_middle_up": True, "thumb_between": True},
    "L": {"index_up": True, "thumb_out": True, "shape": "L"},
    "M": {"thumb_under_fingers": True, "fingers_bent": True},
    "N": {"thumb_under_fingers": True, "fingers_bent": True, "middle_over_index": True},
    "O": {"thumb_tip_to_index_tip": True},
    "P": {"index_down": True, "thumb_up": True, "shape": "P"},
    "Q": {"index_down": True, "thumb_up": True, "movement": "q_tilt"},
    "R": {"index_middle_crossed": True},
    "S": {"fist_closed": True, "thumb_over": True},
    "T": {"thumb_between_index_middle": True},
    "U": {"index_middle_up": True},
    "V": {"index_middle_up": True, "separated": True},
    "W": {"index_middle_ring_up": True},
    "X": {"index_bent": True},
    "Y": {"thumb_pinky_out": True},
    "Z": {"index_draws_z": True},
    " ": {"hand_open": True, "duration": 0.5}  # Space gesture
}

# Enhanced word dictionary with scoring system
WORD_DATABASE = {
    "HELLO": {"letters": ["H", "E", "L", "L", "O"], "score": 0},
    "THANK YOU": {"letters": ["T", "H", "A", "N", "K", " ", "Y", "O", "U"], "score": 0},
    "YES": {"letters": ["Y", "E", "S"], "score": 0},
    "NO": {"letters": ["N", "O"], "score": 0},
    "I LOVE YOU": {"letters": ["I", " ", "L", "O", "V", "E", " ", "Y", "O", "U"], "score": 0}
}

# Scoring thresholds
WORD_MATCH_THRESHOLD = 0.8  # 80% letter match