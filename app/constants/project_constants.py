ALLOWED_STATUS_FLOW = {
    "pending": ["inprogress"],
    "inprogress": ["completed"],
    "completed": ["archived"],
    "archived": []
}