import time

def format_image_url(image_path, host_url="https://erpnext.hodanhospital.com", cache_bust=True):
    """
    Formats an image path into a full URL.
    Returns None if input is None/empty.
    """
    if not image_path:
        return None
    
    # Ensure path starts with '/files/'
    if not image_path.startswith('/files/'):
        image_path = f"/files/{image_path}"
    
    full_url = f"{host_url}{image_path}"
    
    # Add cache-busting
    if cache_bust:
        full_url += f"?v={int(time.time())}"
    
    return full_url