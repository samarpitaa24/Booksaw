# --- data/pune_map_data.py ---

pune_map = {
    "Warje": {"Kothrud": 4, "Shivane": 2},
    "Kothrud": {"Warje": 4, "Deccan Gymkhana": 6, "Karve Nagar": 3},
    "Deccan Gymkhana": {"Kothrud": 6, "FC Road": 2, "JM Road": 2},
    "FC Road": {"Deccan Gymkhana": 2, "Shivajinagar": 1},
    "JM Road": {"Deccan Gymkhana": 2, "Shivajinagar": 1},
    "Shivajinagar": {"FC Road": 1, "JM Road": 1, "Karve Nagar": 5},
    "Shivane": {"Warje": 2, "Malwadi": 1},
    "Malwadi": {"Shivane": 1, "Uttam Nagar": 1},
    "Uttam Nagar": {"Malwadi": 1},
    "Karve Nagar": {"Kothrud": 3, "Shivajinagar": 5},
}


heuristic = {
    "Warje": 8,
    "Kothrud": 6,
    "Deccan Gymkhana": 4,
    "FC Road": 0,
    "JM Road": 1,
    "Shivajinagar": 2,
    "Shivane": 9,
    "Malwadi": 8,
    "Uttam Nagar": 9,
    "Karve Nagar": 5,
}
heuristic = {
    "Warje": 8,
    "Kothrud": 6,
    "Deccan Gymkhana": 4,
    "FC Road": 0,
    "JM Road": 1,
    "Shivajinagar": 2,
    "Shivane": 9,
    "Malwadi": 8,
    "Uttam Nagar": 9,
    "Karve Nagar": 5,
}
