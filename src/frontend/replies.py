def not_registered(name: str) -> str:
    return f"Hey {name}, looks like you're not registered in Ah Gong's database 😰\n\nPlease ask the admins to register your telegram handle first!"

def not_admin(name: str) -> str:
    return f"Hey {name}, this feature is unfortunately unavailable to you because you're not an admin 😬"

def error() -> str:
    return "Oops, ah gong seems to have run into a problem 🤧, please notify the devs if this persists..."