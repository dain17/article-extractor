from sites.fox import Fox
from sites.kango import Kango
from sites.yahoo import Yahoo


def create_domain_instance(domain, category = None):
    domain = domain
    domain_dict = {
        'yahoo': lambda: Yahoo(category=category),
        'kango': lambda: Kango(category=category),
        'fox': lambda: Fox(category=category)
    }

    return domain_dict[domain]()